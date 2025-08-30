"""
Test MongoDB connection and manual venue insertion
"""
import pymongo
from datetime import datetime

try:
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["planeet_db"]
    venues_collection = db["venues"]
    
    print("✅ Connected to MongoDB successfully!")
    print(f"Database: {db.name}")
    print(f"Collection: {venues_collection.name}")
    
    # Test manual insertion with new schema
    test_venue = {
        "google_place_id": "test_place_id_123",
        "venue_name": "Test Cafe",
        "venue_type": "cafe",
        "opening_hours": {
            "open_at": "08:00",
            "close_at": "18:00"
        },
        "time_slots": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert test venue
    result = venues_collection.insert_one(test_venue)
    print(f"✅ Test venue inserted with ID: {result.inserted_id}")
    
    # Verify insertion
    count = venues_collection.count_documents({})
    print(f"📊 Total venues in collection: {count}")
    
    # Retrieve and display
    test_doc = venues_collection.find_one({"google_place_id": "test_place_id_123"})
    if test_doc:
        print("📄 Retrieved test document:")
        for key, value in test_doc.items():
            print(f"  {key}: {value}")
    
    # Clean up test document
    venues_collection.delete_one({"google_place_id": "test_place_id_123"})
    print("🧹 Test document cleaned up")
    
except Exception as e:
    print(f"❌ Error: {e}")
