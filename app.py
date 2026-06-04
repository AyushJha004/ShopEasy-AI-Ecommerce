from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import services
from services.search_service import SearchService
from services.recommendation_service import RecommendationService
from services.comparison_service import ComparisonService
from services.review_service import ReviewService

app = Flask(__name__)

# MongoDB Connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DB = os.getenv('MONGODB_DB', 'ecommerce')

try:
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    products_collection = db['products']
    orders_collection = db['orders']
    baskets_collection = db['baskets']
    users_collection = db['users']
    reviews_collection = db['reviews']

    # Create indexes for better performance
    products_collection.create_index('category')
    products_collection.create_index('price')
    products_collection.create_index('brand')
    products_collection.create_index([('name', 'text'), ('description', 'text')])
    
    reviews_collection.create_index('product_id')
    reviews_collection.create_index('user_id')
    reviews_collection.create_index('created_at')

    print("Connected to MongoDB")
except Exception as e:
    print(f"MongoDB connection failed: {e}")

# Initialize services
search_service = SearchService(products_collection)
recommendation_service = RecommendationService(products_collection, orders_collection, users_collection)
comparison_service = ComparisonService(products_collection)
review_service = ReviewService(reviews_collection, products_collection)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/cart/<user_id>')
def cart_page(user_id):
    return render_template('cart.html', user_id=user_id)

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/seed')
def seed_page():
    return render_template('seed.html')

@app.route('/product/<product_id>')
def product_details_page(product_id):
    return render_template('product_details.html', product_id=product_id)

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product_details(product_id):
    try:
        if not ObjectId.is_valid(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        product = products_collection.find_one({'_id': ObjectId(product_id)})
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        product['_id'] = str(product['_id'])
        return jsonify(product)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        products = list(products_collection.find())
        for product in products:
            product['_id'] = str(product['_id'])
        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def add_product():
    try:
        data = request.json
        product = {
            'name': data.get('name'),
            'price': float(data.get('price')),
            'description': data.get('description'),
            'stock': int(data.get('stock', 0)),
            'image': data.get('image', '/placeholder.svg?height=300&width=300'),
            'created_at': datetime.utcnow()
        }
        result = products_collection.insert_one(product)
        product['_id'] = str(result.inserted_id)
        return jsonify(product), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        items = data.get('items', [])
        
        # Calculate total and validate stock using numpy
        prices = np.array([item['price'] for item in items])
        quantities = np.array([item['quantity'] for item in items])
        total = float(np.sum(prices * quantities))
        
        # Update product stock
        for item in items:
            products_collection.update_one(
                {'_id': ObjectId(item['product_id'])},
                {'$inc': {'stock': -item['quantity']}}
            )
        
        order = {
            'items': items,
            'total': total,
            'status': 'pending',
            'created_at': datetime.utcnow()
        }
        result = orders_collection.insert_one(order)
        return jsonify({'order_id': str(result.inserted_id), 'total': total}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/basket/<user_id>', methods=['GET'])
def get_basket(user_id):
    try:
        basket = baskets_collection.find_one({'user_id': user_id})
        if not basket:
            return jsonify({'items': [], 'total': 0})
        
        # Get product details for each item
        items_with_details = []
        total = 0
        for item in basket.get('items', []):
            product = products_collection.find_one({'_id': ObjectId(item['product_id'])})
            if product:
                item_total = item['quantity'] * product['price']
                items_with_details.append({
                    'product_id': str(product['_id']),
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': item['quantity'],
                    'item_total': item_total
                })
                total += item_total
        
        return jsonify({'items': items_with_details, 'total': total})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/basket/<user_id>/add', methods=['POST'])
def add_to_basket(user_id):
    try:
        data = request.json
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        # Check if product exists and has enough stock
        product = products_collection.find_one({'_id': ObjectId(product_id)})
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        if product['stock'] < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        # Update or create basket
        basket = baskets_collection.find_one({'user_id': user_id})
        if basket:
            # Check if item already in basket
            item_found = False
            for item in basket['items']:
                if item['product_id'] == product_id:
                    item['quantity'] += quantity
                    item_found = True
                    break
            if not item_found:
                basket['items'].append({'product_id': product_id, 'quantity': quantity})
            
            baskets_collection.update_one(
                {'user_id': user_id},
                {'$set': {'items': basket['items'], 'updated_at': datetime.utcnow()}}
            )
        else:
            baskets_collection.insert_one({
                'user_id': user_id,
                'items': [{'product_id': product_id, 'quantity': quantity}],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
        
        return jsonify({'message': 'Item added to basket'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/basket/<user_id>/remove', methods=['POST'])
def remove_from_basket(user_id):
    try:
        data = request.json
        product_id = data.get('product_id')
        basket = baskets_collection.find_one({'user_id': user_id})
        if not basket:
            return jsonify({'error': 'Basket not found'}), 404
        remaining = [item for item in basket['items'] if item['product_id'] != product_id]
        baskets_collection.update_one(
            {'user_id': user_id},
            {'$set': {'items': remaining, 'updated_at': datetime.utcnow()}}
        )
        return jsonify({'message': 'Item removed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/basket/<user_id>/item', methods=['DELETE'])
def delete_basket_item(user_id):
    try:
        data = request.json
        product_id = data.get('product_id')
        basket = baskets_collection.find_one({'user_id': user_id})
        if not basket:
            return jsonify({'error': 'Basket not found'}), 404
        remaining = [item for item in basket['items'] if item['product_id'] != product_id]
        baskets_collection.update_one(
            {'user_id': user_id},
            {'$set': {'items': remaining, 'updated_at': datetime.utcnow()}}
        )
        return jsonify({'message': 'Item deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/basket/<user_id>/clear', methods=['DELETE'])
def clear_basket(user_id):
    try:
        baskets_collection.delete_one({'user_id': user_id})
        return jsonify({'message': 'Basket cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/basket/<user_id>/purchase', methods=['POST'])
def purchase_selected_items(user_id):
    try:
        data = request.json
        selected_items = data.get('selected_items', [])
        address = data.get('address', {})
        payment_method = data.get('payment_method', '')
        
        if not selected_items:
            return jsonify({'error': 'No items selected'}), 400
        if not address or not payment_method:
            return jsonify({'error': 'Address and payment method required'}), 400
        
        # Get basket
        basket = baskets_collection.find_one({'user_id': user_id})
        if not basket:
            return jsonify({'error': 'Basket not found'}), 404
        
        # Prepare order items and calculate total
        order_items = []
        total = 0
        
        for selected_item in selected_items:
            product_id = selected_item['product_id']
            quantity = selected_item['quantity']
            
            # Get product details
            product = products_collection.find_one({'_id': ObjectId(product_id)})
            if not product:
                return jsonify({'error': f'Product {product_id} not found'}), 404
            if product['stock'] < quantity:
                return jsonify({'error': f'Insufficient stock for {product["name"]}'}), 400
            
            item_total = product['price'] * quantity
            order_items.append({
                'product_id': product_id,
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity
            })
            total += item_total
        
        # Update product stock
        for item in order_items:
            products_collection.update_one(
                {'_id': ObjectId(item['product_id'])},
                {'$inc': {'stock': -item['quantity']}}
            )
        
        # Get buyer info
        buyer = users_collection.find_one({'_id': ObjectId(user_id)})
        buyer_info = {
            'user_id': user_id,
            'name': f"{buyer['firstName']} {buyer['lastName']}" if buyer else 'Unknown',
            'email': buyer['email'] if buyer else 'Unknown',
            'phone': buyer.get('phone', 'Not provided') if buyer else 'Unknown'
        }
        
        # Create order
        order = {
            'buyer_info': buyer_info,
            'items': order_items,
            'total': total,
            'address': address,
            'payment_method': payment_method,
            'status': 'pending',
            'created_at': datetime.utcnow()
        }
        result = orders_collection.insert_one(order)
        
        # Remove purchased items from basket
        remaining_items = []
        for basket_item in basket['items']:
            purchased = False
            for selected_item in selected_items:
                if basket_item['product_id'] == selected_item['product_id']:
                    if basket_item['quantity'] > selected_item['quantity']:
                        basket_item['quantity'] -= selected_item['quantity']
                        remaining_items.append(basket_item)
                    purchased = True
                    break
            if not purchased:
                remaining_items.append(basket_item)
        
        if remaining_items:
            baskets_collection.update_one(
                {'user_id': user_id},
                {'$set': {'items': remaining_items, 'updated_at': datetime.utcnow()}}
            )
        else:
            baskets_collection.delete_one({'user_id': user_id})
        
        return jsonify({
            'order_id': str(result.inserted_id),
            'total': total,
            'message': 'Order placed successfully'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        email = data.get('email')
        
        # Check if user already exists
        if users_collection.find_one({'email': email}):
            return jsonify({'error': 'Email already registered'}), 400
        
        user = {
            'firstName': data.get('firstName'),
            'lastName': data.get('lastName'),
            'email': email,
            'phone': data.get('phone'),
            'password': data.get('password'),  # In production, hash this!
            'created_at': datetime.utcnow()
        }
        
        result = users_collection.insert_one(user)
        return jsonify({
            'message': 'Account created successfully',
            'user_id': str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        user = users_collection.find_one({'email': email, 'password': password})
        if user:
            return jsonify({
                'message': 'Login successful',
                'user_id': str(user['_id']),
                'name': f"{user['firstName']} {user['lastName']}"
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        products = list(products_collection.find())
        prices = np.array([p['price'] for p in products])
        stocks = np.array([p['stock'] for p in products])
        
        stats = {
            'total_products': len(products),
            'avg_price': float(np.mean(prices)) if len(prices) > 0 else 0,
            'total_stock': int(np.sum(stocks)),
            'price_range': {
                'min': float(np.min(prices)) if len(prices) > 0 else 0,
                'max': float(np.max(prices)) if len(prices) > 0 else 0
            }
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== NEW AI-POWERED ENDPOINTS =====

@app.route('/api/search/natural', methods=['GET'])
def natural_language_search():
    """Search products using natural language query"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        logger.info(f"Natural language search: {query}")
        results = search_service.natural_language_search(query)
        
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        logger.error(f"Error in natural search: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommendations/<user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get personalized product recommendations for user"""
    try:
        if not ObjectId.is_valid(user_id):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        limit = request.args.get('limit', 5, type=int)
        if limit > 20:
            limit = 20
        
        logger.info(f"Getting recommendations for user: {user_id}")
        recommendations = recommendation_service.get_recommendations(user_id, limit)
        
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def compare_products():
    """Compare multiple products"""
    try:
        data = request.json
        product_ids = data.get('product_ids', [])
        
        if not isinstance(product_ids, list) or len(product_ids) == 0:
            return jsonify({'error': 'product_ids array required'}), 400
        
        # Validate all IDs
        for product_id in product_ids:
            if not ObjectId.is_valid(product_id):
                return jsonify({'error': f'Invalid product ID: {product_id}'}), 400
        
        logger.info(f"Comparing {len(product_ids)} products")
        comparison = comparison_service.compare_products(product_ids)
        
        return jsonify(comparison)
    except Exception as e:
        logger.error(f"Error comparing products: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<product_id>/reviews', methods=['GET'])
def get_product_reviews(product_id):
    """Get reviews for a product"""
    try:
        if not ObjectId.is_valid(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        if limit > 100:
            limit = 100
        if page < 1:
            page = 1
        
        logger.info(f"Fetching reviews for product: {product_id}")
        result = review_service.get_product_reviews(product_id, limit, page)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error fetching reviews: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<product_id>/reviews', methods=['POST'])
def add_product_review(product_id):
    """Add a review for a product"""
    try:
        if not ObjectId.is_valid(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        
        data = request.json
        user_id = data.get('user_id')
        rating = data.get('rating')
        title = data.get('title', '')
        text = data.get('text', '')
        
        if not all([user_id, rating is not None, text]):
            return jsonify({'error': 'user_id, rating, and text required'}), 400
        
        if not (1 <= rating <= 5):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        if len(text) < 10:
            return jsonify({'error': 'Review text must be at least 10 characters'}), 400
        
        logger.info(f"Adding review for product: {product_id}")
        result = review_service.add_review(product_id, user_id, rating, title, text)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error adding review: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<product_id>/reviews/summary', methods=['GET'])
def get_review_summary(product_id):
    """Get AI-generated summary of reviews for a product"""
    try:
        if not ObjectId.is_valid(product_id):
            return jsonify({'error': 'Invalid product ID'}), 400
        
        logger.info(f"Getting review summary for product: {product_id}")
        summary = review_service.get_review_summary(product_id)
        
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Error getting review summary: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reviews/<review_id>/helpful', methods=['POST'])
def mark_review_helpful(review_id):
    """Mark a review as helpful"""
    try:
        if not ObjectId.is_valid(review_id):
            return jsonify({'error': 'Invalid review ID'}), 400
        
        logger.info(f"Marking review as helpful: {review_id}")
        success = review_service.mark_helpful(review_id)
        
        if success:
            return jsonify({'message': 'Review marked as helpful'})
        else:
            return jsonify({'error': 'Failed to mark review'}), 500
    except Exception as e:
        logger.error(f"Error marking review: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/seed', methods=['POST'])
def seed_products():
    """Seed sample products for all categories"""
    try:
        # Clear existing products
        products_collection.delete_many({})
        
        sample_products = [
            # Electronics
            {'name': 'Wireless Noise-Cancelling Headphones', 'category': 'electronics', 'price': 7499, 'stock': 50, 'description': 'Premium sound quality with active noise cancellation and 30-hour battery life. Perfect for music lovers and travelers.', 'brand': 'AudioTech', 'rating': 4.5, 'reviews_count': 128, 'colors': ['Black', 'Silver', 'Blue', 'Red'], 'image': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80'},
            {'name': 'Smartphone Pro 15', 'category': 'electronics', 'price': 58999, 'stock': 30, 'description': '6.7" AMOLED display, 200MP camera with AI enhancement, 5G ready. The ultimate smartphone experience.', 'brand': 'TechMobile', 'rating': 4.7, 'reviews_count': 342, 'colors': ['Midnight Black', 'Pearl White', 'Ocean Blue'], 'image': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&q=80'},
            {'name': '4K Ultra HD Smart TV 55"', 'category': 'electronics', 'price': 37999, 'stock': 20, 'description': 'Stunning 4K picture quality with HDR support and built-in streaming apps. Transform your living room.', 'brand': 'VisionMax', 'rating': 4.6, 'reviews_count': 89, 'colors': ['Black'], 'image': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=600&q=80'},
            {'name': 'Mechanical Gaming Keyboard', 'category': 'electronics', 'price': 6499, 'stock': 40, 'description': 'RGB backlit mechanical keyboard with tactile blue switches. Full-size layout with programmable keys.', 'brand': 'GameGear', 'rating': 4.4, 'reviews_count': 156, 'colors': ['Black', 'White', 'RGB'], 'image': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&q=80'},
            # Clothing
            {'name': 'Classic Denim Jacket', 'category': 'clothing', 'price': 2499, 'stock': 60, 'description': 'Timeless denim jacket in premium cotton. Slim fit design perfect for all seasons. True to size.', 'brand': 'DenimCo', 'rating': 4.3, 'reviews_count': 95, 'sizes': ['S', 'M', 'L', 'XL', 'XXL'], 'colors': ['Blue', 'Black', 'Light Blue'], 'image': 'https://images.unsplash.com/photo-1495105787522-5334e3ffa0ef?w=600&q=80'},
            {'name': 'Running Sneakers', 'category': 'clothing', 'price': 3999, 'stock': 45, 'description': 'Lightweight breathable mesh upper with cushioned midsole. Ideal for running and daily wear.', 'brand': 'SportFlex', 'rating': 4.5, 'reviews_count': 203, 'sizes': ['6', '7', '8', '9', '10', '11', '12'], 'colors': ['White', 'Black', 'Grey', 'Navy Blue'], 'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80'},
            {'name': 'Floral Summer Dress', 'category': 'clothing', 'price': 1999, 'stock': 55, 'description': 'Light cotton floral print dress, perfect for summer outings. Comfortable A-line fit with adjustable straps.', 'brand': 'FloraWear', 'rating': 4.6, 'reviews_count': 167, 'sizes': ['XS', 'S', 'M', 'L', 'XL'], 'colors': ['Floral Pink', 'Floral Blue', 'Floral Yellow'], 'image': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&q=80'},
            {'name': 'Wool Knit Sweater', 'category': 'clothing', 'price': 2999, 'stock': 35, 'description': 'Warm merino wool blend sweater. Relaxed fit with ribbed cuffs and hem. Perfect for winter.', 'brand': 'CozyKnit', 'rating': 4.7, 'reviews_count': 134, 'sizes': ['S', 'M', 'L', 'XL'], 'colors': ['Grey', 'Navy', 'Burgundy', 'Beige'], 'image': 'https://images.unsplash.com/photo-1576871337622-98d48d1cf531?w=600&q=80'},
            # Toys
            {'name': 'LEGO City Builder Set', 'category': 'toys', 'price': 3499, 'stock': 70, 'description': 'Build your dream city with 850 pieces! Includes buildings, vehicles, and mini-figures. Ages 7+.', 'brand': 'LEGO', 'rating': 4.8, 'reviews_count': 245, 'colors': ['Multicolor'], 'image': 'https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=600&q=80'},
            {'name': 'Remote Control Racing Car', 'category': 'toys', 'price': 2799, 'stock': 60, 'description': '2.4GHz RC car with 25 km/h top speed. Rechargeable battery, shock absorbers, all-terrain tires.', 'brand': 'SpeedRacer', 'rating': 4.4, 'reviews_count': 89, 'colors': ['Red', 'Blue', 'Green'], 'image': 'https://images.unsplash.com/photo-1581235720704-06d3acfcb36f?w=600&q=80'},
            {'name': 'Stuffed Teddy Bear', 'category': 'toys', 'price': 899, 'stock': 100, 'description': 'Super soft plush teddy bear, 45cm tall. Safe for all ages, machine washable. Perfect gift for kids.', 'brand': 'CuddleBear', 'rating': 4.9, 'reviews_count': 312, 'colors': ['Brown', 'White', 'Pink'], 'image': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&q=80'},
            {'name': 'Board Game: Strategy Quest', 'category': 'toys', 'price': 1799, 'stock': 40, 'description': 'Epic fantasy strategy board game for 2-6 players. Ages 8+. Includes game board, cards, and tokens.', 'brand': 'GameMaster', 'rating': 4.5, 'reviews_count': 78, 'colors': ['Multicolor'], 'image': 'https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?w=600&q=80'},
            # Art
            {'name': 'Abstract Canvas Painting', 'category': 'art', 'price': 8999, 'stock': 15, 'description': 'Hand-painted acrylic abstract art on 24x36" canvas. Ready to hang with hooks included. Adds elegance to any room.', 'brand': 'ArtStudio', 'rating': 4.6, 'reviews_count': 45, 'colors': ['Blue Abstract', 'Red Abstract', 'Multi-color'], 'image': 'https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=600&q=80'},
            {'name': 'Watercolor Landscape Print', 'category': 'art', 'price': 4999, 'stock': 25, 'description': 'Serene mountain lake watercolor scene in premium frame. UV-resistant glass protects colors.', 'brand': 'NatureArt', 'rating': 4.5, 'reviews_count': 67, 'colors': ['Natural'], 'image': 'https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=600&q=80'},
            {'name': 'Oil Painting Portrait', 'category': 'art', 'price': 15999, 'stock': 8, 'description': 'Classic style oil portrait on linen canvas. Museum-quality archival materials used. Limited collection.', 'brand': 'ClassicArt', 'rating': 4.8, 'reviews_count': 23, 'colors': ['Original'], 'image': 'https://images.unsplash.com/photo-1577083552431-6e5fd01988ec?w=600&q=80'},
            {'name': 'Acrylic Paint Set 24 Colors', 'category': 'art', 'price': 1499, 'stock': 80, 'description': 'Professional quality acrylic paints with vibrant pigments. 60ml tubes, includes color mixing guide.', 'brand': 'ArtSupply', 'rating': 4.7, 'reviews_count': 189, 'colors': ['Multicolor'], 'image': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&q=80'},
            # Food
            {'name': 'Organic Dark Chocolate Box', 'category': 'food', 'price': 799, 'stock': 120, 'description': '72% cacao dark chocolate. Ethically sourced cocoa beans. 24 individually wrapped pieces. Rich and smooth.', 'brand': 'ChocoDelux', 'rating': 4.8, 'reviews_count': 456, 'colors': ['Dark Brown'], 'image': 'https://images.unsplash.com/photo-1511381939415-e44015466834?w=600&q=80'},
            {'name': 'Premium Green Tea Collection', 'category': 'food', 'price': 999, 'stock': 90, 'description': 'Assorted Japanese green teas. 30 pyramid sachets with flavors like Sencha, Matcha, and Jasmine. Antioxidant-rich.', 'brand': 'ZenTea', 'rating': 4.6, 'reviews_count': 234, 'colors': ['Green'], 'image': 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=600&q=80'},
            {'name': 'Artisan Pasta Variety Pack', 'category': 'food', 'price': 649, 'stock': 110, 'description': 'Bronze-cut Italian pasta in 6 shapes. Made from durum wheat. Includes penne, fusilli, and spaghetti.', 'brand': 'PastaMia', 'rating': 4.5, 'reviews_count': 178, 'colors': ['Natural'], 'image': 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600&q=80'},
            {'name': 'Mixed Nuts & Dried Fruits', 'category': 'food', 'price': 549, 'stock': 85, 'description': 'Premium trail mix with almonds, cashews, raisins, and cranberries. 500g resealable pouch. High protein snack.', 'brand': 'NutriSnack', 'rating': 4.7, 'reviews_count': 267, 'colors': ['Mixed'], 'image': 'https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=600&q=80'},
            # Sports
            {'name': 'Professional Basketball', 'category': 'sports', 'price': 1999, 'stock': 55, 'description': 'Official size and weight basketball. Premium rubber with deep channel design. Indoor/outdoor use.', 'brand': 'ProSport', 'rating': 4.6, 'reviews_count': 145, 'colors': ['Orange', 'Black/Orange'], 'image': 'https://images.unsplash.com/photo-1519861531473-9200262188bf?w=600&q=80'},
            {'name': 'Yoga Mat Premium 6mm', 'category': 'sports', 'price': 1499, 'stock': 65, 'description': 'Non-slip 6mm thick yoga mat. Eco-friendly TPE material. Includes carrying strap. Perfect for yoga and Pilates.', 'brand': 'YogaLife', 'rating': 4.7, 'reviews_count': 298, 'colors': ['Purple', 'Blue', 'Pink', 'Black'], 'image': 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600&q=80'},
            {'name': 'Adjustable Dumbbell Set', 'category': 'sports', 'price': 8999, 'stock': 30, 'description': 'Adjustable dumbbells 5-25 kg per hand. Space-saving design replaces 15 dumbbells. Quick weight change mechanism.', 'brand': 'PowerFit', 'rating': 4.8, 'reviews_count': 167, 'colors': ['Black/Red', 'Black/Blue'], 'image': 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600&q=80'},
            {'name': 'Carbon Fiber Tennis Racket', 'category': 'sports', 'price': 4999, 'stock': 40, 'description': 'Lightweight carbon fiber racket. Pre-strung with synthetic gut. Ideal for intermediate to advanced players.', 'brand': 'TennisAce', 'rating': 4.5, 'reviews_count': 92, 'colors': ['Black/Yellow', 'Black/Red'], 'image': 'https://images.unsplash.com/photo-1622163642998-1ea32b0bbc67?w=600&q=80'},
            {'name': 'Badminton Racket Set', 'category': 'sports', 'price': 1299, 'stock': 55, 'description': 'Set of 2 aluminum badminton rackets with 3 shuttlecocks. Great for beginners and casual players.', 'brand': 'SmashPro', 'rating': 4.3, 'reviews_count': 74, 'colors': ['Blue/White', 'Red/Black'], 'image': 'https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=600&q=80'},
            {'name': 'Football (Size 5)', 'category': 'sports', 'price': 899, 'stock': 80, 'description': 'FIFA-approved size 5 football. Durable PU outer shell with air retention bladder.', 'brand': 'GoalKing', 'rating': 4.6, 'reviews_count': 210, 'colors': ['White/Black', 'Orange', 'White/Blue'], 'image': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=600&q=80'},
            {'name': 'Swimming Goggles', 'category': 'sports', 'price': 699, 'stock': 90, 'description': 'Anti-fog UV-protected silicone goggles. Adjustable strap, wide-view lens for competitive swimming.', 'brand': 'AquaVision', 'rating': 4.5, 'reviews_count': 132, 'colors': ['Blue', 'Black', 'Red'], 'image': 'https://images.unsplash.com/photo-1530549387789-4c1017266635?w=600&q=80'},
            # More Electronics
            {'name': 'True Wireless Earbuds', 'category': 'electronics', 'price': 2999, 'stock': 60, 'description': 'Active noise cancelling TWS earbuds. 6hr playback + 24hr case, IPX5 water-resistant, Bluetooth 5.3.', 'brand': 'SoundDrop', 'rating': 4.6, 'reviews_count': 445, 'colors': ['White', 'Black', 'Sage Green'], 'image': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&q=80'},
            {'name': 'Laptop Stand Adjustable', 'category': 'electronics', 'price': 1499, 'stock': 70, 'description': 'Aluminium ergonomic laptop stand. 6 height levels, foldable, fits 10-17 inch laptops.', 'brand': 'DeskMate', 'rating': 4.7, 'reviews_count': 289, 'colors': ['Silver', 'Space Grey'], 'image': 'https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=600&q=80'},
            {'name': 'Portable Power Bank 20000mAh', 'category': 'electronics', 'price': 1799, 'stock': 85, 'description': '20000mAh fast-charge power bank. 22.5W PD, dual USB-A + USB-C output. Charges phones 4-5 times.', 'brand': 'ChargePlus', 'rating': 4.8, 'reviews_count': 612, 'colors': ['Black', 'White', 'Blue'], 'image': 'https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=600&q=80'},
            # More Clothing
            {'name': 'Slim Fit Chino Pants', 'category': 'clothing', 'price': 1799, 'stock': 50, 'description': 'Stretch cotton slim-fit chinos. Versatile for office or casual. Machine washable.', 'brand': 'UrbanThread', 'sizes': ['28', '30', '32', '34', '36', '38'], 'rating': 4.4, 'reviews_count': 178, 'colors': ['Khaki', 'Navy', 'Olive', 'Black'], 'image': 'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600&q=80'},
            {'name': 'Graphic Print Hoodie', 'category': 'clothing', 'price': 1499, 'stock': 75, 'description': 'Fleece-lined pullover hoodie with bold graphic print. Kangaroo pocket, ribbed cuffs.', 'brand': 'StreetVibe', 'sizes': ['S', 'M', 'L', 'XL', 'XXL'], 'rating': 4.5, 'reviews_count': 236, 'colors': ['Black', 'Charcoal', 'White'], 'image': 'https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=600&q=80'},
            # Books
            {'name': 'Atomic Habits', 'category': 'books', 'price': 499, 'stock': 200, 'description': 'By James Clear. The #1 New York Times bestseller. Build good habits and break bad ones with proven strategies.', 'brand': 'Penguin Books', 'rating': 4.9, 'reviews_count': 3421, 'colors': ['Paperback', 'Hardcover'], 'image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&q=80'},
            {'name': 'The Psychology of Money', 'category': 'books', 'price': 399, 'stock': 180, 'description': 'By Morgan Housel. Timeless lessons on wealth, greed and happiness. A must-read for financial literacy.', 'brand': 'Jaico Publishing', 'rating': 4.8, 'reviews_count': 2876, 'colors': ['Paperback'], 'image': 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=600&q=80'},
            {'name': 'Rich Dad Poor Dad', 'category': 'books', 'price': 349, 'stock': 220, 'description': 'By Robert Kiyosaki. What the rich teach their kids about money that the poor and middle class do not.', 'brand': 'Plata Publishing', 'rating': 4.7, 'reviews_count': 5642, 'colors': ['Paperback', 'Hardcover'], 'image': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600&q=80'},
            {'name': 'Harry Potter Set (1-7)', 'category': 'books', 'price': 2999, 'stock': 60, 'description': 'Complete set of all 7 Harry Potter books by J.K. Rowling. Paperback box set edition.', 'brand': 'Bloomsbury', 'rating': 4.9, 'reviews_count': 8901, 'colors': ['Paperback Box Set'], 'image': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=600&q=80'},
            # Beauty
            {'name': 'Vitamin C Face Serum', 'category': 'beauty', 'price': 699, 'stock': 120, 'description': '20% Vitamin C + Hyaluronic Acid serum. Brightens skin, reduces dark spots. Dermatologist tested.', 'brand': 'GlowLab', 'rating': 4.6, 'reviews_count': 1243, 'colors': ['30ml', '60ml'], 'image': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&q=80'},
            {'name': 'Matte Lipstick Collection', 'category': 'beauty', 'price': 599, 'stock': 150, 'description': 'Long-lasting 16hr matte formula. Hydrating, non-drying, rich pigmented finish. Cruelty-free.', 'brand': 'ColorBliss', 'rating': 4.5, 'reviews_count': 876, 'colors': ['Red Runway', 'Rose Nude', 'Berry Crush', 'Coral Glow', 'Deep Plum'], 'image': 'https://images.unsplash.com/photo-1586495777744-4e6232bf2b18?w=600&q=80'},
            {'name': 'Hair Care Gift Set', 'category': 'beauty', 'price': 1299, 'stock': 80, 'description': 'Includes shampoo, conditioner, hair mask and serum. Sulphate-free, argan oil enriched formula.', 'brand': 'SilkStrands', 'rating': 4.7, 'reviews_count': 567, 'colors': ['Normal Hair', 'Dry Hair', 'Oily Hair'], 'image': 'https://images.unsplash.com/photo-1585232351009-aa87c56e5271?w=600&q=80'},
            {'name': 'Men\'s Grooming Kit', 'category': 'beauty', 'price': 999, 'stock': 95, 'description': 'Complete grooming kit with beard oil, trimming scissors, comb and moisturiser. Ideal gift for men.', 'brand': 'ManCave', 'rating': 4.6, 'reviews_count': 432, 'colors': ['Standard Kit', 'Premium Kit'], 'image': 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=600&q=80'},
            # Furniture
            {'name': 'Ergonomic Office Chair', 'category': 'furniture', 'price': 12999, 'stock': 25, 'description': 'Mesh back ergonomic chair with lumbar support, adjustable armrests, and seat height. For long work sessions.', 'brand': 'ComfortDesk', 'rating': 4.7, 'reviews_count': 389, 'colors': ['Black', 'Grey', 'Blue'], 'image': 'https://images.unsplash.com/photo-1592078615290-033ee584e267?w=600&q=80'},
            {'name': '3-Seater Fabric Sofa', 'category': 'furniture', 'price': 24999, 'stock': 10, 'description': 'Modern L-shaped fabric sofa with firm cushions and solid wood legs. Easy to assemble. Stain-resistant.', 'brand': 'HomePlus', 'rating': 4.5, 'reviews_count': 178, 'colors': ['Grey', 'Beige', 'Blue', 'Green'], 'image': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=80'},
            {'name': 'Study Table with Shelves', 'category': 'furniture', 'price': 6999, 'stock': 30, 'description': 'Compact study/work desk with 3-tier shelves. MDF board, metal legs. Ideal for home office or students.', 'brand': 'WorkNest', 'rating': 4.4, 'reviews_count': 224, 'colors': ['Walnut Brown', 'White', 'Black'], 'image': 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=600&q=80'},
            {'name': 'Wooden Bookshelf 5-Tier', 'category': 'furniture', 'price': 4499, 'stock': 40, 'description': 'Solid wood 5-tier open bookshelf. Perfect for books, decor and storage. Easy to assemble.', 'brand': 'ShelfLife', 'rating': 4.6, 'reviews_count': 312, 'colors': ['Natural Wood', 'Dark Walnut', 'White'], 'image': 'https://images.unsplash.com/photo-1594620302200-9a762244a156?w=600&q=80'},
        ]
        for p in sample_products:
            p['created_at'] = datetime.utcnow()
            # Add default values for options
            if 'sizes' not in p:
                p['sizes'] = []
            if 'colors' not in p:
                p['colors'] = []
            if 'brand' not in p:
                p['brand'] = 'Generic'
            if 'rating' not in p:
                p['rating'] = 0
            if 'reviews_count' not in p:
                p['reviews_count'] = 0
        products_collection.insert_many(sample_products)
        return jsonify({'message': f'Seeded {len(sample_products)} products successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
