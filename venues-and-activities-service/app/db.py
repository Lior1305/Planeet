"""
Database configuration and connection management for MongoDB.
"""

from typing import Dict, Any
import os
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import logging

logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/planeet")
client: MongoClient = None
db: Database = None

# Collections
venues_collection: Collection = None
time_slots_collection: Collection = None

def connect_to_mongodb():
    """Initialize MongoDB connection and collections"""
    global client, db, venues_collection, time_slots_collection
    
    try:
        client = MongoClient(MONGO_URI)
        db = client.planeet
        
        # Initialize collections
        venues_collection = db.venues
        time_slots_collection = db.time_slots
        
        # Create indexes for better performance
        venues_collection.create_index([("name", 1)])
        venues_collection.create_index([("venue_type", 1)])
        venues_collection.create_index([("location.city", 1)])
        venues_collection.create_index([("rating", -1)])
        
        time_slots_collection.create_index([("venue_id", 1)])
        time_slots_collection.create_index([("date", 1)])
        time_slots_collection.create_index([("start_time", 1)])
        
        logger.info("Successfully connected to MongoDB")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

def get_venues_collection() -> Collection:
    """Get venues collection"""
    if venues_collection is None:
        connect_to_mongodb()
    return venues_collection

def get_time_slots_collection() -> Collection:
    """Get time_slots collection"""
    if time_slots_collection is None:
        connect_to_mongodb()
    return time_slots_collection

def close_connection():
    """Close MongoDB connection"""
    if client:
        client.close()
        logger.info("MongoDB connection closed")

# Initialize connection on module import
try:
    connect_to_mongodb()
except Exception as e:
    logger.warning(f"Could not connect to MongoDB on startup: {e}")
