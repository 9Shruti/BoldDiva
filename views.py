from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from . import firebase_mock
import json
from datetime import datetime

def home(request):
    context = {
        'bestsellers': firebase_mock.get_bestsellers(),
        'trending': firebase_mock.get_trending()
    }
    return render(request, 'index.html', context)

def shop(request):
    category = request.GET.get('category')
    query = request.GET.get('q')
    shade = request.GET.get('shade')
    price = request.GET.get('price')
    products = firebase_mock.get_all_products()
    
    if category:
        products = [p for p in products if p.get('category') == category]
    if query:
        products = [p for p in products if query.lower() in p.get('name', '').lower() or query.lower() in p.get('description', '').lower()]
    
    if shade:
        products = [p for p in products if shade.lower() in p.get('name', '').lower() or shade.lower() in p.get('description', '').lower() or p.get('shade', '') == shade.lower()]
        
    if price:
        if price == 'under_1000':
            products = [p for p in products if float(p.get('price', 0)) < 1000]
        elif price == '1000_2000':
            products = [p for p in products if 1000 <= float(p.get('price', 0)) <= 2000]
        elif price == 'over_2000':
            products = [p for p in products if float(p.get('price', 0)) > 2000]
    
    current_category = category or (f"Search results for '{query}'" if query else 'All Products')
    if shade:
        current_category = f"{shade.title()} Shades"
    
    context = {
        'products': products,
        'current_category': current_category,
        'active_shade': shade,
        'active_price': price
    }
    return render(request, 'shop.html', context)

def product_detail(request, product_id):
    product = firebase_mock.get_product(product_id)
    if not product:
        # For simplicity, returning 404 naturally via django
        from django.http import Http404
        raise Http404("Product not found")
        
    context = {
        'product': product,
        'bestsellers': firebase_mock.get_bestsellers()[:4] # 'You may also like'
    }
    return render(request, 'product.html', context)

def cart(request):
    return render(request, 'cart.html')

def checkout(request):
    return render(request, 'checkout.html')

def blogs(request):
    return render(request, 'blogs.html')

def login_view(request):
    error = None
    if request.method == 'POST':
        e = request.POST.get('email')
        p = request.POST.get('password')
        
        user_obj = User.objects.filter(email=e).first()
        username_to_auth = user_obj.username if user_obj else e
        
        user = authenticate(request, username=username_to_auth, password=p)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = "Invalid email or password"
    return render(request, 'login.html', {'error': error})

def signup_view(request):
    error = None
    if request.method == 'POST':
        e = request.POST.get('email')
        p1 = request.POST.get('password')
        p2 = request.POST.get('password_confirm')
        
        if User.objects.filter(username=e).exists():
            error = "An account with this email already exists."
        elif len(p1) < 6:
            error = "Password must be at least 6 characters."
        elif p1 != p2:
            error = "Passwords do not match."
        else:
            user = User.objects.create_user(username=e, email=e, password=p1)
            login(request, user)
            return redirect('home')
            
    return render(request, 'signup.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def customer_dashboard_view(request):
    if request.user.is_superuser:
        return redirect('dashboard')
    orders = firebase_mock.get_orders_by_email(request.user.email)
    profile = firebase_mock.get_user_profile(request.user.email)
    context = {
        'orders': orders,
        'total_orders': len(orders),
        'total_spent': sum([o.get('total', 0) for o in orders]),
        'profile': profile,
        'addresses': profile.get('addresses', []),
    }
    return render(request, 'my_account.html', context)

@login_required
def dashboard_view(request):
    if not request.user.is_superuser:
        return redirect('home')
    orders = firebase_mock.get_recent_orders()
    # Build customer list from Django auth users (non-admin)
    from django.contrib.auth.models import User as AuthUser
    django_users = AuthUser.objects.filter(is_superuser=False).order_by('-date_joined')
    customers = []
    for u in django_users:
        user_orders = [o for o in orders if o.get('email') == u.email]
        customers.append({
            'id': str(u.id),
            'name': u.email.split('@')[0].title(),
            'email': u.email,
            'total_orders': len(user_orders),
            'date_joined': u.date_joined.strftime('%d %b %Y'),
        })
    context = {
        'products': firebase_mock.get_all_products(),
        'orders': orders,
        'customers': customers,
        'reviews': firebase_mock.get_reviews(),
        'offers': firebase_mock.get_offers(),
        'total_revenue': sum([o.get('total', 0) for o in orders])
    }
    return render(request, 'dashboard.html', context)

@csrf_exempt
@login_required
def api_add_product(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_data = {
                'name': data.get('name', ''),
                'description': data.get('description', ''),
                'price': float(data.get('price', 0)),
                'category': data.get('category', ''),
                'shade': data.get('shade', ''),
                'image_url': data.get('image_url', ''),
                'is_bestseller': False,
                'is_trending': False,
            }
            doc_id = firebase_mock.add_product(product_data)
            if doc_id:
                return JsonResponse({'status': 'success', 'id': doc_id})
            else:
                return JsonResponse({'status': 'error', 'message': 'Failed to save product'}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

@csrf_exempt
def api_place_order(request):
    if request.method == 'POST':
        if request.user.is_authenticated and request.user.is_superuser:
            return JsonResponse({'status': 'error', 'message': 'Admins cannot place orders.'}, status=403)
            
        try:
            data = json.loads(request.body)
            
            # Build product names string from cart
            cart_items = data.get('cart', [])
            product_names = ', '.join([item.get('name', 'Unknown') for item in cart_items])
            
            order_data = {
                'customer': data.get('firstName', '') + ' ' + data.get('lastName', ''),
                'email': request.user.email if request.user.is_authenticated else data.get('email', ''),
                'phone': data.get('phone', ''),
                'address': data.get('address', ''),
                'product_name': product_names,
                'items': len(cart_items),
                'cart_details': cart_items,
                'payment_method': data.get('payment_method', 'Cash on Delivery'),
                'payment_detail': data.get('payment_detail', ''),
                'total': float(data.get('total', 0)),
                'status': 'Processing',
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            doc_id = firebase_mock.add_order(order_data)
            if doc_id:
                return JsonResponse({'status': 'success', 'order_id': doc_id})
            else:
                return JsonResponse({'status': 'error', 'message': 'Failed to save order'}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)


@csrf_exempt
@login_required
def api_delete_record(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            collection = data.get('collection')
            doc_id = data.get('id')
            
            if not collection or not doc_id:
                return JsonResponse({'status': 'error', 'message': 'Missing collection or id'}, status=400)
                
            # If the frontend passes 'categories' but they aren't in firebase, we just mock success
            if collection == 'categories':
                return JsonResponse({'status': 'success'})
                
            success = firebase_mock.delete_document(collection, doc_id)
            if success:
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Failed to delete from database'}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

@csrf_exempt
@login_required
def api_delete_user(request):
    if not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Admin only'}, status=403)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            if not user_id:
                return JsonResponse({'status': 'error', 'message': 'Missing user_id'}, status=400)
            from django.contrib.auth.models import User as AuthUser
            target = AuthUser.objects.filter(id=user_id, is_superuser=False).first()
            if not target:
                return JsonResponse({'status': 'error', 'message': 'User not found or cannot delete admin'}, status=404)
            target.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

@csrf_exempt
@login_required
def api_update_order_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            new_status = data.get('status')
            if not order_id or not new_status:
                return JsonResponse({'status': 'error', 'message': 'Missing order_id or status'}, status=400)
            success = firebase_mock.update_document('orders', order_id, {'status': new_status})
            if success:
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'Failed to update'}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

@csrf_exempt
@login_required
def api_save_profile(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profile_data = {
                'name': data.get('name', ''),
                'phone': data.get('phone', ''),
            }
            success = firebase_mock.save_user_profile(request.user.email, profile_data)
            if success:
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'Failed to save'}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

@csrf_exempt
@login_required
def api_save_address(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action', 'add')
            profile = firebase_mock.get_user_profile(request.user.email)
            addresses = profile.get('addresses', [])

            if action == 'add':
                new_addr = {
                    'label': data.get('label', 'Home'),
                    'name': data.get('name', ''),
                    'phone': data.get('phone', ''),
                    'address': data.get('address', ''),
                    'city': data.get('city', ''),
                    'state': data.get('state', ''),
                    'pincode': data.get('pincode', ''),
                    'is_default': len(addresses) == 0
                }
                addresses.append(new_addr)
            elif action == 'delete':
                idx = int(data.get('index', -1))
                if 0 <= idx < len(addresses):
                    addresses.pop(idx)
            elif action == 'set_default':
                idx = int(data.get('index', -1))
                for i, a in enumerate(addresses):
                    a['is_default'] = (i == idx)

            firebase_mock.save_user_profile(request.user.email, {'addresses': addresses})
            return JsonResponse({'status': 'success', 'addresses': addresses})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

@csrf_exempt
@login_required
def api_get_addresses(request):
    profile = firebase_mock.get_user_profile(request.user.email)
    return JsonResponse({'status': 'success', 'addresses': profile.get('addresses', []), 'profile': {'name': profile.get('name', ''), 'phone': profile.get('phone', '')}})

