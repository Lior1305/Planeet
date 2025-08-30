"""
Check the correct database that venues service uses
"""
import pymongo

# Connect to MongoDB with both possible database names
client = pymongo.MongoClient("mongodb://localhost:27017/")

print("=== Available Databases ===")
for db_name in client.list_database_names():
    print(f"  {db_name}")

print("\n=== Checking 'planeet' database (venues service) ===")
planeet_db = client["planeet"]
venues_collection = planeet_db["venues"]
venues_count = venues_collection.count_documents({})
print(f"Venues in 'planeet' database: {venues_count}")

if venues_count > 0:
    sample = venues_collection.find_one()
    print("Sample document:")
    for key, value in sample.items():
        print(f"  {key}: {value}")

print("\n=== Checking 'planeet_db' database (our test) ===")
planeet_db_alt = client["planeet_db"]
venues_collection_alt = planeet_db_alt["venues"]
venues_count_alt = venues_collection_alt.count_documents({})
print(f"Venues in 'planeet_db' database: {venues_count_alt}")

print(f"\n=== Testing Manual Insert to 'planeet' database ===")
test_doc = {
    "google_place_id": "manual_test_123",
    "venue_name": "Manual Test Venue",
    "venue_type": "cafe",
    "opening_hours": {"open_at": "09:00", "close_at": "17:00"},
    "time_slots": []
}

try:
    result = venues_collection.insert_one(test_doc)
    print(f"✅ Manual insert successful: {result.inserted_id}")
    
    # Cleanup
    venues_collection.delete_one({"google_place_id": "manual_test_123"})
    print("🧹 Cleaned up test document")
except Exception as e:
    print(f"❌ Manual insert failed: {e}")
