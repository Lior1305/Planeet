"""
Check for recently added venues with new schema
"""
import pymongo
from datetime import datetime, timedelta

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["planeet"]
venues_collection = db["venues"]

print("=== Recent Venues Analysis ===")

# Check for venues added in the last hour
one_hour_ago = datetime.utcnow() - timedelta(hours=1)
recent_venues = list(venues_collection.find({"created_at": {"$gte": one_hour_ago}}).sort("created_at", -1))

print(f"Venues added in the last hour: {len(recent_venues)}")

for i, venue in enumerate(recent_venues[:3], 1):
    print(f"\n--- Recent Venue {i} ---")
    print(f"ID: {venue.get('_id')}")
    print(f"Name: {venue.get('name', venue.get('venue_name', 'Unknown'))}")
    print(f"Type: {venue.get('venue_type')}")
    print(f"Created: {venue.get('created_at')}")
    print(f"Google place_id: {venue.get('google_place_id', 'Not found')}")
    print(f"Opening hours: {venue.get('opening_hours')}")
    print(f"Has venue_name field: {'venue_name' in venue}")

print("\n=== Schema Comparison ===")
old_schema_count = venues_collection.count_documents({"name": {"$exists": True}, "venue_name": {"$exists": False}})
new_schema_count = venues_collection.count_documents({"venue_name": {"$exists": True}})
google_place_id_count = venues_collection.count_documents({"google_place_id": {"$exists": True}})

print(f"Old schema venues (has 'name', no 'venue_name'): {old_schema_count}")
print(f"New schema venues (has 'venue_name'): {new_schema_count}")
print(f"Venues with google_place_id: {google_place_id_count}")

if new_schema_count > 0:
    print("\n--- Sample New Schema Venue ---")
    new_venue = venues_collection.find_one({"venue_name": {"$exists": True}})
    for key, value in new_venue.items():
        print(f"  {key}: {value}")
