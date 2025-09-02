"""
Planning Service API Routes - Database-First Architecture
"""

import logging
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from app.models.plan_request import PlanRequest
from app.services.venues_client import venues_client
from app.services.user_service_client import user_service_client
from app.services.outing_profile_client import outing_profile_client

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
def home():
    return {"message": "Planning Service Running"}

@router.post("/plans/create", response_model=Dict[str, Any])
async def create_plan(plan_request: PlanRequest):
    """
    Create a new outing plan by coordinating with Venues Service
    This is a database-first approach that doesn't store plans in memory
    """
    try:
        logger.info(f"Creating plan for user {plan_request.user_id}")
        
        # Step 1: Get user preferences from Outing-Profile-Service
        user_preferences = None
        try:
            user_preferences = await outing_profile_client.get_user_preferences(plan_request.user_id)
            logger.info(f"Retrieved preferences for user {plan_request.user_id}")
        except Exception as e:
            logger.warning(f"Failed to get user preferences: {e}. Continuing without personalization.")
        
        # Step 2: Get user profile information
        user_profile = None
        try:
            user_profile = await outing_profile_client.get_user_profile(plan_request.user_id)
            logger.info(f"Retrieved profile for user {plan_request.user_id}")
        except Exception as e:
            logger.warning(f"Failed to get user profile: {e}. Continuing without profile data.")
        
        # Step 3: Send plan request to Venues Service
        venues_response = await venues_client.create_plan(plan_request)
        
        if not venues_response or venues_response.get("status") != "completed":
            raise HTTPException(status_code=500, detail="Failed to generate plans from Venues Service")
        
        # Step 4: Apply personalization if user preferences are available
        if user_preferences and venues_response.get("plans"):
            try:
                # Get venues by type for personalization
                venues_by_type = {}
                for plan in venues_response["plans"]:
                    for venue in plan.get("suggested_venues", []):
                        venue_type = venue.get("venue_type")
                        if venue_type not in venues_by_type:
                            venues_by_type[venue_type] = []
                        venues_by_type[venue_type].append(venue)
                
                # Get user's venue rating history for personalization
                user_rating_history = await outing_profile_client.get_user_venue_ratings(plan_request.user_id)
                logger.info(f"Retrieved rating history for {len(user_rating_history)} venues")
                
                if user_rating_history or user_preferences:
                    from app.services.personalization import planning_personalization_service
                    
                    # Apply personalization to venues
                    personalized_venues = planning_personalization_service.personalize_venues(
                        venues_by_type, user_rating_history, user_preferences
                    )
                    
                    # Convert back to list format for plan generation (take top 10 per type)
                    for venue_type in venues_by_type:
                        if venue_type in personalized_venues:
                            # Take top 10 personalized venues per type
                            venues_by_type[venue_type] = [
                                venue for venue, score in personalized_venues[venue_type][:10]
                            ]
                    
                    logger.info("Applied enhanced personalization with user rating history")
                else:
                    logger.info("No user rating history or preferences available, skipping personalization")
                    
            except Exception as e:
                logger.warning(f"Failed to apply personalization: {e}. Continuing with original venues.")
        
        # Step 5: Return the generated plans directly (no storage needed)
        logger.info(f"Successfully generated {venues_response.get('total_plans_generated', 0)} plans for user {plan_request.user_id}")
        
        return venues_response
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e) if str(e) else "Unknown error"
        trace_msg = traceback.format_exc()
        logger.error(f"Error creating plan: {error_msg}")
        logger.error(f"Full traceback: {trace_msg}")
        # No storage needed for failed plans
        raise HTTPException(status_code=500, detail=f"Plan creation failed: {error_msg}")

@router.post("/plans/select", response_model=Dict[str, Any])
async def select_plan_direct(selection_request: Dict[str, Any]):
    """
    Select a plan and add it directly to outing history
    This is a database-first approach that doesn't rely on in-memory storage
    """
    try:
        plan_id = selection_request.get("plan_id")
        selected_plan = selection_request.get("selected_plan")
        user_id = selection_request.get("user_id")
        original_plan_request = selection_request.get("original_plan_request")
        
        if not all([plan_id, selected_plan, user_id]):
            raise HTTPException(status_code=400, detail="Missing required fields: plan_id, selected_plan, user_id")
        
        logger.info(f"Selecting plan {plan_id} for user {user_id}")
        
        # Get creator's information from users service
        creator_info = await user_service_client.get_user_by_id(user_id)
        
        # Extract date and time from original plan request
        plan_date = original_plan_request.get("date") if original_plan_request else selection_request.get("outing_date")
        plan_time = original_plan_request.get("time") if original_plan_request else selection_request.get("outing_time")
        group_size = original_plan_request.get("group_size") if original_plan_request else selection_request.get("group_size", 2)
        city = original_plan_request.get("location", {}).get("city") if original_plan_request else selection_request.get("city", "Unknown")
        
        # Parse the date properly
        if plan_date:
            if isinstance(plan_date, str):
                try:
                    # Parse ISO format date
                    plan_datetime = datetime.fromisoformat(plan_date.replace('Z', '+00:00'))
                    outing_date = plan_datetime.date().isoformat()
                    outing_time = plan_datetime.time().strftime("%H:%M")
                except:
                    # Fallback to current date/time
                    outing_date = datetime.utcnow().date().isoformat()
                    outing_time = "18:00"
            else:
                outing_date = plan_date.date().isoformat()
                outing_time = plan_date.time().strftime("%H:%M")
        else:
            outing_date = datetime.utcnow().date().isoformat()
            outing_time = plan_time or "18:00"
        
        # Create outing data for the creator
        outing_data = {
            "user_id": user_id,
            "plan_id": plan_id,
            "plan_name": selected_plan.get("name", "Outing Plan"),
            "outing_date": outing_date,
            "outing_time": outing_time,
            "group_size": group_size,
            "city": city,
            "venue_types": [venue.get("venue_type") for venue in selected_plan.get("suggested_venues", [])],
            "selected_plan": selected_plan,
            "creator_user_id": user_id,
            "confirmed": True,
            "status": "planned"
        }
        
        # Add to creator's outing history
        logger.info(f"Adding outing to history with data: {outing_data}")
        try:
            result = await outing_profile_client.add_outing_history(outing_data)
            logger.info(f"Outing profile service response: {result}")
            if not result:
                raise HTTPException(status_code=500, detail="Failed to save plan to outing history")
        except Exception as e:
            logger.error(f"Failed to add outing to history: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save plan to history: {str(e)}")
        
        logger.info(f"Successfully selected plan {plan_id} for user {user_id} on {outing_date} at {outing_time}")
        
        return {
            "message": "Plan selected successfully",
            "plan_id": plan_id,
            "status": "confirmed",
            "outing_date": outing_date,
            "outing_time": outing_time
        }
        
    except Exception as e:
        logger.error(f"Error selecting plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to select plan: {str(e)}")

@router.post("/plans/{plan_id}/invite", response_model=Dict[str, Any])
async def invite_participants(plan_id: str, invite_request: Dict[str, Any]):
    """
    Invite participants to a plan
    This is a database-first approach that queries the database directly
    """
    try:
        participant_emails = invite_request.get("participant_emails", [])
        
        if not participant_emails:
            raise HTTPException(status_code=400, detail="No participant emails provided")
        
        logger.info(f"Inviting {len(participant_emails)} participants to plan {plan_id}")
        
        # Get the plan from the database
        outing_data = await outing_profile_client.get_outing_by_plan_id(plan_id)
        if not outing_data:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Get creator information
        creator_id = outing_data.get("creator_user_id")
        if not creator_id:
            raise HTTPException(status_code=400, detail="Creator information not found")
        
        creator_info = await user_service_client.get_user_by_id(creator_id)
        if not creator_info:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        # Check group size limit
        group_size = outing_data.get("group_size", 2)
        current_participants = 1  # Creator is already a participant
        max_invites = group_size - current_participants
        
        if len(participant_emails) > max_invites:
            raise HTTPException(
                status_code=400, 
                detail=f"Too many invites. Group size is {group_size}, can only invite {max_invites} more people."
            )
        
        # Get user IDs for the invited emails
        invited_users = []
        for email in participant_emails:
            user_info = await user_service_client.get_user_by_email(email)
            if user_info:
                invited_users.append(user_info)
            else:
                logger.warning(f"User with email {email} not found")
        
        if not invited_users:
            raise HTTPException(status_code=404, detail="No valid users found for the provided emails")
        
        # Create outing entries for invited users
        for user in invited_users:
            invite_outing_data = {
                "user_id": user["id"],
                "plan_id": plan_id,
                "plan_name": outing_data.get("plan_name", "Outing Plan"),
                "outing_date": outing_data.get("outing_date"),
                "outing_time": outing_data.get("outing_time"),
                "group_size": group_size,
                "city": outing_data.get("city"),
                "venue_types": outing_data.get("venue_types", []),
                "selected_plan": outing_data.get("selected_plan"),
                "creator_user_id": creator_id,
                "confirmed": False,
                "status": "invited"
            }
            
            # Add to invited user's outing history
            await outing_profile_client.add_outing_history(invite_outing_data)
            logger.info(f"Added invitation for user {user['id']} to plan {plan_id}")
        
        logger.info(f"Successfully invited {len(invited_users)} participants to plan {plan_id}")
        
        return {
            "message": f"Successfully invited {len(invited_users)} participants",
            "plan_id": plan_id,
            "invited_count": len(invited_users),
            "invited_users": [{"id": user["id"], "email": user.get("email")} for user in invited_users]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inviting participants: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to invite participants: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "planning-service"}
