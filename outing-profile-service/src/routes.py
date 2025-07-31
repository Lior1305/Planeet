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
    """Get all profiles or a specific profile by user_id"""
    try:
        user_id = request.args.get('user_id')
        profiles_collection = db.get_profiles_collection()
        
        if user_id:
            # Get specific profile by user_id
            profile = profiles_collection.find_one({"user_id": user_id}, {"_id": 0})
            if profile:
                logger.info(f"Retrieved profile for user_id: {user_id}")
                return jsonify(profile), 200
            else:
                logger.warning(f"Profile not found for user_id: {user_id}")
                return jsonify({"error": "Profile not found"}), 404
        else:
            # Get all profiles
            profiles = list(profiles_collection.find({}, {"_id": 0}))
            logger.info(f"Retrieved {len(profiles)} profiles")
            return jsonify(profiles), 200
            
    except Exception as e:
        logger.error(f"Error retrieving profiles: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/profiles', methods=['DELETE'])
def delete_profile():
    """Delete a profile by user_id query parameter"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            logger.warning("Missing user_id query parameter")
            return jsonify({"error": "user_id query parameter is required"}), 400
        
        profiles_collection = db.get_profiles_collection()
        
        # Check if profile exists
        existing_profile = profiles_collection.find_one({"user_id": user_id})
        if not existing_profile:
            logger.warning(f"Profile with user_id {user_id} not found")
            return jsonify({"error": "Profile not found"}), 404
        
        # Delete the profile
        result = profiles_collection.delete_one({"user_id": user_id})
        
        if result.deleted_count > 0:
            logger.info(f"Profile deleted successfully for user_id: {user_id}")
            return jsonify({"message": "Profile deleted successfully"}), 200
        else:
            logger.warning(f"Failed to delete profile for user_id: {user_id}")
            return jsonify({"error": "Failed to delete profile"}), 500
            
    except Exception as e:
        logger.error(f"Error deleting profile: {e}")
        return jsonify({"error": str(e)}), 500 