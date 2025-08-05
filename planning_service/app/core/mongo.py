from pymongo import MongoClient
from app.core.config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["places_db"]

def get_mongo_collection():
    return db["ontopo_links"]
