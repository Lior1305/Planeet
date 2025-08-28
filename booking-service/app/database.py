from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os

# MongoDB connection settings
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "Planeet")

# Async client for FastAPI
async_client = None

async def connect_to_mongo():
    """Connect to MongoDB"""
    global async_client
    async_client = AsyncIOMotorClient(MONGO_URL)
    print(f"Connected to MongoDB: {MONGO_URL}")
    return async_client

async def close_mongo_connection():
    """Close MongoDB connection"""
    global async_client
    if async_client:
        async_client.close()
        print("MongoDB connection closed")

def get_database():
    """Get database instance"""
    if async_client:
        return async_client[DATABASE_NAME]
    raise Exception("Database not connected")

def get_venues_collection():
    """Get venues collection"""
    db = get_database()
    return db.venues
