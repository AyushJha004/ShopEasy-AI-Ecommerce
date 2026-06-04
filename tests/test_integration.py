"""
Integration tests for AI-powered features
Run with: python tests/test_integration.py
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_natural_language_search():
    """Test natural language search"""
    print("\n--- Testing Natural Language Search ---")
    
    queries = [
        "Show me budget watches under ₹3000",
        "Find gaming laptops under ₹80k",
        "Good quality smartphones in budget range"
    ]
    
    for query in queries:
        try:
            response = requests.get(
                f"{BASE_URL}/api/search/natural",
                params={"q": query}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Query: '{query}'")
                print(f"  Found: {data['count']} products")
                if data['results']:
                    print(f"  First result: {data['results'][0]['name']}")
            else:
                print(f"✗ Query: '{query}' - Status: {response.status_code}")
        except Exception as e:
            print(f"✗ Error testing query: {e}")


def test_recommendations():
    """Test product recommendations"""
    print("\n--- Testing Product Recommendations ---")
    
    # You need a valid user_id from your database
    user_id = "your_user_id_here"
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/recommendations/{user_id}"
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Recommendations retrieved")
            print(f"  Personalized: {data.get('is_personalized')}")
            print(f"  Product count: {len(data.get('recommendations', []))}")
            print(f"  Explanation: {data.get('explanation', 'N/A')[:100]}...")
        else:
            print(f"✗ Failed - Status: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_product_comparison():
    """Test product comparison"""
    print("\n--- Testing Product Comparison ---")
    
    # You need valid product IDs from your database
    product_ids = ["id1", "id2"]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/compare",
            json={"product_ids": product_ids}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Comparison generated")
            print(f"  Product count: {data.get('product_count')}")
            print(f"  Recommendation: {data.get('recommendation', 'N/A')[:100]}...")
        else:
            print(f"✗ Failed - Status: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_review_endpoints():
    """Test review endpoints"""
    print("\n--- Testing Review Endpoints ---")
    
    product_id = "your_product_id_here"
    
    # Get reviews
    try:
        response = requests.get(
            f"{BASE_URL}/api/products/{product_id}/reviews"
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Reviews retrieved: {data.get('total')} total")
        else:
            print(f"✗ Get reviews failed - Status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error getting reviews: {e}")
    
    # Get review summary
    try:
        response = requests.get(
            f"{BASE_URL}/api/products/{product_id}/reviews/summary"
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Review summary generated")
            print(f"  Sentiment: {data.get('sentiment')}")
            print(f"  Average rating: {data.get('average_rating')}")
            print(f"  Summary: {data.get('summary', 'N/A')[:100]}...")
        else:
            print(f"✗ Get summary failed - Status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error getting summary: {e}")


def test_add_review():
    """Test adding a review"""
    print("\n--- Testing Add Review ---")
    
    product_id = "your_product_id_here"
    user_id = "your_user_id_here"
    
    review_data = {
        "user_id": user_id,
        "rating": 5,
        "title": "Great product!",
        "text": "This product is amazing. I highly recommend it to everyone. Excellent quality and fast delivery."
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/products/{product_id}/reviews",
            json=review_data
        )
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Review added successfully")
            print(f"  Review ID: {data.get('review_id')}")
        else:
            print(f"✗ Failed - Status: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("AI Features Integration Tests")
    print("=" * 60)
    
    print("\nNote: Replace placeholder IDs with actual IDs from your database")
    print(f"Base URL: {BASE_URL}")
    
    test_natural_language_search()
    test_recommendations()
    test_product_comparison()
    test_review_endpoints()
    test_add_review()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)
