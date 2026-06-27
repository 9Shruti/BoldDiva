from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('my-account/', views.customer_dashboard_view, name='my_account'),
    path('api/add_product/', views.api_add_product, name='api_add_product'),
    path('api/place_order/', views.api_place_order, name='api_place_order'),
    path('api/delete_record/', views.api_delete_record, name='api_delete_record'),
    path('api/delete_user/', views.api_delete_user, name='api_delete_user'),
    path('api/update_order_status/', views.api_update_order_status, name='api_update_order_status'),
    path('api/save_profile/', views.api_save_profile, name='api_save_profile'),
    path('api/save_address/', views.api_save_address, name='api_save_address'),
    path('api/get_addresses/', views.api_get_addresses, name='api_get_addresses'),
    path('blogs/', views.blogs, name='blogs'),
]
