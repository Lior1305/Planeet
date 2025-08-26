import logging
from flask import Blueprint, jsonify, request
from .database import db
from .models import Profile
from datetime import datetime

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

# Updated endpoints for outing history stored within profiles

@api.route('/outing-history', methods=['POST'])
def add_outing_history():
    """Add a new outing to user's profile history"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        plan_id = data.get("plan_id")
        plan_name = data.get("plan_name")
        outing_date = data.get("outing_date")
        outing_time = data.get("outing_time")
        group_size = data.get("group_size")
        city = data.get("city")
        venue_types = data.get("venue_types", [])
        selected_plan = data.get("selected_plan", {})

        logger.info(f"Attempting to add outing history: {data}")

        if not all([user_id, plan_id, plan_name, outing_date, outing_time, group_size, city]):
            logger.warning("Missing required fields in request")
            return jsonify({"error": "user_id, plan_id, plan_name, outing_date, outing_time, group_size, and city are required"}), 400

        # Create the outing entry
        outing_entry = {
            "plan_id": plan_id,
            "plan_name": plan_name,
            "outing_date": outing_date,
            "outing_time": outing_time,
            "group_size": group_size,
            "city": city,
            "venue_types": venue_types,
            "selected_plan": selected_plan,
            "status": "planned",
            "created_at": datetime.utcnow().isoformat()
        }
        
        profiles_collection = db.get_profiles_collection()
        
        # Add the outing to the user's profile
        result = profiles_collection.update_one(
            {"user_id": user_id},
            {"$push": {"outing_history": outing_entry}},
            upsert=True  # Create profile if it doesn't exist
        )
        
        if result.modified_count > 0 or result.upserted_id:
            logger.info(f"Outing history added to profile for user_id: {user_id}")
            return jsonify({
                "message": "Outing added to history successfully",
                "status": "planned"
            }), 201
        else:
            logger.warning(f"Failed to add outing history for user_id: {user_id}")
            return jsonify({"error": "Failed to add outing history"}), 500
        
    except Exception as e:
        logger.error(f"Error adding outing history: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/outing-history', methods=['GET'])
def get_outing_history():
    """Get outing history for a specific user from their profile"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            logger.warning("Missing user_id query parameter")
            return jsonify({"error": "user_id query parameter is required"}), 400
        
        profiles_collection = db.get_profiles_collection()
        
        # Get the user's profile with outing history
        profile = profiles_collection.find_one(
            {"user_id": user_id}, 
            {"_id": 0, "outing_history": 1}
        )
        
        if not profile:
            logger.warning(f"Profile not found for user_id: {user_id}")
            return jsonify({
                "user_id": user_id,
                "future_outings": [],
                "past_outings": [],
                "total_outings": 0
            }), 200
        
        outing_history = profile.get("outing_history", [])
        logger.info(f"Retrieved {len(outing_history)} outings for user_id: {user_id}")
        
        # Separate into future and past outings
        today = datetime.now().date()
        
        future_outings = []
        past_outings = []
        
        for outing in outing_history:
            try:
                outing_date = datetime.fromisoformat(outing["outing_date"]).date()
                if outing_date >= today:
                    future_outings.append(outing)
                else:
                    past_outings.append(outing)
            except:
                # If date parsing fails, treat as past outing
                past_outings.append(outing)
        
        return jsonify({
            "user_id": user_id,
            "future_outings": future_outings,
            "past_outings": past_outings,
            "total_outings": len(outing_history)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving outing history: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/outing-history/<plan_id>', methods=['PUT'])
def update_outing_status(plan_id):
    """Update the status of an outing in the user's profile"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        new_status = data.get("status")
        
        if not user_id or not new_status:
            logger.warning("Missing user_id or status in request")
            return jsonify({"error": "user_id and status are required"}), 400
        
        if new_status not in ["planned", "completed", "cancelled"]:
            logger.warning(f"Invalid status: {new_status}")
            return jsonify({"error": "status must be one of: planned, completed, cancelled"}), 400
        
        profiles_collection = db.get_profiles_collection()
        
        # Update the specific outing's status in the user's profile
        result = profiles_collection.update_one(
            {"user_id": user_id, "outing_history.plan_id": plan_id},
            {"$set": {"outing_history.$.status": new_status}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Outing status updated to {new_status} for plan_id: {plan_id}")
            return jsonify({"message": "Outing status updated successfully"}), 200
        else:
            logger.warning(f"Outing not found for plan_id: {plan_id} and user_id: {user_id}")
            return jsonify({"error": "Outing not found"}), 404
            
    except Exception as e:
        logger.error(f"Error updating outing status: {e}")
        return jsonify({"error": str(e)}), 500 