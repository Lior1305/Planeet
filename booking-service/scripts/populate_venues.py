#!/usr/bin/env python3
"""
Script to populate the MongoDB database with sample venue data
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, get_venues_collection

def generate_time_slots(start_time: str, end_time: str) -> list:
    """
    Generate time slots in 2-hour intervals from start_time to end_time
    Format: "HH:MM-HH:MM"
    """
    slots = []
    
    # Parse start and end times
    start_hour = int(start_time.split(':')[0])
    end_hour = int(end_time.split(':')[0])
    
    # Generate 2-hour slots
    for hour in range(start_hour, end_hour - 1, 2):
        slot_start = f"{hour:02d}:00"
        slot_end = f"{hour + 2:02d}:00"
        slot = {
            "hours": f"{slot_start}-{slot_end}",
            "counter": 10  # Default 10 available slots per time slot
        }
        slots.append(slot)
    
    return slots

async def populate_venues():
    """Populate the database with sample venues"""
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        venues_collection = get_venues_collection()
        
        # Sample venue data
        sample_venues = [
            {
                "venue_name": "Central Park Restaurant",
                "venue_type": "Restaurant",
                "open_hours": {
                    "start": "10:00",
                    "end": "22:00"
                },
                "time_slots": generate_time_slots("10:00", "22:00")
            },
            {
                "venue_name": "Downtown Cinema",
                "venue_type": "Entertainment",
                "open_hours": {
                    "start": "12:00",
                    "end": "24:00"
                },
                "time_slots": generate_time_slots("12:00", "24:00")
            },
            {
                "venue_name": "Sports Center Gym",
                "venue_type": "Fitness",
                "open_hours": {
                    "start": "06:00",
                    "end": "22:00"
                },
                "time_slots": generate_time_slots("06:00", "22:00")
            },
            {
                "venue_name": "Art Gallery Museum",
                "venue_type": "Cultural",
                "open_hours": {
                    "start": "09:00",
                    "end": "18:00"
                },
                "time_slots": generate_time_slots("09:00", "18:00")
            },
            {
                "venue_name": "Bowling Alley",
                "venue_type": "Entertainment",
                "open_hours": {
                    "start": "11:00",
                    "end": "23:00"
                },
                "time_slots": generate_time_slots("11:00", "23:00")
            }
        ]
        
        # Clear existing venues (optional - comment out if you want to keep existing data)
        # await venues_collection.delete_many({})
        
        # Insert sample venues
        result = await venues_collection.insert_many(sample_venues)
        
        print(f"Successfully inserted {len(result.inserted_ids)} venues:")
        for i, venue_id in enumerate(result.inserted_ids):
            venue = sample_venues[i]
            print(f"  - {venue['venue_name']} (ID: {venue_id})")
            print(f"    Type: {venue['venue_type']}")
            print(f"    Hours: {venue['open_hours']['start']} - {venue['open_hours']['end']}")
            print(f"    Time slots: {len(venue['time_slots'])} slots")
            print()
        
        print("Database population completed successfully!")
        
    except Exception as e:
        print(f"Error populating database: {e}")
    finally:
        # Close connection
        from app.database import close_mongo_connection
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(populate_venues())
