import logging
from flask import Blueprint, jsonify, request
from .database import db
from .models import Profile
from datetime import datetime
import os

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
        
        # Debug timezone info
        logger.info(f"Server timezone: {os.environ.get('TZ', 'Not set')}")
        logger.info(f"Current server time: {datetime.now()}")
        logger.info(f"Current server time (naive): {datetime.now().replace(tzinfo=None)}")
        
        # Separate into future and past outings
        today = datetime.now().date()
        
        future_outings = []
        past_outings = []
        
        # Check if any outings need status updates
        outings_to_update = []
        
        for outing in outing_history:
            try:
                outing_date = datetime.fromisoformat(outing["outing_date"]).date()
                outing_time = outing.get("outing_time", "00:00")
                
                # Create full datetime for comparison
                # Convert outing time to UTC for comparison (assuming outing time is in Israel time UTC+3)
                outing_datetime = datetime.combine(outing_date, datetime.strptime(outing_time, "%H:%M").time())
                # Subtract 3 hours to convert from Israel time to UTC
                outing_datetime_utc = outing_datetime.replace(hour=(outing_datetime.hour - 3) % 24)
                if outing_datetime.hour < 3:  # Day rolled back
                    outing_datetime_utc = outing_datetime_utc.replace(day=outing_datetime.day - 1)
                
                current_datetime = datetime.now().replace(tzinfo=None)
                
                # Debug logging
                logger.info(f"Outing {outing.get('plan_id', 'unknown')}: Date={outing['outing_date']}, Time={outing_time}")
                logger.info(f"Outing datetime (local): {outing_datetime}")
                logger.info(f"Outing datetime (UTC): {outing_datetime_utc}")
                logger.info(f"Current datetime (UTC): {current_datetime}")
                logger.info(f"Outing < Current: {outing_datetime_utc < current_datetime}")
                logger.info(f"Status: {outing.get('status', 'unknown')}")
                
                if outing_datetime_utc < current_datetime and outing.get("status") == "planned":
                    # Outing has passed but still marked as planned - mark for update
                    outings_to_update.append(outing["plan_id"])
                    # Mark as completed for this response
                    outing["status"] = "completed"
                
                if outing_datetime_utc > current_datetime:
                    future_outings.append(outing)
                else:
                    past_outings.append(outing)
            except:
                # If date parsing fails, treat as past outing
                past_outings.append(outing)
        
        # Update the status of outings that have passed (in background)
        if outings_to_update:
            try:
                for plan_id in outings_to_update:
                    profiles_collection.update_one(
                        {"user_id": user_id, "outing_history.plan_id": plan_id},
                        {"$set": {"outing_history.$.status": "completed"}}
                    )
                logger.info(f"Updated {len(outings_to_update)} outings to completed status for user_id: {user_id}")
            except Exception as e:
                logger.warning(f"Failed to update outing statuses: {e}")
        
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

@api.route('/outing-history/<plan_id>', methods=['DELETE'])
def delete_outing(plan_id):
    """Delete an outing from the user's profile"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        
        if not user_id:
            logger.warning("Missing user_id in request")
            return jsonify({"error": "user_id is required"}), 400
        
        profiles_collection = db.get_profiles_collection()
        
        # Remove the specific outing from the user's profile
        result = profiles_collection.update_one(
            {"user_id": user_id},
            {"$pull": {"outing_history": {"plan_id": plan_id}}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Outing deleted for plan_id: {plan_id} and user_id: {user_id}")
            return jsonify({"message": "Outing deleted successfully"}), 200
        else:
            logger.warning(f"Outing not found for plan_id: {plan_id} and user_id: {user_id}")
            return jsonify({"error": "Outing not found"}), 404
            
    except Exception as e:
        logger.error(f"Error deleting outing: {e}")
        return jsonify({"error": str(e)}), 500 

@api.route('/outing-history/update-expired', methods=['POST'])
def update_expired_outings():
    """Update all expired outings across all users (admin/maintenance endpoint)"""
    try:
        profiles_collection = db.get_profiles_collection()
        current_datetime = datetime.now().replace(tzinfo=None)
        
        # Find all profiles with outing history
        profiles = profiles_collection.find({"outing_history": {"$exists": True, "$ne": []}})
        
        total_updated = 0
        
        for profile in profiles:
            user_id = profile["user_id"]
            outing_history = profile.get("outing_history", [])
            outings_to_update = []
            
            for outing in outing_history:
                try:
                    if outing.get("status") == "planned":
                        outing_date = datetime.fromisoformat(outing["outing_date"]).date()
                        outing_time = outing.get("outing_time", "00:00")
                        outing_datetime = datetime.combine(outing_date, datetime.strptime(outing_time, "%H:%M").time())
                        
                        if outing_datetime < current_datetime:
                            outings_to_update.append(outing["plan_id"])
                except:
                    continue
            
            # Update expired outings for this user
            if outings_to_update:
                for plan_id in outings_to_update:
                    result = profiles_collection.update_one(
                        {"user_id": user_id, "outing_history.plan_id": plan_id},
                        {"$set": {"outing_history.$.status": "completed"}}
                    )
                    if result.modified_count > 0:
                        total_updated += 1
        
        logger.info(f"Updated {total_updated} expired outings across all users")
        return jsonify({
            "message": f"Updated {total_updated} expired outings",
            "total_updated": total_updated
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating expired outings: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/outing-history/<plan_id>/ratings', methods=['POST'])
def add_outing_ratings(plan_id):
    """Add ratings for venues in a past outing"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        venue_ratings = data.get("venue_ratings", [])
        
        if not user_id:
            logger.warning("Missing user_id in request")
            return jsonify({"error": "user_id is required"}), 400
        
        if not venue_ratings:
            logger.warning("Missing venue_ratings in request")
            return jsonify({"error": "venue_ratings is required"}), 400
        
        # Validate venue ratings
        for rating in venue_ratings:
            venue_id = rating.get("venue_id")
            rating_value = rating.get("rating")
            
            if not venue_id:
                logger.warning("Missing venue_id in venue rating")
                return jsonify({"error": "venue_id is required for each rating"}), 400
            
            if not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5:
                logger.warning(f"Invalid rating value: {rating_value}")
                return jsonify({"error": "rating must be an integer between 1 and 5"}), 400
        
        profiles_collection = db.get_profiles_collection()
        
        # Check if the outing exists and is a past outing
        profile = profiles_collection.find_one(
            {"user_id": user_id, "outing_history.plan_id": plan_id},
            {"outing_history.$": 1}
        )
        
        if not profile:
            logger.warning(f"Outing not found for plan_id: {plan_id} and user_id: {user_id}")
            return jsonify({"error": "Outing not found"}), 404
        
        outing = profile["outing_history"][0]
        
        # Check if outing is in the past
        try:
            outing_date = datetime.fromisoformat(outing["outing_date"]).date()
            outing_time = outing.get("outing_time", "00:00")
            outing_datetime = datetime.combine(outing_date, datetime.strptime(outing_time, "%H:%M").time())
            current_datetime = datetime.now().replace(tzinfo=None)
            
            if outing_datetime >= current_datetime:
                logger.warning(f"Cannot rate future outing: {plan_id}")
                return jsonify({"error": "Cannot rate future outings"}), 400
        except:
            logger.warning(f"Invalid outing date format for plan_id: {plan_id}")
            return jsonify({"error": "Invalid outing date format"}), 400
        
        # Add ratings to the outing
        result = profiles_collection.update_one(
            {"user_id": user_id, "outing_history.plan_id": plan_id},
            {"$set": {"outing_history.$.venue_ratings": venue_ratings}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Ratings added for outing plan_id: {plan_id}, user_id: {user_id}")
            return jsonify({
                "message": "Ratings added successfully",
                "plan_id": plan_id,
                "venue_ratings": venue_ratings
            }), 200
        else:
            logger.warning(f"Failed to add ratings for plan_id: {plan_id}")
            return jsonify({"error": "Failed to add ratings"}), 500
            
    except Exception as e:
        logger.error(f"Error adding outing ratings: {e}")
        return jsonify({"error": str(e)}), 500 