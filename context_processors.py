from . import firebase_mock

def category_processor(request):
    products = firebase_mock.get_all_products()
    
    # Extract unique categories from products (ensuring they have at least one product)
    unique_categories = []
    for p in products:
        cat = p.get('category')
        if cat and cat not in unique_categories:
            unique_categories.append(cat)
            
    # Sort them alphabetically or just return as is
    unique_categories.sort()
    
    return {
        'dynamic_categories': unique_categories
    }
