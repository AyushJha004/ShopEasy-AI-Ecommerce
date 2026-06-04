from pymongo import MongoClient
from datetime import datetime
from seed_data_1 import ELECTRONICS, CLOTHING
from seed_data_2 import TOYS, ART, SPORTS
from seed_data_3 import BOOKS, BEAUTY, FURNITURE

client = MongoClient('mongodb://localhost:27017')
db = client['ecommerce']
col = db['products']

col.delete_many({})

all_products = ELECTRONICS + CLOTHING + TOYS + ART + SPORTS + BOOKS + BEAUTY + FURNITURE

for p in all_products:
    p.setdefault('sizes', [])
    p.setdefault('colors', [])
    p.setdefault('brand', 'Generic')
    p.setdefault('rating', 0)
    p.setdefault('reviews_count', 0)
    p['created_at'] = datetime.utcnow()

col.insert_many(all_products)

counts = {}
for p in all_products:
    counts[p['category']] = counts.get(p['category'], 0) + 1

print(f"Seeded {len(all_products)} products:")
for cat, n in sorted(counts.items()):
    print(f"  {cat}: {n}")
