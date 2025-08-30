"""
Simple script to check MongoDB venue documents and verify the new schema
"""
import pymongo
from pprint import pprint

# Connect to MongoDB (assuming it's accessible via port forwarding)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["planeet_db"]
venues_collection = db["venues"]

print("=== MongoDB Venue Schema Check ===")
print(f"Total venues in collection: {venues_collection.count_documents({})}")
print()

# Get a few recent venue documents
print("=== Recent Venue Documents ===")
recent_venues = list(venues_collection.find().sort("created_at", -1).limit(3))

for i, venue in enumerate(recent_venues, 1):
    print(f"--- Venue {i} ---")
    pprint(venue)
    print()

# Check for venues with Google place_id
print("=== Checking for Google place_id field ===")
google_venue_count = venues_collection.count_documents({"google_place_id": {"$exists": True}})
print(f"Venues with google_place_id: {google_venue_count}")

if google_venue_count > 0:
    sample_google_venue = venues_collection.find_one({"google_place_id": {"$exists": True}})
    print("--- Sample venue with google_place_id ---")
    pprint(sample_google_venue)

print("\n=== Schema Analysis ===")
# Check field variations
name_variants = [
    ("name", venues_collection.count_documents({"name": {"$exists": True}})),
    ("venue_name", venues_collection.count_documents({"venue_name": {"$exists": True}}))
]

opening_hours_variants = [
    ("opening_hours (object)", venues_collection.count_documents({"opening_hours": {"$type": "object"}})),
    ("opening_hours (array)", venues_collection.count_documents({"opening_hours": {"$type": "array"}}))
]

print("Name field variants:")
for field, count in name_variants:
    print(f"  {field}: {count}")

print("Opening hours variants:")
for field, count in opening_hours_variants:
    print(f"  {field}: {count}")
