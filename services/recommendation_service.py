from utils.ai_service import get_ai_service
from utils.cache import CacheService, generate_cache_key
from bson.objectid import ObjectId
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for product recommendations"""
    
    def __init__(self, products_collection, orders_collection, users_collection):
        self.products_collection = products_collection
        self.orders_collection = orders_collection
        self.users_collection = users_collection
        self.ai_service = get_ai_service()
        self.cache = CacheService()
    
    def get_recommendations(self, user_id: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get personalized product recommendations for a user
        """
        # Check cache first
        cache_key = generate_cache_key("recommendations", user_id)
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info(f"Cache hit for recommendations: {user_id}")
            return cached
        
        # Get user's purchase history
        user_purchase_history = self._get_user_purchase_history(user_id)
        
        if not user_purchase_history:
            # New user - recommend popular/top-rated products
            recommendations = self._get_popular_products(limit)
            result = {
                "recommendations": recommendations,
                "explanation": "Recommended popular products for new users",
                "is_personalized": False
            }
        else:
            # Personalized recommendations based on history
            recommended_products = self._get_personalized_recommendations(
                user_purchase_history, limit
            )
            explanation = self.ai_service.generate_recommendations_explanation(
                user_purchase_history, recommended_products
            )
            
            result = {
                "recommendations": recommended_products,
                "explanation": explanation,
                "is_personalized": True
            }
        
        # Cache results (5 minutes)
        self.cache.set(cache_key, result, ttl=300)
        return result
    
    def _get_user_purchase_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get products purchased by user"""
        try:
            orders = list(self.orders_collection.find(
                {"buyer_info.user_id": user_id}
            ).sort("created_at", -1).limit(10))
            
            purchased_products = []
            for order in orders:
                for item in order.get('items', []):
                    product = self.products_collection.find_one(
                        {'_id': ObjectId(item['product_id'])}
                    )
                    if product:
                        product['_id'] = str(product['_id'])
                        purchased_products.append(product)
            
            return purchased_products
        except Exception as e:
            logger.error(f"Error fetching purchase history: {e}")
            return []
    
    def _get_personalized_recommendations(
        self, purchase_history: List[Dict[str, Any]], limit: int
    ) -> List[Dict[str, Any]]:
        """Get recommendations based on purchase history"""
        try:
            # Extract categories and price range from history
            categories = set()
            prices = []
            brands = set()
            
            for product in purchase_history[:5]:
                if 'category' in product:
                    categories.add(product['category'])
                if 'price' in product:
                    prices.append(product['price'])
                if 'brand' in product:
                    brands.add(product['brand'])
            
            # Build query for similar products
            query = {
                'category': {'$in': list(categories)} if categories else None,
                '_id': {'$nin': [ObjectId(p['_id']) for p in purchase_history]}
            }
            
            # Remove None filters
            query = {k: v for k, v in query.items() if v is not None}
            
            # Get average price range for filtering
            avg_price = sum(prices) / len(prices) if prices else 1000
            price_range_min = avg_price * 0.5
            price_range_max = avg_price * 1.5
            
            query['price'] = {'$gte': price_range_min, '$lte': price_range_max}
            
            # Fetch recommendations
            recommendations = list(self.products_collection.find(query).limit(limit))
            
            for product in recommendations:
                product['_id'] = str(product['_id'])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendations: {e}")
            return self._get_popular_products(limit)
    
    def _get_popular_products(self, limit: int) -> List[Dict[str, Any]]:
        """Get popular products (by rating or stock)"""
        try:
            products = list(
                self.products_collection.find()
                .sort([('ratings.average', -1), ('stock', -1)])
                .limit(limit)
            )
            
            for product in products:
                product['_id'] = str(product['_id'])
            
            return products
        except Exception as e:
            logger.error(f"Error fetching popular products: {e}")
            return []
