from utils.ai_service import get_ai_service
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ComparisonService:
    """Service for product comparison"""
    
    def __init__(self, products_collection):
        self.products_collection = products_collection
        self.ai_service = get_ai_service()
    
    def compare_products(self, product_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple products
        """
        if not product_ids or len(product_ids) < 2:
            return {
                "error": "At least 2 products required for comparison",
                "comparison_table": {}
            }
        
        if len(product_ids) > 5:
            product_ids = product_ids[:5]  # Limit to 5 products
        
        try:
            from bson.objectid import ObjectId
            
            # Fetch products
            products = []
            for product_id in product_ids:
                product = self.products_collection.find_one(
                    {'_id': ObjectId(product_id)}
                )
                if product:
                    product['_id'] = str(product['_id'])
                    products.append(product)
            
            if len(products) < 2:
                return {
                    "error": "Could not find enough products",
                    "comparison_table": {}
                }
            
            # Generate comparison using Gemini
            comparison = self.ai_service.generate_product_comparison(products)
            comparison["products"] = products
            comparison["product_count"] = len(products)
            
            logger.info(f"Generated comparison for {len(products)} products")
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing products: {e}")
            return {
                "error": f"Comparison failed: {str(e)}",
                "comparison_table": {}
            }
