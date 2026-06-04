# Feature Showcase - Real Examples

This document shows real-world examples of how each AI feature works.

## 1. Natural Language Search - Real Examples

### Example 1: Budget Watch Search

```
Query: "Show me budget watches under ₹3000"

Processing:
1. Gemini parses query
2. Extracts: category="watch", max_price=3000, budget_oriented=true
3. Builds filter: {category: /watch/i, price: {$lte: 3000}}
4. MongoDB returns matching products
5. Sorts by price (ascending, because budget_oriented=true)

Response:
{
  "query": "Show me budget watches under ₹3000",
  "results": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "name": "Titanium Sport Watch",
      "price": 2499,
      "category": "watches",
      "description": "Durable titanium case with digital display",
      "brand": "TechTime",
      "stock": 15,
      "ratings": {"average": 4.2, "count": 145}
    },
    {
      "_id": "507f1f77bcf86cd799439012",
      "name": "Classic Analog Watch",
      "price": 2799,
      "category": "watches",
      "description": "Elegant analog design with leather strap",
      "brand": "ClassicStyle",
      "stock": 8,
      "ratings": {"average": 4.5, "count": 89}
    }
  ],
  "count": 2
}
```

### Example 2: Gaming Laptop Search

```
Query: "Find gaming laptops under ₹80k with good graphics"

Processing:
1. Gemini extracts: category="laptop", max_price=80000, features=["gaming", "graphics"]
2. Builds filter: {category: /laptop/i, price: {$lte: 80000}, $text: {$search: "gaming graphics"}}

Response:
{
  "query": "Find gaming laptops under ₹80k with good graphics",
  "count": 3,
  "results": [
    {
      "_id": "507f1f77bcf86cd799439013",
      "name": "ROG Gaming Laptop Pro",
      "price": 75000,
      "category": "laptops",
      "brand": "ASUS",
      "description": "RTX 3060, 16GB RAM, Gaming-ready laptop",
      "stock": 5,
      "ratings": {"average": 4.7, "count": 234}
    }
  ]
}
```

---

## 2. Product Recommendations - Real Examples

### Example 1: Tech Enthusiast

```
User ID: "user_12345"
Purchase History:
- Gaming Mouse (₹5000)
- Mechanical Keyboard (₹8000)
- USB-C Hub (₹3000)

Processing:
1. System analyzes purchases → Electronics lover, price_range: ₹3k-₹8k
2. Gemini explains: "Based on your gaming peripherals..."
3. Finds complementary products

Response:
{
  "recommendations": [
    {
      "_id": "507f1f77bcf86cd799439014",
      "name": "Gaming Headset Pro",
      "price": 6500,
      "category": "electronics",
      "description": "7.1 Surround Sound, RGB LED"
    },
    {
      "_id": "507f1f77bcf86cd799439015",
      "name": "Monitor Stand with USB Hub",
      "price": 4200,
      "category": "accessories"
    }
  ],
  "explanation": "Based on your recent purchases of gaming peripherals and tech accessories, we recommend products that complement your gaming setup. The gaming headset pairs well with your mechanical keyboard, and the monitor stand maximizes your desk space.",
  "is_personalized": true
}
```

### Example 2: New User (No History)

```
User ID: "user_new_999"
Purchase History: None

Processing:
1. No purchase history found
2. System returns popular/top-rated products
3. Recommendation not personalized

Response:
{
  "recommendations": [
    {
      "_id": "507f1f77bcf86cd799439016",
      "name": "Best Seller Watch",
      "price": 4999,
      "category": "watches",
      "ratings": {"average": 4.8, "count": 1200}
    },
    {
      "_id": "507f1f77bcf86cd799439017",
      "name": "Top Rated Smartphone",
      "price": 25000,
      "category": "electronics",
      "ratings": {"average": 4.9, "count": 5600}
    }
  ],
  "explanation": "Recommended popular products for new users",
  "is_personalized": false
}
```

---

## 3. Product Comparison - Real Examples

### Example 1: Smartphone Comparison

```
Request:
POST /api/compare
{
  "product_ids": ["507f1f77bcf86cd799439018", "507f1f77bcf86cd799439019"]
}

Products:
1. SmartPhone Pro Max - ₹65000 - 12MP Camera, 5G, 120Hz Display
2. Budget Smart Phone - ₹25000 - 8MP Camera, 4G, 60Hz Display

Response:
{
  "comparison_table": {
    "SmartPhone Pro Max": {
      "Price": "₹65000",
      "Camera": "12MP with Night Mode",
      "Display": "120Hz AMOLED",
      "Processor": "Latest Flagship",
      "Battery": "5000mAh",
      "5G Support": "Yes",
      "Rating": "4.8/5"
    },
    "Budget Smart Phone": {
      "Price": "₹25000",
      "Camera": "8MP Standard",
      "Display": "60Hz IPS LCD",
      "Processor": "Mid-range",
      "Battery": "4000mAh",
      "5G Support": "No",
      "Rating": "4.3/5"
    }
  },
  "pros_cons": {
    "SmartPhone Pro Max": {
      "pros": [
        "Excellent camera quality with night mode",
        "High refresh rate display for smooth scrolling",
        "5G enabled for future-ready connectivity",
        "Premium build quality and design",
        "Larger battery capacity"
      ],
      "cons": [
        "Higher price point (2.6x more expensive)",
        "May be overkill for basic users",
        "Premium price doesn't always justify for casual users"
      ]
    },
    "Budget Smart Phone": {
      "pros": [
        "Affordable price point",
        "Great value for basic daily use",
        "Reliable performance for emails and social media",
        "Smaller and lightweight"
      ],
      "cons": [
        "Lower camera quality",
        "Slower refresh rate display",
        "No 5G support",
        "Smaller battery"
      ]
    }
  },
  "value_for_money": {
    "SmartPhone Pro Max": 3,
    "Budget Smart Phone": 5
  },
  "recommendation": "For most users, the Budget Smart Phone offers better value for money at ₹25000. However, if you prioritize photography and need the latest technology, the Pro Max is worth the investment.",
  "price_analysis": "The Pro Max is 2.6 times more expensive than the Budget model. Choose based on your specific needs: photography enthusiasts should pick Pro Max, budget-conscious users should pick Budget model.",
  "products": [...],
  "product_count": 2
}
```

### Example 2: Laptop Comparison

```
Request:
POST /api/compare
{
  "product_ids": ["laptop1", "laptop2", "laptop3"]
}

Response:
{
  "comparison_table": {
    "Gaming Laptop": {
      "Price": "₹85000",
      "Processor": "Intel i7-12th Gen",
      "GPU": "RTX 3050",
      "RAM": "16GB",
      "Storage": "512GB SSD"
    },
    "Ultrabook": {
      "Price": "₹75000",
      "Processor": "Intel i5-12th Gen",
      "GPU": "Intel Iris Xe",
      "RAM": "8GB",
      "Storage": "256GB SSD"
    },
    "Budget Laptop": {
      "Price": "₹35000",
      "Processor": "AMD Ryzen 5",
      "GPU": "Radeon Graphics",
      "RAM": "8GB",
      "Storage": "256GB SSD"
    }
  },
  "recommendation": "Choose Gaming Laptop for high-performance gaming and video editing. Choose Ultrabook for portability and everyday work. Choose Budget Laptop for basic tasks and students."
}
```

---

## 4. Review Summarization - Real Examples

### Example 1: Positive Product Reviews

```
Request:
GET /api/products/507f1f77bcf86cd799439020/reviews/summary

Product: Premium Headphones

Response:
{
  "product_id": "507f1f77bcf86cd799439020",
  "summary": "Customers love these headphones for exceptional sound quality and comfort. Most reviewers praise the active noise cancellation and long battery life. The premium build quality justifies the price for audiophiles. A few users mentioned the price is steep compared to competitors.",
  "sentiment": "positive",
  "average_rating": 4.6,
  "total_reviews": 156,
  "key_points": [
    "Outstanding audio quality with deep bass",
    "Excellent active noise cancellation",
    "Comfortable for extended wear",
    "Long battery life (40+ hours)",
    "Premium construction and materials"
  ],
  "pros": [
    "Crystal clear sound",
    "Powerful noise cancellation",
    "Durable build quality",
    "Excellent customer support"
  ],
  "cons": [
    "Expensive compared to competitors",
    "Heavy for some users",
    "App could be better"
  ],
  "recommendation": "recommended",
  "ratings_distribution": {
    "1": 2,
    "2": 3,
    "3": 12,
    "4": 58,
    "5": 81
  }
}
```

### Example 2: Mixed Reviews

```
Request:
GET /api/products/507f1f77bcf86cd799439021/reviews/summary

Product: Budget Smartphone

Response:
{
  "product_id": "507f1f77bcf86cd799439021",
  "summary": "This budget smartphone offers good value for the price, with a decent camera and battery life. However, some users report heating issues after extended use and the display could be better. Performance is adequate for everyday use but struggles with heavy games.",
  "sentiment": "mixed",
  "average_rating": 3.8,
  "total_reviews": 287,
  "key_points": [
    "Great value for budget price",
    "Good battery life",
    "Camera performs well in daylight",
    "Heating issues reported",
    "Display brightness could be better"
  ],
  "pros": [
    "Affordable price",
    "Good battery backup",
    "Fast processor for daily use",
    "Good connectivity options"
  ],
  "cons": [
    "Gets warm during gaming",
    "Poor low-light photography",
    "Display not as bright as competitors",
    "Only 1 year warranty"
  ],
  "recommendation": "recommended",
  "ratings_distribution": {
    "1": 8,
    "2": 18,
    "3": 76,
    "4": 112,
    "5": 73
  }
}
```

### Example 3: New Product (No Reviews)

```
Request:
GET /api/products/507f1f77bcf86cd799439022/reviews/summary

Product: Newly Listed Item

Response:
{
  "product_id": "507f1f77bcf86cd799439022",
  "summary": "No reviews yet",
  "sentiment": "neutral",
  "key_points": [],
  "average_rating": 0,
  "total_reviews": 0,
  "ratings_distribution": {
    "1": 0,
    "2": 0,
    "3": 0,
    "4": 0,
    "5": 0
  }
}
```

---

## 5. Review Management - Real Examples

### Example 1: Add a Review

```
Request:
POST /api/products/507f1f77bcf86cd799439020/reviews
{
  "user_id": "user_12345",
  "rating": 5,
  "title": "Best headphones I've ever owned!",
  "text": "These headphones exceeded all my expectations. The sound quality is absolutely amazing with deep, rich bass. The active noise cancellation works perfectly on flights and trains. They're also very comfortable even after hours of use. Highly recommend to anyone looking for premium audio."
}

Response:
{
  "review_id": "507f1f77bcf86cd799439023",
  "message": "Review added successfully"
}
```

### Example 2: Get Product Reviews (Paginated)

```
Request:
GET /api/products/507f1f77bcf86cd799439020/reviews?page=1&limit=3

Response:
{
  "reviews": [
    {
      "_id": "507f1f77bcf86cd799439024",
      "product_id": "507f1f77bcf86cd799439020",
      "user_id": "user_12345",
      "rating": 5,
      "title": "Best headphones I've ever owned!",
      "text": "These headphones exceeded all my expectations...",
      "created_at": "2024-01-15T10:30:00",
      "helpful_count": 47
    },
    {
      "_id": "507f1f77bcf86cd799439025",
      "product_id": "507f1f77bcf86cd799439020",
      "user_id": "user_67890",
      "rating": 4,
      "title": "Great quality, premium price",
      "text": "Excellent sound and build quality...",
      "created_at": "2024-01-14T15:20:00",
      "helpful_count": 32
    }
  ],
  "total": 156,
  "page": 1,
  "limit": 3
}
```

### Example 3: Mark Review as Helpful

```
Request:
POST /api/reviews/507f1f77bcf86cd799439024/helpful

Response:
{
  "message": "Review marked as helpful"
}
```

---

## Complete User Journey Example

### Scenario: John looking for a gaming laptop

**Step 1: Search**

```
John searches: "I need a gaming laptop for under ₹1 lakh that can run modern games"

API Call: GET /api/search/natural?q=I need a gaming laptop for under 1 lakh that can run modern games

Returns: 12 gaming laptops under ₹100,000
```

**Step 2: View Reviews**

```
John clicks on a laptop to see reviews

API Call: GET /api/products/{laptop_id}/reviews/summary

Sees: "4.6 star rating, customers love the gaming performance"
```

**Step 3: Compare Options**

```
John wants to compare 3 laptops he's interested in

API Call: POST /api/compare with 3 product IDs

Sees: Detailed comparison, pros/cons, value ratings
```

**Step 4: Get Recommendations**

```
John is logged in, system recommends accessories

API Call: GET /api/recommendations/{john_user_id}

Sees: "Gaming Mouse", "Cooling Pad", "USB Hub" recommended
```

**Step 5: Leave Review**

```
After purchase, John leaves a review

API Call: POST /api/products/{laptop_id}/reviews
{
  "rating": 5,
  "title": "Perfect gaming laptop!",
  "text": "..."
}

System updates review summary for next user
```

---

## Performance Metrics (Expected)

- **Search Response Time**: < 500ms (with cache: < 50ms)
- **Recommendations Response Time**: < 800ms (with cache: < 100ms)
- **Comparison Generation Time**: < 2 seconds
- **Review Summary Generation Time**: < 3 seconds
- **Review Addition Time**: < 500ms

---

## Cost Estimates (Gemini API)

- Free Tier: 15 requests/minute
- ~$0.000075 per request (when paying)
- Each feature uses 1 API call per request

---

These examples show realistic usage patterns and responses from the AI-powered features.
