# Setup Guide for AI-Powered E-Commerce Features

## Overview

This guide will help you set up the new AI-powered features for the e-commerce platform.

## Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher
- MongoDB instance running
- Redis instance (optional, but recommended for caching)
- Gemini API key from Google

## Step 1: Get Your API Keys

### Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key (you'll need it in the `.env` file)

## Step 2: Install Dependencies

```bash
# Navigate to project directory
cd Ecommerce-Website

# Install Python dependencies
pip install -r requirements.txt
```

### New Dependencies Added:

- `google-generativeai` - Gemini API client
- `redis` - Caching layer
- `python-dotenv` - Environment variable management
- `requests` - HTTP library

## Step 3: Setup Environment Variables

### Create .env file

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your configuration
# On Windows, you can use:
notepad .env
```

### Configure .env

Fill in the following variables:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=ecommerce

# Gemini API (Required for AI features)
GEMINI_API_KEY=your_gemini_api_key_here

# Redis (Optional, but recommended for performance)
REDIS_URL=redis://localhost:6379

# Cache settings
CACHE_TTL=3600  # 1 hour

# Rate limiting
RATE_LIMIT=100  # requests per minute

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
```

## Step 4: Setup MongoDB

### Ensure MongoDB is running

```bash
# Windows (if installed as service)
net start MongoDB

# Or run MongoDB standalone
mongod

# Or use MongoDB Atlas (cloud)
# Update MONGODB_URI in .env with your Atlas connection string
```

### Update Products with Required Fields

Run this script to add missing fields to products:

```bash
python -c "
from pymongo import MongoClient
import os

client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))
db = client[os.getenv('MONGODB_DB', 'ecommerce')]
products = db['products']

# Add missing fields
products.update_many(
    { 'category': { '\$exists': False } },
    { '\$set': { 'category': 'Uncategorized' } }
)

products.update_many(
    { 'brand': { '\$exists': False } },
    { '\$set': { 'brand': 'Unknown' } }
)

products.update_many(
    { 'ratings': { '\$exists': False } },
    { '\$set': { 'ratings': { 'average': 0, 'count': 0 } } }
)

print('✓ Products updated with required fields')
"
```

## Step 5: Setup Redis (Optional but Recommended)

### Windows

```bash
# Using Windows Subsystem for Linux (WSL2)
wsl
sudo service redis-server start

# Or use Docker
docker run -d -p 6379:6379 redis:latest

# Or use Redis on Windows (pre-built binaries)
# Download from: https://github.com/microsoftarchive/redis/releases
redis-server.exe
```

### macOS

```bash
brew install redis
brew services start redis
```

### Linux

```bash
sudo apt-get install redis-server
sudo service redis-server start
```

### Verify Redis is running

```bash
redis-cli ping
# Should return: PONG
```

## Step 6: Verify Setup

### Test MongoDB Connection

```bash
python -c "
from pymongo import MongoClient
import os

try:
    client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))
    client.admin.command('ping')
    print('✓ MongoDB connected successfully')
except Exception as e:
    print(f'✗ MongoDB connection failed: {e}')
"
```

### Test Gemini API

```bash
python -c "
import os
import google.generativeai as genai

try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content('Say \"test successful\"')
    print(f'✓ Gemini API working: {response.text}')
except Exception as e:
    print(f'✗ Gemini API failed: {e}')
"
```

### Test Redis Connection

```bash
python -c "
import os
import redis

try:
    redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
    redis_client.ping()
    print('✓ Redis connected successfully')
except Exception as e:
    print(f'✗ Redis connection failed (optional): {e}')
"
```

## Step 7: Start the Application

```bash
# Navigate to project directory
cd Ecommerce-Website

# Run Flask application
python app.py

# Should output:
# * Running on http://127.0.0.1:5000
```

## Step 8: Test the Features

### Option A: Using cURL

```bash
# Test natural language search
curl "http://localhost:5000/api/search/natural?q=budget watches under 3000"

# Test recommendations
curl "http://localhost:5000/api/recommendations/{user_id}"

# Test product comparison
curl -X POST http://localhost:5000/api/compare \
  -H "Content-Type: application/json" \
  -d '{"product_ids": ["product_id_1", "product_id_2"]}'

# Get reviews
curl "http://localhost:5000/api/products/{product_id}/reviews"

# Get review summary
curl "http://localhost:5000/api/products/{product_id}/reviews/summary"
```

### Option B: Using Python Integration Tests

```bash
python tests/test_integration.py
```

### Option C: Using Postman or Insomnia

Import the requests from the documentation in `AI_FEATURES.md`

## Troubleshooting

### Issue: "MongoDB connection failed"

**Solution:**

- Ensure MongoDB is running: `mongod` or `net start MongoDB`
- Check MONGODB_URI in .env file
- If using Atlas, ensure your IP is whitelisted

### Issue: "Gemini API not responding"

**Solution:**

- Verify API key is correct in .env
- Check that API is enabled in Google Cloud Console
- Check rate limits (free tier: 15 requests/min)
- Verify internet connection

### Issue: "Redis connection failed (optional)"

**Solution:**

- This is non-critical - features work without Redis, just slower
- Install Redis if you want caching
- Ensure Redis is running before starting app

### Issue: "ModuleNotFoundError: No module named 'google.generativeai'"

**Solution:**

```bash
pip install --upgrade google-generativeai
```

### Issue: "Reviews collection not found"

**Solution:**

- MongoDB automatically creates collections, this is normal
- First time you add a review, the collection will be created

### Issue: "Products have no results in search"

**Solution:**

- Ensure products have `category` field populated
- Update products: `db.products.updateMany({}, {$set: {category: "Electronics"}})`
- Try simpler search queries
- Check MongoDB has product data

## Production Deployment

When deploying to production:

1. **Update Flask settings:**

```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

2. **Use environment variables:**

```bash
export FLASK_ENV=production
export GEMINI_API_KEY=your_key
```

3. **Use a production WSGI server:**

```bash
pip install gunicorn
gunicorn -w 4 app:app
```

4. **Enable HTTPS:**
   Use a reverse proxy like Nginx with SSL

5. **Monitor logs:**
   Configure proper logging to file

6. **Rate limiting:**
   Implement per-IP rate limiting with Nginx or similar

## File Structure

```
Ecommerce-Website/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .env                     # Your environment variables (create this)
├── AI_FEATURES.md           # API documentation
├── SETUP_GUIDE.md           # This file
│
├── utils/
│   ├── __init__.py
│   ├── ai_service.py        # Gemini API wrapper
│   └── cache.py             # Redis caching layer
│
├── services/
│   ├── __init__.py
│   ├── search_service.py    # Natural language search
│   ├── recommendation_service.py  # Product recommendations
│   ├── comparison_service.py      # Product comparison
│   └── review_service.py          # Review management
│
└── tests/
    ├── __init__.py
    └── test_integration.py   # Integration tests
```

## Next Steps

1. Read `AI_FEATURES.md` for complete API documentation
2. Test all endpoints with sample data
3. Integrate AI search into your frontend
4. Add reviews functionality to product pages
5. Display recommendations on homepage

## Support & Resources

- **Gemini API**: https://ai.google.dev/docs
- **MongoDB**: https://docs.mongodb.com/
- **Redis**: https://redis.io/docs/
- **Flask**: https://flask.palletsprojects.com/
- **Project Issues**: [GitHub Issues](https://github.com/AyushJha004/Ecommerce-Website/issues)

## Performance Tips

1. **Enable Redis caching** for better performance
2. **Add database indexes** on frequently searched fields
3. **Batch API calls** to reduce Gemini API usage
4. **Monitor API costs** on Google Cloud Console
5. **Use pagination** for large result sets

---

**Setup completed! Your AI-powered e-commerce features are ready to use.** 🚀
