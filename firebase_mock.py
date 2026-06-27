import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase (Make sure `serviceAccountKey.json` is in your project root)
key_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'serviceAccountKey.json')

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase initialization error: {e}")

db = firestore.client()

def fetch_collection(collection_name):
    """Helper function to fetch all documents from a Firestore collection."""
    try:
        docs = db.collection(collection_name).stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            results.append(data)
        return results
    except Exception as e:
        print(f"Error fetching {collection_name}: {e}")
        return []

def get_all_products():
    return fetch_collection('products')

def get_product(product_id):
    try:
        doc = db.collection('products').document(product_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
    except Exception as e:
        print(e)
    return None

def get_bestsellers():
    # Advanced query requiring an index in Firebase, or just filter in memory for simplicity
    products = fetch_collection('products')
    return [p for p in products if p.get('is_bestseller', False)]

def get_trending():
    products = fetch_collection('products')
    return [p for p in products if p.get('is_trending', False)]

def get_recent_orders():
    return fetch_collection('orders')

def get_orders_by_email(email):
    """Fetch orders for a specific customer email."""
    try:
        docs = db.collection('orders').where('email', '==', email).stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            results.append(data)
        return results
    except Exception as e:
        print(f"Error fetching orders for {email}: {e}")
        return []

def get_customers():
    return fetch_collection('users')

def get_reviews():
    return fetch_collection('reviews')

def get_offers():
    return fetch_collection('offers')

def add_product(data):
    """Add a new product to Firestore and return the document ID."""
    try:
        doc_ref = db.collection('products').document()
        doc_ref.set(data)
        return doc_ref.id
    except Exception as e:
        print(f"Error adding product: {e}")
        return None

def add_order(order_data):
    try:
        doc_ref = db.collection('orders').document()
        doc_ref.set(order_data)
        return doc_ref.id
    except Exception as e:
        print(f"Error adding order: {e}")
        return None

def delete_document(collection_name, document_id):
    """Delete a document from a specified Firestore collection."""
    try:
        db.collection(collection_name).document(document_id).delete()
        return True
    except Exception as e:
        print(f"Error deleting document from {collection_name}: {e}")
        return False

def update_document(collection_name, document_id, data):
    """Update fields in a Firestore document."""
    try:
        db.collection(collection_name).document(document_id).update(data)
        return True
    except Exception as e:
        print(f"Error updating {collection_name}/{document_id}: {e}")
        return False

def get_user_profile(email):
    """Get or create a user profile document keyed by email."""
    try:
        doc = db.collection('user_profiles').document(email).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return {'id': email, 'name': '', 'phone': '', 'addresses': []}
    except Exception as e:
        print(f"Error fetching profile for {email}: {e}")
        return {'id': email, 'name': '', 'phone': '', 'addresses': []}

def save_user_profile(email, data):
    """Save/update user profile."""
    try:
        db.collection('user_profiles').document(email).set(data, merge=True)
        return True
    except Exception as e:
        print(f"Error saving profile for {email}: {e}")
        return False

