import os
import logging
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
        self.client = None
        self.db = None
        self.profiles_collection = None
    
    def connect(self):
        """Initialize database connection"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client.outing_profiles
            self.profiles_collection = self.db.profiles
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def get_profiles_collection(self):
        """Get the profiles collection"""
        return self.profiles_collection

# Global database instance
db = Database() 