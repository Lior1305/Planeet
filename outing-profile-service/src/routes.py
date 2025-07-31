import logging
from flask import Blueprint, jsonify, request
from .database import db
from .models import Profile

logger = logging.getLogger(__name__)

# Create blueprint for routes
api = Blueprint('api', __name__)

@api.route('/')
def home():
    """Home endpoint"""
    logger.info("Home endpoint was hit")
    return jsonify({"message": "Welcome to Outing Profile Server"})

@api.route('/profiles', methods=['POST'])
def add_profile():
    """Add a new profile"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        name = data.get("name")

        logger.info(f"Attempting to add profile: {data}")

        if not user_id or not name:
            logger.warning("Missing user_id or name in request")
            return jsonify({"error": "user_id and name are required"}), 400

        profile = Profile(user_id=user_id, name=name)
        profiles_collection = db.get_profiles_collection()
        profiles_collection.insert_one(profile.to_dict())

        logger.info(f"Profile added: {profile.to_dict()}")
        return jsonify({"message": "Profile added successfully"}), 201
    except Exception as e:
        logger.error(f"Error adding profile: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/profiles', methods=['GET'])
def get_profiles():
    """Get all profiles"""
    try:
        profiles_collection = db.get_profiles_collection()
        profiles = list(profiles_collection.find({}, {"_id": 0}))
        logger.info(f"Retrieved {len(profiles)} profiles")
        return jsonify(profiles), 200
    except Exception as e:
        logger.error(f"Error retrieving profiles: {e}")
        return jsonify({"error": str(e)}), 500 