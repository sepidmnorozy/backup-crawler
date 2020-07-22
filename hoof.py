from pymongo import MongoClient

client = MongoClient()
db = client.real_estate

# Reset.
db.houses.delete_many({})

# Insert houses.
db.houses.insert_many([
    {"address": "100 Main St.", "price": 45000},
    {"address": "110 Main St.", "price": 50000},
    {"address": "1400 Rich Ave.", "price": 200000},
])

# Find inexpensive houses.
print("FIND PRICE LT 60000")
cursor = db.houses.find({"price": {"$lt": 60000,"$gt":46000}})
for doc in cursor:
    print(doc)

# Find expensive houses.
print("FIND PRICE GT 60000")
cursor = db.houses.find({"price": {"$gt": 60000}})
for doc in cursor:
    print(doc)
