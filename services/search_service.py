from utils.ai_service import get_ai_service
from utils.cache import CacheService, generate_cache_key
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Service for natural language product search"""
    
    def __init__(self, products_collection):
        self.products_collection = products_collection
        self.ai_service = get_ai_service()
        self.cache = CacheService()
    
    def natural_language_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search products using natural language query
        Example: "Show me budget watches under ₹3000"
        """
        # Check cache first
        cache_key = generate_cache_key("search", query.lower())
        cached_results = self.cache.get(cache_key)
        if cached_results is not None:
            logger.info(f"Cache hit for query: {query}")
            return cached_results
        
        # Parse query using Gemini
        logger.info(f"Parsing query: {query}")
        parsed_query = self.ai_service.parse_search_query(query)
        logger.info(f"Parsed query: {parsed_query}")
        
        # Build MongoDB filter
        filter_dict = self._build_filter(parsed_query)
        logger.info(f"MongoDB filter: {filter_dict}")
        
        # Query database
        try:
            results = list(self.products_collection.find(filter_dict))
            
            # Convert ObjectId to string and sort by relevance
            for product in results:
                product['_id'] = str(product['_id'])
            
            # Sort by price if budget query
            if parsed_query.get('budget_oriented'):
                results.sort(key=lambda x: x['price'])
            
            # Cache results
            self.cache.set(cache_key, results, ttl=1800)  # 30 min cache
            
            logger.info(f"Found {len(results)} products")
            return results
            
        except Exception as e:
            logger.error(f"Database error during search: {e}")
            return []
    
    def _build_filter(self, parsed_query: Dict[str, Any]) -> Dict[str, Any]:
        """Build MongoDB filter from parsed query"""
        filter_dict = {}
        
        # Category filter
        if parsed_query.get('category'):
            filter_dict['category'] = {'$regex': parsed_query['category'], '$options': 'i'}
        
        # Price range filter
        price_filter = {}
        if parsed_query.get('min_price') is not None:
            price_filter['$gte'] = parsed_query['min_price']
        if parsed_query.get('max_price') is not None:
            price_filter['$lte'] = parsed_query['max_price']
        
        if price_filter:
            filter_dict['price'] = price_filter
        
        # Brand filter
        if parsed_query.get('brand'):
            filter_dict['brand'] = {'$regex': parsed_query['brand'], '$options': 'i'}
        
        # Features filter - use text search if available
        if parsed_query.get('features'):
            features_query = ' '.join(parsed_query['features'])
            filter_dict['$text'] = {'$search': features_query}
        
        return filter_dict
