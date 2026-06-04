# AI-Powered E-Commerce Features

This document describes the new AI-powered features added to the e-commerce platform.

## Features Overview

### 1. Natural Language Product Search

Search for products using natural language queries instead of traditional filters.

**Endpoint:** `GET /api/search/natural?q={query}`

**Example Queries:**

- "Show me budget watches under ₹3000"
- "Find gaming laptops under ₹80k"
- "Show affordable smartwatches with good battery"

**Response:**

```json
{
  "query": "Show me budget watches under ₹3000",
  "results": [
    {
      "_id": "product_id",
      "name": "Watch Name",
      "price": 2500,
      "category": "watches",
      "description": "...",
      "stock": 10
    }
  ],
  "count": 5
}
```

**How it works:**

1. Gemini API parses the natural language query
2. Extracts structured filters (category, price range, features)
3. Queries MongoDB with intelligent filters
4. Returns products sorted by relevance
5. Results are cached for 30 minutes

---

### 2. Product Recommendations

Get personalized product recommendations based on user's purchase history.

**Endpoint:** `GET /api/recommendations/{user_id}?limit=5`

**Response:**

```json
{
  "recommendations": [
    {
      "_id": "product_id",
      "name": "Product Name",
      "price": 5000,
      "category": "category",
      "stock": 15
    }
  ],
  "explanation": "Based on your previous purchases in electronics and your price range...",
  "is_personalized": true
}
```

**How it works:**

1. Fetches user's purchase history from orders
2. Analyzes purchase patterns (categories, price range, brands)
3. Finds similar products not yet purchased
4. Uses Gemini to explain recommendations
5. Results cached for 5 minutes per user

---

### 3. Product Comparison

Compare multiple products side-by-side with AI-powered analysis.

**Endpoint:** `POST /api/compare`

**Request:**

```json
{
  "product_ids": ["id1", "id2", "id3"]
}
```

**Response:**

```json
{
  "comparison_table": {
    "Product 1": {
      "price": 5000,
      "category": "...",
      "specs": "..."
    },
    "Product 2": {
      "price": 8000,
      "category": "...",
      "specs": "..."
    }
  },
  "pros_cons": {
    "Product 1": {
      "pros": ["Good price", "Reliable"],
      "cons": ["Limited features"]
    }
  },
  "value_for_money": {
    "Product 1": 5,
    "Product 2": 4
  },
  "recommendation": "Product 1 offers the best value for money...",
  "price_analysis": "Product 1 is most affordable...",
  "products": [...],
  "product_count": 2
}
```

**How it works:**

1. Fetches details for all specified products
2. Sends to Gemini for comprehensive analysis
3. Generates pros/cons for each product
4. Provides price analysis and value ratings
5. Returns structured comparison for easy viewing

---

### 4. Review Summarization

Get AI-generated summaries of product reviews without reading them all.

**Endpoint:** `GET /api/products/{product_id}/reviews/summary`

**Response:**

```json
{
  "product_id": "id",
  "summary": "Customers love this product for its durability and affordability...",
  "sentiment": "positive",
  "average_rating": 4.2,
  "total_reviews": 45,
  "key_points": [
    "Great build quality",
    "Excellent value for money",
    "Long battery life",
    "Good customer service"
  ],
  "pros": ["Durable", "Affordable", "Good warranty"],
  "cons": ["Limited color options", "Slow shipping"],
  "recommendation": "recommended",
  "ratings_distribution": {
    "1": 2,
    "2": 3,
    "3": 8,
    "4": 18,
    "5": 14
  }
}
```

---

## Review Endpoints

### Add a Review

**Endpoint:** `POST /api/products/{product_id}/reviews`

**Request:**

```json
{
  "user_id": "user_id",
  "rating": 5,
  "title": "Excellent product!",
  "text": "This product exceeded my expectations. Great quality and fast delivery."
}
```

**Response:**

```json
{
  "review_id": "review_id",
  "message": "Review added successfully"
}
```

### Get Product Reviews

**Endpoint:** `GET /api/products/{product_id}/reviews?page=1&limit=10`

**Response:**

```json
{
  "reviews": [
    {
      "_id": "review_id",
      "product_id": "product_id",
      "user_id": "user_id",
      "rating": 5,
      "title": "Great product",
      "text": "I love this product...",
      "created_at": "2024-01-15T10:30:00",
      "helpful_count": 12
    }
  ],
  "total": 45,
  "page": 1,
  "limit": 10
}
```

### Mark Review as Helpful

**Endpoint:** `POST /api/reviews/{review_id}/helpful`

**Response:**

```json
{
  "message": "Review marked as helpful"
}
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with:

- `GEMINI_API_KEY`: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `MONGODB_URI`: Your MongoDB connection string
- `REDIS_URL`: Your Redis instance URL

### 3. Create MongoDB Indexes

The application automatically creates indexes on startup. However, you can manually create them using the MongoDB shell:

```javascript
db.products.createIndex({ category: 1 });
db.products.createIndex({ price: 1 });
db.products.createIndex({ brand: 1 });
db.products.createIndex({ name: "text", description: "text" });

db.reviews.createIndex({ product_id: 1 });
db.reviews.createIndex({ user_id: 1 });
db.reviews.createIndex({ created_at: -1 });
```

### 4. Ensure Products Have Required Fields

For full functionality, products should have these fields:

- `name` (string)
- `price` (number)
- `description` (string)
- `category` (string)
- `brand` (string)
- `stock` (number)
- `ratings` (object with `average` and `count`)

Update existing products:

```python
db.products.update_many(
    { "category": { "$exists": False } },
    { "$set": { "category": "Uncategorized", "brand": "Unknown" } }
)
```

---

## Performance Considerations

### Caching Strategy

- **Search results**: 30 minutes
- **Recommendations**: 5 minutes per user
- **Review summaries**: 1 hour

Redis is used for all caching. If Redis is unavailable, the system will still work but API calls won't be cached.

### Rate Limiting

By default, 100 requests per minute are allowed per user. Configure via `RATE_LIMIT` in `.env`.

### Database Indexes

Indexes are automatically created on:

- `products.category`
- `products.price`
- `products.brand`
- `products.name` and `products.description` (text search)
- `reviews.product_id`
- `reviews.user_id`
- `reviews.created_at`

---

## API Cost Considerations

### Gemini API Pricing (Free Tier Available)

- 15 requests per minute (free tier)
- Some features may require paid API

**To optimize costs:**

1. Enable caching (enabled by default)
2. Batch operations where possible
3. Review and batch limit API calls

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Successful creation (reviews)
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**

```json
{
  "error": "Description of the error"
}
```

---

## Testing the Features

### 1. Test Natural Language Search

```bash
curl "http://localhost:5000/api/search/natural?q=budget watches under 3000"
```

### 2. Test Recommendations

```bash
curl "http://localhost:5000/api/recommendations/{user_id}"
```

### 3. Test Product Comparison

```bash
curl -X POST http://localhost:5000/api/compare \
  -H "Content-Type: application/json" \
  -d '{"product_ids": ["id1", "id2"]}'
```

### 4. Test Reviews

```bash
# Get reviews
curl "http://localhost:5000/api/products/{product_id}/reviews"

# Add review
curl -X POST http://localhost:5000/api/products/{product_id}/reviews \
  -H "Content-Type: application/json" \
  -d '{"user_id": "uid", "rating": 5, "title": "Great!", "text": "..."}'

# Get summary
curl "http://localhost:5000/api/products/{product_id}/reviews/summary"
```

---

## Troubleshooting

### "MongoDB connection failed"

- Ensure MongoDB is running
- Check `MONGODB_URI` in `.env`

### "Redis connection failed"

- Caching will be disabled, but features still work
- Install and run Redis if needed

### "Gemini API error"

- Check that `GEMINI_API_KEY` is set correctly
- Verify API key is active in Google AI Studio
- Check rate limits (free tier: 15 requests/min)

### "Empty search results"

- Ensure products have `category` field populated
- Try more general queries
- Check MongoDB has data

---

## Future Enhancements

1. **Sentiment Analysis**: More detailed sentiment extraction from reviews
2. **Similar Products**: Find visually or specification-similar products
3. **Price Tracking**: Historical price trends and predictions
4. **User Preferences**: Machine learning for better recommendations
5. **Multi-language Support**: Handle queries in multiple languages
6. **Image Search**: Search by product image

---

## Support & Documentation

- [Gemini API Documentation](https://ai.google.dev/docs)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Redis Documentation](https://redis.io/docs/)
