# Quick Start Guide - AI Features

Get the AI-powered features running in 5 minutes!

## TL;DR - Quick Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Ensure MongoDB is running
mongod

# 4. Start app
python app.py

# 5. Test it
curl "http://localhost:5000/api/search/natural?q=budget watches"
```

## Getting Gemini API Key (1 minute)

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key and paste in `.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```

## The 4 AI Features

### 1️⃣ Natural Language Search

```bash
curl "http://localhost:5000/api/search/natural?q=budget watches under 3000"
```

### 2️⃣ Recommendations

```bash
curl "http://localhost:5000/api/recommendations/{user_id}"
```

### 3️⃣ Product Comparison

```bash
curl -X POST http://localhost:5000/api/compare \
  -H "Content-Type: application/json" \
  -d '{"product_ids": ["id1", "id2"]}'
```

### 4️⃣ Review Summarization

```bash
curl "http://localhost:5000/api/products/{product_id}/reviews/summary"
```

## API Reference Summary

| Feature         | Endpoint                             | Method | Example                  |
| --------------- | ------------------------------------ | ------ | ------------------------ |
| Search          | `/api/search/natural?q=`             | GET    | `q=budget watches`       |
| Recommendations | `/api/recommendations/{user_id}`     | GET    | -                        |
| Compare         | `/api/compare`                       | POST   | `{"product_ids": [...]}` |
| Add Review      | `/api/products/{id}/reviews`         | POST   | Rating + text            |
| Get Reviews     | `/api/products/{id}/reviews`         | GET    | -                        |
| Review Summary  | `/api/products/{id}/reviews/summary` | GET    | -                        |

## Common Issues & Fixes

**❌ "Gemini API error"**
→ Copy API key from https://makersuite.google.com/app/apikey

**❌ "MongoDB connection failed"**
→ Run `mongod` in another terminal

**❌ "Redis connection failed"**
→ This is optional - system still works without it

**❌ "No search results"**
→ Add `category` field to your products in MongoDB

## Full Documentation

- **Complete API docs**: See `AI_FEATURES.md`
- **Setup guide**: See `SETUP_GUIDE_AI.md`
- **Testing**: Run `python tests/test_integration.py`

## Architecture Overview

```
Natural Language Query
         ↓
  Gemini API (parse)
         ↓
  Extract: category, price, features
         ↓
  MongoDB Filter
         ↓
  Return Results (cached 30 min)
```

## Integration Example

```python
from services.search_service import SearchService
from pymongo import MongoClient

client = MongoClient()
db = client['ecommerce']
search = SearchService(db['products'])

# Search
results = search.natural_language_search("budget watches under 3000")
print(f"Found {len(results)} products")
```

## Next Steps

1. ✅ Set up API key (1 min)
2. ✅ Install dependencies (1 min)
3. ✅ Test search endpoint (1 min)
4. ✅ Integrate into frontend
5. ✅ Deploy to production

## Support

- **GitHub**: https://github.com/AyushJha004/Ecommerce-Website
- **Google AI**: https://ai.google.dev/docs
- **MongoDB**: https://docs.mongodb.com/

---

**Happy coding! 🚀**
