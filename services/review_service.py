from utils.ai_service import get_ai_service
from utils.cache import CacheService, generate_cache_key
from bson.objectid import ObjectId
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ReviewService:
    """Service for product reviews and summarization"""
    
    def __init__(self, reviews_collection, products_collection):
        self.reviews_collection = reviews_collection
        self.products_collection = products_collection
        self.ai_service = get_ai_service()
        self.cache = CacheService()
    
    def add_review(self, product_id: str, user_id: str, rating: int, 
                   title: str, text: str) -> Dict[str, Any]:
        """Add a review for a product"""
        try:
            if not (1 <= rating <= 5):
                return {"error": "Rating must be between 1 and 5"}
            
            review = {
                'product_id': ObjectId(product_id),
                'user_id': ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id,
                'rating': rating,
                'title': title,
                'text': text,
                'created_at': datetime.utcnow(),
                'helpful_count': 0
            }
            
            result = self.reviews_collection.insert_one(review)
            
            # Clear cache for this product's summary
            cache_key = generate_cache_key("review_summary", product_id)
            self.cache.delete(cache_key)
            
            logger.info(f"Added review for product {product_id}")
            return {
                "review_id": str(result.inserted_id),
                "message": "Review added successfully"
            }
        except Exception as e:
            logger.error(f"Error adding review: {e}")
            return {"error": str(e)}
    
    def get_product_reviews(self, product_id: str, limit: int = 10, 
                           page: int = 1) -> Dict[str, Any]:
        """Get all reviews for a product with pagination"""
        try:
            skip = (page - 1) * limit
            
            reviews = list(
                self.reviews_collection.find(
                    {'product_id': ObjectId(product_id)}
                )
                .sort('created_at', -1)
                .skip(skip)
                .limit(limit)
            )
            
            # Convert ObjectId to string
            for review in reviews:
                review['_id'] = str(review['_id'])
                review['product_id'] = str(review['product_id'])
                if isinstance(review['user_id'], ObjectId):
                    review['user_id'] = str(review['user_id'])
            
            # Get total count
            total_count = self.reviews_collection.count_documents(
                {'product_id': ObjectId(product_id)}
            )
            
            return {
                "reviews": reviews,
                "total": total_count,
                "page": page,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Error fetching reviews: {e}")
            return {"reviews": [], "total": 0, "page": page, "limit": limit}
    
    def get_review_summary(self, product_id: str) -> Dict[str, Any]:
        """Get AI-generated summary of product reviews"""
        try:
            # Check cache first
            cache_key = generate_cache_key("review_summary", product_id)
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info(f"Cache hit for review summary: {product_id}")
                return cached
            
            # Fetch all reviews for this product
            reviews = list(
                self.reviews_collection.find(
                    {'product_id': ObjectId(product_id)}
                )
                .sort('helpful_count', -1)
                .limit(50)  # Get up to 50 most helpful reviews
            )
            
            if not reviews:
                result = {
                    "product_id": product_id,
                    "summary": "No reviews yet",
                    "sentiment": "neutral",
                    "key_points": [],
                    "pros": [],
                    "cons": [],
                    "recommendation": "not_enough_data",
                    "ratings_distribution": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                    "average_rating": 0,
                    "total_reviews": 0
                }
            else:
                # Convert for AI processing
                reviews_for_ai = [
                    {
                        'rating': r.get('rating', 3),
                        'title': r.get('title', ''),
                        'text': r.get('text', '')
                    }
                    for r in reviews
                ]
                
                # Generate summary
                summary = self.ai_service.summarize_reviews(reviews_for_ai)
                
                # Calculate average rating
                ratings = [r.get('rating', 3) for r in reviews]
                avg_rating = sum(ratings) / len(ratings) if ratings else 0
                
                result = {
                    "product_id": product_id,
                    "average_rating": round(avg_rating, 2),
                    "total_reviews": len(reviews),
                    **summary
                }
            
            # Cache for 1 hour
            self.cache.set(cache_key, result, ttl=3600)
            return result
            
        except Exception as e:
            logger.error(f"Error summarizing reviews: {e}")
            return {
                "product_id": product_id,
                "summary": "Error generating summary",
                "sentiment": "neutral",
                "key_points": [],
                "error": str(e)
            }
    
    def mark_helpful(self, review_id: str) -> bool:
        """Mark a review as helpful"""
        try:
            self.reviews_collection.update_one(
                {'_id': ObjectId(review_id)},
                {'$inc': {'helpful_count': 1}}
            )
            
            # Clear summary cache for the product
            review = self.reviews_collection.find_one({'_id': ObjectId(review_id)})
            if review and 'product_id' in review:
                cache_key = generate_cache_key("review_summary", str(review['product_id']))
                self.cache.delete(cache_key)
            
            return True
        except Exception as e:
            logger.error(f"Error marking review as helpful: {e}")
            return False
