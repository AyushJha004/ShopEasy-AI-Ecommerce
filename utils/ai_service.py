import google.generativeai as genai
import os
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
MODEL_NAME = "gemini-pro"


class AIService:
    """Service for interacting with Gemini API"""
    
    @staticmethod
    def parse_search_query(query: str) -> Dict[str, Any]:
        """
        Parse natural language search query into structured filters
        Example: "Show me budget watches under ₹3000" 
        Returns: {category: "watches", max_price: 3000, budget: true}
        """
        try:
            prompt = f"""Parse this e-commerce search query and extract structured filters.
            
Query: "{query}"

Extract and return ONLY a JSON object with these fields (use null for missing):
- category: product category (singular, lowercase)
- max_price: maximum price in rupees (number or null)
- min_price: minimum price in rupees (number or null)
- brand: brand name (or null)
- features: list of key features/specs (or empty array)
- budget_oriented: true if query mentions "budget", "cheap", "affordable" etc

Example output:
{{"category": "watch", "max_price": 3000, "min_price": null, "brand": null, "features": ["durable", "water-resistant"], "budget_oriented": true}}

Return ONLY the JSON object, no other text."""

            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            
            response_text = response.text.strip()
            # Clean up response if it has markdown code blocks
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            parsed = json.loads(response_text)
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            return {"category": None, "max_price": None, "min_price": None, "brand": None, "features": [], "budget_oriented": False}
        except Exception as e:
            logger.error(f"Error parsing search query: {e}")
            return {"category": None, "max_price": None, "min_price": None, "brand": None, "features": [], "budget_oriented": False}
    
    @staticmethod
    def generate_recommendations_explanation(user_purchase_history: list, recommended_products: list, query: str = "") -> str:
        """Generate explanation for why products are recommended"""
        try:
            products_str = "\n".join([
                f"- {p['name']} (₹{p['price']}, Category: {p.get('category', 'N/A')})"
                for p in recommended_products
            ])
            
            history_str = "\n".join([
                f"- {p['name']} (₹{p['price']}, Category: {p.get('category', 'N/A')})"
                for p in user_purchase_history[:5]  # Last 5 purchases
            ])
            
            prompt = f"""Based on user's purchase history, explain why these products are recommended.

User's recent purchases:
{history_str}

Recommended products:
{products_str}

Provide a brief 2-3 sentence explanation of why these are good recommendations based on the user's preferences."""

            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return "Personalized recommendations based on your preferences"
    
    @staticmethod
    def generate_product_comparison(products: list) -> Dict[str, Any]:
        """Generate structured comparison between products"""
        try:
            products_str = "\n".join([
                f"""Product {i+1}: {p['name']}
Price: ₹{p['price']}
Category: {p.get('category', 'N/A')}
Description: {p.get('description', 'N/A')}
Stock: {p.get('stock', 0)}
Rating: {p.get('ratings', {}).get('average', 'N/A')}/5"""
                for i, p in enumerate(products)
            ])
            
            prompt = f"""Compare these {len(products)} products and provide analysis in JSON format.

{products_str}

Return a JSON object with:
- comparison_table: object with product names as keys, specs as values
- pros_cons: object with product names as keys, each having "pros" and "cons" arrays
- value_for_money: object with product names as keys, rating 1-5
- recommendation: string with which product is recommended and why
- price_analysis: string comparing prices and value

Return ONLY valid JSON, no other text."""

            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            
            response_text = response.text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse comparison response: {e}")
            return {"error": "Failed to generate comparison", "comparison_table": {}}
        except Exception as e:
            logger.error(f"Error generating comparison: {e}")
            return {"error": str(e), "comparison_table": {}}
    
    @staticmethod
    def summarize_reviews(reviews: list) -> Dict[str, Any]:
        """Summarize reviews using Gemini"""
        try:
            if not reviews:
                return {
                    "summary": "No reviews yet",
                    "sentiment": "neutral",
                    "key_points": [],
                    "ratings_distribution": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                    "total_reviews": 0
                }
            
            # Batch reviews if too many
            reviews_to_use = reviews[:10] if len(reviews) > 10 else reviews
            
            reviews_str = "\n".join([
                f"""Review {i+1} (Rating: {r['rating']}/5):
Title: {r.get('title', 'N/A')}
Text: {r.get('text', 'N/A')}"""
                for i, r in enumerate(reviews_to_use)
            ])
            
            prompt = f"""Summarize these {len(reviews_to_use)} product reviews into a JSON response.

{reviews_str}

Return a JSON object with:
- summary: 2-3 sentence summary of reviews
- sentiment: "positive", "negative", or "mixed"
- key_points: array of 3-5 main points customers mention
- pros: array of 3-5 pros mentioned
- cons: array of 3-5 cons mentioned
- recommendation: "recommended" or "not_recommended" based on reviews

Return ONLY valid JSON, no other text."""

            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            
            response_text = response.text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            parsed = json.loads(response_text)
            # Add ratings distribution
            ratings_dist = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
            for r in reviews:
                rating = str(r.get('rating', 3))
                if rating in ratings_dist:
                    ratings_dist[rating] += 1
            
            parsed["ratings_distribution"] = ratings_dist
            parsed["total_reviews"] = len(reviews)
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse review summary: {e}")
            return {
                "summary": "Unable to generate summary",
                "sentiment": "neutral",
                "key_points": [],
                "ratings_distribution": {},
                "total_reviews": len(reviews)
            }
        except Exception as e:
            logger.error(f"Error summarizing reviews: {e}")
            return {
                "summary": f"Error: {str(e)}",
                "sentiment": "neutral",
                "key_points": [],
                "ratings_distribution": {},
                "total_reviews": len(reviews)
            }


def get_ai_service() -> AIService:
    """Factory function to get AI service instance"""
    return AIService()
