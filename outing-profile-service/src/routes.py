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
    """Add a new outing to user's profile history with participants support"""
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
        creator_user_id = data.get("creator_user_id") or user_id  # Auto-set if missing
        participants = data.get("participants", [])  # New field for participants
        is_group_outing = data.get("is_group_outing", len(participants) > 1)

        logger.info(f"Attempting to add outing history: {data}")

        if not all([user_id, plan_id, plan_name, outing_date, outing_time, group_size, city]):
            logger.warning("Missing required fields in request")
            return jsonify({"error": "user_id, plan_id, plan_name, outing_date, outing_time, group_size, and city are required"}), 400

        # Create the outing entry with participants
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
            "confirmed": data.get("confirmed", False),  # New field for confirmation status
            "creator_user_id": creator_user_id,  # Track who created the plan
            "participants": participants,  # List of participants
            "is_group_outing": is_group_outing,  # Whether this is a group outing
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

@api.route('/outing-history/<plan_id>/confirm', methods=['PUT'])
def update_outing_confirmation(plan_id):
    """Update the confirmation status of an outing in the user's profile"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        confirmed = data.get("confirmed", True)  # Default to True when confirming
        
        if not user_id:
            logger.warning("Missing user_id in request")
            return jsonify({"error": "user_id is required"}), 400
        
        if not isinstance(confirmed, bool):
            logger.warning(f"Invalid confirmed value: {confirmed}")
            return jsonify({"error": "confirmed must be a boolean"}), 400
        
        profiles_collection = db.get_profiles_collection()
        
        # Update the specific outing's confirmation status in the user's profile
        result = profiles_collection.update_one(
            {"user_id": user_id, "outing_history.plan_id": plan_id},
            {"$set": {"outing_history.$.confirmed": confirmed}}
        )
        
        if result.modified_count > 0:
            status_text = "confirmed" if confirmed else "unconfirmed"
            logger.info(f"Outing confirmation updated to {status_text} for plan_id: {plan_id}")
            return jsonify({
                "message": f"Outing {status_text} successfully",
                "plan_id": plan_id,
                "confirmed": confirmed
            }), 200
        else:
            logger.warning(f"Outing not found for plan_id: {plan_id} and user_id: {user_id}")
            return jsonify({"error": "Outing not found"}), 404
            
    except Exception as e:
        logger.error(f"Error updating outing confirmation: {e}")
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
        
        # Allow ratings for planned and completed outings (users can rate after booking)
        if outing.get("status") not in ["planned", "completed"]:
            logger.warning(f"Cannot rate outing with status '{outing.get('status')}': {plan_id}")
            return jsonify({"error": "Can only rate planned or completed outings"}), 400
        
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

# Enhanced Plan Management Endpoints using existing outing history structure

@api.route('/plans/<plan_id>', methods=['GET'])
def get_plan(plan_id):
    """Get a specific plan by ID from outing history"""
    try:
        profiles_collection = db.get_profiles_collection()
        
        # Find the plan in any user's outing history
        plan_data = profiles_collection.find_one(
            {"outing_history.plan_id": plan_id},
            {"outing_history.$": 1, "_id": 0}
        )
        
        if plan_data and plan_data.get("outing_history"):
            plan = plan_data["outing_history"][0]
            logger.info(f"Retrieved plan: {plan_id}")
            return jsonify(plan), 200
        else:
            logger.warning(f"Plan not found: {plan_id}")
            return jsonify({"error": "Plan not found"}), 404
            
    except Exception as e:
        logger.error(f"Error retrieving plan: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/plans', methods=['GET'])
def get_user_plans():
    """Get all plans for a specific user (as creator or participant)"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            logger.warning("Missing user_id query parameter")
            return jsonify({"error": "user_id query parameter is required"}), 400
        
        profiles_collection = db.get_profiles_collection()
        
        # Find all plans where user is creator or participant
        plans = []
        
        # Find plans where user is creator
        creator_plans = profiles_collection.find(
            {"user_id": user_id, "outing_history.creator_user_id": user_id},
            {"outing_history.$": 1, "_id": 0}
        )
        
        for profile in creator_plans:
            if profile.get("outing_history"):
                plans.extend(profile["outing_history"])
        
        # Find plans where user is participant (but not creator)
        participant_plans = profiles_collection.find(
            {
                "outing_history": {
                    "$elemMatch": {
                        "participants.user_id": user_id,
                        "creator_user_id": {"$ne": user_id}
                    }
                }
            },
            {"outing_history": 1, "_id": 0}
        )
        
        for profile in participant_plans:
            if profile.get("outing_history"):
                for outing in profile["outing_history"]:
                    # Check if user is participant but not creator
                    if (outing.get("creator_user_id") != user_id and 
                        any(p.get("user_id") == user_id for p in outing.get("participants", []))):
                        plans.append(outing)
        
        logger.info(f"Retrieved {len(plans)} plans for user: {user_id}")
        return jsonify({
            "user_id": user_id,
            "plans": plans,
            "total": len(plans)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving user plans: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/plans/<plan_id>/participants', methods=['POST'])
def add_participants_to_plan(plan_id):
    """Add participants to an existing plan"""
    try:
        data = request.get_json()
        new_participants_data = data.get('participants', [])
        
        if not new_participants_data:
            logger.warning("No participants provided")
            return jsonify({"error": "participants are required"}), 400
        
        profiles_collection = db.get_profiles_collection()
        
        # Find the plan in outing history
        plan_profile = profiles_collection.find_one(
            {"outing_history.plan_id": plan_id},
            {"outing_history.$": 1, "_id": 0}
        )
        
        if not plan_profile or not plan_profile.get("outing_history"):
            logger.warning(f"Plan not found: {plan_id}")
            return jsonify({"error": "Plan not found"}), 404
        
        existing_plan = plan_profile["outing_history"][0]
        creator_user_id = existing_plan.get("creator_user_id")
        
        # Get existing participants to avoid duplicates
        existing_participants = existing_plan.get('participants', [])
        existing_user_ids = {p['user_id'] for p in existing_participants}
        
        # Create new participants (only if not already invited)
        new_participants = []
        for p_data in new_participants_data:
            if p_data['user_id'] not in existing_user_ids:
                participant = {
                    "user_id": p_data['user_id'],
                    "email": p_data['email'],
                    "name": p_data['name'],
                    "status": p_data.get('status', 'pending'),
                    "invited_at": datetime.utcnow().isoformat(),
                    "confirmed_at": None
                }
                new_participants.append(participant)
            else:
                logger.warning(f"User {p_data['user_id']} is already a participant in plan {plan_id}")
        
        if not new_participants:
            logger.info("No new participants to add (all were already invited)")
            return jsonify({
                "message": "No new participants added (all were already invited)",
                "plan_id": plan_id,
                "participants_added": 0
            }), 200
        
        # Calculate new group size (total participants)
        total_participants = len(existing_participants) + len(new_participants)
        
        # Update the plan with new participants in ALL profiles that have this plan
        result = profiles_collection.update_many(
            {"outing_history.plan_id": plan_id},
            {
                "$push": {"outing_history.$.participants": {"$each": new_participants}},
                "$set": {
                    "outing_history.$.is_group_outing": True,
                    "outing_history.$.group_size": total_participants
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Added {len(new_participants)} participants to plan: {plan_id}")
            return jsonify({
                "message": f"Added {len(new_participants)} participants successfully",
                "plan_id": plan_id,
                "participants_added": len(new_participants)
            }), 200
        else:
            logger.warning(f"Failed to add participants to plan: {plan_id}")
            return jsonify({"error": "Failed to add participants"}), 500
            
    except Exception as e:
        logger.error(f"Error adding participants: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/plans/<plan_id>/creator-participants', methods=['PUT'])
def update_creator_plan_participants(plan_id):
    """Update the creator's plan with new participants"""
    try:
        data = request.get_json()
        creator_user_id = data.get('creator_user_id')
        new_participants_data = data.get('new_participants', [])
        
        if not creator_user_id:
            logger.warning("Creator user ID is required")
            return jsonify({"error": "creator_user_id is required"}), 400
        
        if not new_participants_data:
            logger.warning("No new participants provided")
            return jsonify({"error": "new_participants are required"}), 400
        
        profiles_collection = db.get_profiles_collection()
        
        # Find the creator's profile with this plan
        creator_profile = profiles_collection.find_one(
            {
                "user_id": creator_user_id,
                "outing_history.plan_id": plan_id
            }
        )
        
        if not creator_profile:
            logger.warning(f"Creator profile not found for user {creator_user_id} with plan {plan_id}")
            return jsonify({"error": "Creator profile not found"}), 404
        
        # Find the specific plan in the creator's outing history
        plan_index = None
        for i, outing in enumerate(creator_profile.get("outing_history", [])):
            if outing.get("plan_id") == plan_id:
                plan_index = i
                break
        
        if plan_index is None:
            logger.warning(f"Plan {plan_id} not found in creator's outing history")
            return jsonify({"error": "Plan not found in creator's outing history"}), 404
        
        # Get existing participants to avoid duplicates
        existing_participants = creator_profile["outing_history"][plan_index].get('participants', [])
        existing_user_ids = {p['user_id'] for p in existing_participants}
        
        # Create new participants (only if not already invited)
        new_participants = []
        for p_data in new_participants_data:
            if p_data['user_id'] not in existing_user_ids:
                participant = {
                    "user_id": p_data['user_id'],
                    "email": p_data['email'],
                    "name": p_data['name'],
                    "status": p_data.get('status', 'pending'),
                    "invited_at": datetime.utcnow().isoformat(),
                    "confirmed_at": None
                }
                new_participants.append(participant)
            else:
                logger.warning(f"User {p_data['user_id']} is already a participant in creator's plan {plan_id}")
        
        if not new_participants:
            logger.info("No new participants to add to creator's plan (all were already invited)")
            return jsonify({
                "message": "No new participants added to creator's plan (all were already invited)",
                "plan_id": plan_id,
                "participants_added": 0
            }), 200
        
        # Get the original group size to preserve it
        original_group_size = creator_profile["outing_history"][plan_index].get('group_size', 2)
        
        # Update the creator's plan with new participants (preserve original group size)
        result = profiles_collection.update_one(
            {
                "user_id": creator_user_id,
                "outing_history.plan_id": plan_id
            },
            {
                "$push": {f"outing_history.{plan_index}.participants": {"$each": new_participants}},
                "$set": {
                    f"outing_history.{plan_index}.is_group_outing": True,
                    f"outing_history.{plan_index}.group_size": original_group_size  # Preserve original group size
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated creator's plan {plan_id} with {len(new_participants)} new participants")
            return jsonify({
                "message": f"Updated creator's plan with {len(new_participants)} new participants successfully",
                "plan_id": plan_id,
                "participants_added": len(new_participants)
            }), 200
        else:
            logger.warning(f"Failed to update creator's plan: {plan_id}")
            return jsonify({"error": "Failed to update creator's plan"}), 500
            
    except Exception as e:
        logger.error(f"Error updating creator's plan participants: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/plans/<plan_id>/participants/<user_id>/respond', methods=['PUT'])
def respond_to_plan_invitation(plan_id, user_id):
    """Allow participants to confirm or decline plan invitation"""
    try:
        data = request.get_json()
        response_status = data.get('status')  # "confirmed" or "declined"
        
        if response_status not in ["confirmed", "declined"]:
            logger.warning(f"Invalid response status: {response_status}")
            return jsonify({"error": "status must be 'confirmed' or 'declined'"}), 400
        
        profiles_collection = db.get_profiles_collection()
        
        # Find the profile with the plan and update the participant status
        # We need to use arrayFilters to update nested array elements
        array_filters = [
            {"plan.plan_id": plan_id},
            {"participant.user_id": user_id}
        ]
        
        update_data = {
            "outing_history.$[plan].participants.$[participant].status": response_status
        }
        
        if response_status == "confirmed":
            update_data["outing_history.$[plan].participants.$[participant].confirmed_at"] = datetime.utcnow().isoformat()
        
        result = profiles_collection.update_many(
            {
                "outing_history.plan_id": plan_id,
                "outing_history.participants.user_id": user_id
            },
            {"$set": update_data},
            array_filters=array_filters
        )
        
        if result.modified_count > 0:
            logger.info(f"User {user_id} {response_status} invitation for plan {plan_id}")
            return jsonify({
                "message": f"Response recorded: {response_status}",
                "plan_id": plan_id,
                "user_id": user_id,
                "status": response_status
            }), 200
        else:
            logger.warning(f"Participant not found in plan: {plan_id}, user: {user_id}")
            return jsonify({"error": "Participant not found in plan"}), 404
            
    except Exception as e:
        logger.error(f"Error responding to invitation: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/plans/<plan_id>/cancel', methods=['POST'])
def cancel_plan_for_everyone(plan_id):
    """Cancel a plan for all participants (creator only)"""
    try:
        data = request.get_json()
        creator_user_id = data.get('creator_user_id')
        
        if not creator_user_id:
            logger.warning("Creator user ID is required")
            return jsonify({"error": "creator_user_id is required"}), 400
        
        profiles_collection = db.get_profiles_collection()
        
        # Find all profiles that have this plan in their outing history
        profiles_with_plan = profiles_collection.find({
            "outing_history.plan_id": plan_id
        })
        
        if not profiles_with_plan:
            logger.warning(f"No profiles found with plan {plan_id}")
            return jsonify({"error": "Plan not found"}), 404
        
        # Update all profiles to set the plan status to 'cancelled'
        result = profiles_collection.update_many(
            {"outing_history.plan_id": plan_id},
            {
                "$set": {
                    "outing_history.$[plan].status": "cancelled"
                }
            },
            array_filters=[{"plan.plan_id": plan_id}]
        )
        
        if result.modified_count > 0:
            logger.info(f"Plan {plan_id} cancelled for {result.modified_count} profiles")
            return jsonify({
                "message": f"Plan cancelled for {result.modified_count} participants",
                "plan_id": plan_id,
                "status": "cancelled",
                "affected_profiles": result.modified_count
            }), 200
        else:
            logger.warning(f"No profiles were updated for plan {plan_id}")
            return jsonify({"error": "Failed to cancel plan"}), 500
            
    except Exception as e:
        logger.error(f"Error cancelling plan for everyone: {e}")
        return jsonify({"error": "Internal server error"}), 500

@api.route('/plans/<plan_id>/delete', methods=['POST'])
def delete_plan_for_everyone(plan_id):
    """Delete a plan for all participants (creator only)"""
    try:
        data = request.get_json()
        creator_user_id = data.get('creator_user_id')
        
        if not creator_user_id:
            logger.warning("Creator user ID is required")
            return jsonify({"error": "creator_user_id is required"}), 400
        
        profiles_collection = db.get_profiles_collection()
        
        # Find all profiles that have this plan in their outing history
        profiles_with_plan = profiles_collection.find({
            "outing_history.plan_id": plan_id
        })
        
        if not profiles_with_plan:
            logger.warning(f"No profiles found with plan {plan_id}")
            return jsonify({"error": "Plan not found"}), 404
        
        # Remove the plan from all profiles' outing history
        result = profiles_collection.update_many(
            {"outing_history.plan_id": plan_id},
            {
                "$pull": {
                    "outing_history": {"plan_id": plan_id}
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Plan {plan_id} deleted from {result.modified_count} profiles")
            return jsonify({
                "message": f"Plan deleted for {result.modified_count} participants",
                "plan_id": plan_id,
                "status": "deleted",
                "affected_profiles": result.modified_count
            }), 200
        else:
            logger.warning(f"No profiles were updated for plan {plan_id}")
            return jsonify({"error": "Failed to delete plan"}), 500
            
    except Exception as e:
        logger.error(f"Error deleting plan for everyone: {e}")
        return jsonify({"error": "Internal server error"}), 500

@api.route('/invitations/pending', methods=['GET'])
def get_pending_invitations():
    """Get pending invitations for a user"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            logger.warning("user_id is required")
            return jsonify({"error": "user_id is required"}), 400
        
        profiles_collection = db.get_profiles_collection()
        
        # Find all profiles that have this user as a pending participant
        profiles_with_invitations = profiles_collection.find({
            "outing_history.participants.user_id": user_id,
            "outing_history.participants.status": "pending"
        })
        
        pending_invitations = []
        seen_plan_ids = set()  # Track seen plan IDs to avoid duplicates
        
        for profile in profiles_with_invitations:
            outing_history = profile.get("outing_history", [])
            
            for outing in outing_history:
                plan_id = outing.get("plan_id")
                
                # Skip if this user is the creator of this plan
                if outing.get("creator_user_id") == user_id:
                    continue
                
                # Skip if we've already processed this plan
                if plan_id in seen_plan_ids:
                    continue
                    
                participants = outing.get("participants", [])
                for participant in participants:
                    if participant.get("user_id") == user_id and participant.get("status") == "pending":
                        # Mark this plan as seen
                        seen_plan_ids.add(plan_id)
                        
                        # Find the creator's profile to get their name
                        creator_user_id = outing.get("creator_user_id")
                        creator_profile = profiles_collection.find_one({"user_id": creator_user_id})
                        creator_name = creator_profile.get("name", "Unknown User") if creator_profile else "Unknown User"
                        
                        invitation = {
                            "id": f"{plan_id}_{user_id}",
                            "plan_id": plan_id,
                            "plan_name": outing.get("plan_name", "Untitled Plan"),
                            "inviter_name": creator_name,  # Show creator's name as inviter
                            "inviter_id": creator_user_id,  # Creator's user ID
                            "invited_at": participant.get("invited_at"),
                            "status": participant.get("status"),
                            "plan_date": outing.get("outing_date"),  # Fixed: was plan_date, should be outing_date
                            "venue_types": outing.get("venue_types", [])
                        }
                        pending_invitations.append(invitation)
                        break  # Found the invitation for this plan, move to next plan
        
        logger.info(f"Found {len(pending_invitations)} pending invitations for user {user_id}")
        logger.info(f"Debug - Profiles found: {profiles_collection.count_documents({'outing_history.participants.user_id': user_id, 'outing_history.participants.status': 'pending'})}")
        return jsonify(pending_invitations), 200
        
    except Exception as e:
        logger.error(f"Error retrieving pending invitations: {e}")
        return jsonify({"error": "Internal server error"}), 500

@api.route('/invitations/<invitation_id>/accept', methods=['PUT'])
def accept_invitation(invitation_id):
    """Accept an invitation"""
    try:
        # Parse invitation_id (format: plan_id_user_id)
        parts = invitation_id.split('_')
        if len(parts) != 2:
            return jsonify({"error": "Invalid invitation ID format"}), 400
        
        plan_id, user_id = parts
        
        profiles_collection = db.get_profiles_collection()
        
        # Update the participant status to confirmed
        array_filters = [
            {"plan.plan_id": plan_id},
            {"participant.user_id": user_id}
        ]
        
        update_data = {
            "outing_history.$[plan].participants.$[participant].status": "confirmed",
            "outing_history.$[plan].participants.$[participant].confirmed_at": datetime.utcnow().isoformat()
        }
        
        result = profiles_collection.update_many(
            {"outing_history.plan_id": plan_id},
            {"$set": update_data},
            array_filters=array_filters
        )
        
        if result.modified_count > 0:
            logger.info(f"User {user_id} accepted invitation for plan {plan_id}")
            return jsonify({
                "message": "Invitation accepted successfully",
                "plan_id": plan_id,
                "user_id": user_id,
                "status": "confirmed"
            }), 200
        else:
            logger.warning(f"No invitation found for user {user_id} in plan {plan_id}")
            return jsonify({"error": "Invitation not found"}), 404
            
    except Exception as e:
        logger.error(f"Error accepting invitation: {e}")
        return jsonify({"error": "Internal server error"}), 500

@api.route('/invitations/<invitation_id>/decline', methods=['PUT'])
def decline_invitation(invitation_id):
    """Decline an invitation"""
    try:
        # Parse invitation_id (format: plan_id_user_id)
        parts = invitation_id.split('_')
        if len(parts) != 2:
            return jsonify({"error": "Invalid invitation ID format"}), 400
        
        plan_id, user_id = parts
        
        profiles_collection = db.get_profiles_collection()
        
        # Update the participant status to declined
        array_filters = [
            {"plan.plan_id": plan_id},
            {"participant.user_id": user_id}
        ]
        
        update_data = {
            "outing_history.$[plan].participants.$[participant].status": "declined"
        }
        
        result = profiles_collection.update_many(
            {"outing_history.plan_id": plan_id},
            {"$set": update_data},
            array_filters=array_filters
        )
        
        if result.modified_count > 0:
            logger.info(f"User {user_id} declined invitation for plan {plan_id}")
            return jsonify({
                "message": "Invitation declined successfully",
                "plan_id": plan_id,
                "user_id": user_id,
                "status": "declined"
            }), 200
        else:
            logger.warning(f"No invitation found for user {user_id} in plan {plan_id}")
            return jsonify({"error": "Invitation not found"}), 404
            
    except Exception as e:
        logger.error(f"Error declining invitation: {e}")
        return jsonify({"error": "Internal server error"}), 500 