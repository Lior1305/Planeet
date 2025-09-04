from fastapi import APIRouter, Query, HTTPException, Body
from datetime import datetime
from typing import Dict, Any
import uuid
import logging

from app.models.plan_request import PlanRequest, PlanResponse, PlanConfirmationRequest, PlanSelectionRequest, PlanInvitationRequest, ConfirmedPlan, Participant
from app.services.venues_service_client import venues_service_client
from app.services.outing_profile_client import outing_profile_client
from app.services.user_service_client import user_service_client

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for temporary plan generation (will be replaced by database storage)
plan_store = {}  # Temporary storage for generated plans before confirmation
plan_requests_store = {}  # Temporary storage for plan requests during generation

@router.get("/")
def home():
    return {"message": "Planning Service Running"}

@router.post("/plans/create", response_model=Dict[str, Any])
async def create_plan(plan_request: PlanRequest):
    """
    Create a new outing plan based on user requirements
    
    This endpoint now orchestrates the full planning process:
    1. Get user preferences from Outing-Profile-Service
    2. Discover venues from Venues Service (Google Places API)
    3. Generate 3 different plans with randomization logic
    """
    try:
        # Generate unique plan ID
        plan_id = str(uuid.uuid4())
        plan_request.plan_id = plan_id
        
        # Store the plan request
        plan_requests_store[plan_id] = plan_request.dict()
        
        logger.info(f"Starting plan creation for plan_id: {plan_id}")
        
        # Step 1: Get user preferences from Outing-Profile-Service
        user_preferences = None
        if plan_request.use_personalization:
            try:
                user_preferences = await outing_profile_client.get_user_preferences(plan_request.user_id)
                logger.info(f"Retrieved user preferences for user {plan_request.user_id}")
            except Exception as e:
                logger.warning(f"Failed to get user preferences: {e}. Continuing without personalization.")
        
        # Step 2: Discover venues from Venues Service
        venue_request = {
            "venue_types": [vt.value for vt in plan_request.venue_types],
            "location": plan_request.location.dict(),
            "radius_km": plan_request.radius_km,
            "user_id": plan_request.user_id,
            "use_personalization": plan_request.use_personalization
        }
        
        logger.info(f"Requesting venue discovery for types: {venue_request['venue_types']}")
        venues_response = await venues_service_client.discover_venues(venue_request)
        
        if not venues_response:
            raise HTTPException(
                status_code=500, 
                detail="Failed to discover venues from Venues Service"
            )
        
        venues_by_type = venues_response.get("venues_by_type", {})
        if not venues_by_type:
            raise HTTPException(
                status_code=404,
                detail="No venues found for the specified criteria"
            )
        
        logger.info(f"Discovered venues for {len(venues_by_type)} venue types")
        
        # Step 3: Apply enhanced personalization based on user rating history
        if plan_request.use_personalization:
            try:
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
        
        # Step 4: Generate multiple plans using our plan generator
        from app.services.plan_generator import plan_generator
        
        plan_response = await plan_generator.generate_multiple_plans(venues_by_type, plan_request)
        
        # Store the complete plan response
        plan_store[plan_id] = plan_response
        
        logger.info(f"Successfully generated {plan_response.get('total_plans_generated', 0)} plans")
        
        return plan_response
            
    except Exception as e:
        import traceback
        error_msg = str(e) if str(e) else "Unknown error"
        trace_msg = traceback.format_exc()
        logger.error(f"Error creating plan: {error_msg}")
        logger.error(f"Full traceback: {trace_msg}")
        # Store failed plan
        plan_store[plan_id] = {
            "plan_id": plan_id,
            "status": "failed",
            "message": f"Plan creation failed: {error_msg}"
        }
        raise HTTPException(status_code=500, detail=f"Plan creation failed: {error_msg}")

@router.get("/plans/{plan_id}", response_model=Dict[str, Any])
async def get_plan(plan_id: str):
    """Get a specific plan by ID from database"""
    # First try to get from database (confirmed plans)
    plan_data = await outing_profile_client.get_plan(plan_id)
    if plan_data:
        return plan_data
    
    # If not found in database, check temporary storage (unconfirmed plans)
    plan = plan_store.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.get("/plans", response_model=Dict[str, Any])
async def get_user_plans(user_id: str = Query(...)):
    """Get all plans for a specific user from database"""
    plans_data = await outing_profile_client.get_user_plans(user_id)
    if not plans_data:
        return {"plans": [], "total": 0}
    
    return plans_data

@router.post("/plans/{plan_id}/status", response_model=Dict[str, Any])
async def update_plan_status(
    plan_id: str,
    status_update: Dict[str, Any] = Body(...)
):
    """Update plan status (called by Venues Service)"""
    # First try to update in database (confirmed plans)
    success = await outing_profile_client.update_plan_status(plan_id, status_update.get("status"))
    if success:
        return {"message": "Plan status updated successfully"}
    
    # If not found in database, update in temporary storage (unconfirmed plans)
    if plan_id not in plan_store:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Update status
    plan_store[plan_id]["status"] = status_update.get("status")
    if "message" in status_update:
        plan_store[plan_id]["message"] = status_update["message"]
    
    return {"message": "Plan status updated successfully"}

@router.post("/plans/{plan_id}/notify", response_model=Dict[str, Any])
async def notify_plan_update(
    plan_id: str,
    notification: Dict[str, Any] = Body(...)
):
    """Receive notifications from Venues Service about plan updates"""
    # First try to update in database (confirmed plans)
    plan_data = await outing_profile_client.get_plan(plan_id)
    if plan_data:
        # For confirmed plans, we could update the database if needed
        # For now, just acknowledge the notification
        return {"message": "Plan notification received"}
    
    # If not found in database, update in temporary storage (unconfirmed plans)
    if plan_id not in plan_store:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Update plan with notification data
    plan_store[plan_id].update(notification)
    
    return {"message": "Plan notification received"}

@router.post("/plans/{plan_id}/response", response_model=Dict[str, Any])
async def receive_plan_response(
    plan_id: str,
    plan_response: Dict[str, Any] = Body(...)
):
    """Receive complete plan response from Venues Service"""
    if plan_id not in plan_requests_store:
        raise HTTPException(status_code=404, detail="Plan request not found")
    
    # Store the complete plan response in temporary storage
    plan_store[plan_id] = plan_response
    
    # TODO: Send to Booking Service and UI
    # This is where you would integrate with your booking service
    # and send notifications to the UI
    
    return {"message": "Plan response received and stored"}

@router.get("/outing-preferences")
async def get_outing_preferences(user_id: str = Query(...)):
    """Get user outing preferences from Outing-Profile-Service"""
    try:
        preferences = await outing_profile_client.get_user_preferences(user_id)
        if preferences:
            return preferences
        else:
            raise HTTPException(status_code=404, detail="Preferences not found")
    except Exception as e:
        logger.error(f"Error fetching preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch preferences")

@router.get("/outing-profile")
async def get_outing_profile(user_id: str = Query(...)):
    """Get user outing profile from Outing-Profile-Service"""
    try:
        profile = await outing_profile_client.get_user_profile(user_id)
        if profile:
            return profile
        else:
            raise HTTPException(status_code=404, detail="Profile not found")
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch profile")


@router.post("/plans/{plan_id}/confirm", response_model=Dict[str, Any])
async def confirm_plan(plan_id: str, confirmation_request: PlanConfirmationRequest):
    """
    Confirm a plan selection and optionally add participants by email (Database-Based).
    This endpoint now stores plans in the outing profile service database.
    
    If no participant_emails are provided, it works like /select (solo plan).
    If participant_emails are provided, it works like /select + /invite (group plan).
    """
    try:
        # Verify the plan exists
        if plan_id not in plan_store:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        if confirmation_request.plan_id != plan_id:
            raise HTTPException(status_code=400, detail="Plan ID mismatch")
        
        plan_data = plan_store[plan_id]
        original_request = plan_requests_store.get(plan_id)
        
        if not original_request:
            raise HTTPException(status_code=404, detail="Original plan request not found")
        
        # Verify the selected plan index is valid
        plans = plan_data.get("plans", [])
        if confirmation_request.selected_plan_index >= len(plans):
            raise HTTPException(status_code=400, detail="Invalid plan index")
        
        selected_plan = plans[confirmation_request.selected_plan_index]
        creator_user_id = original_request["user_id"]
        
        logger.info(f"Confirming plan {plan_id}, selected index: {confirmation_request.selected_plan_index}")
        
        # Get creator's information from users service
        creator_info = await user_service_client.get_user_by_id(creator_user_id)
        
        # Create participants list starting with the creator
        participants = [
            {
                "user_id": creator_user_id,
                "email": creator_info.get("email", "unknown@email.com"),
                "name": creator_info.get("username", "Unknown"),
                "status": "confirmed",
                "confirmed_at": datetime.utcnow().isoformat()
            }
        ]
        
        # Handle date conversion
        plan_date = original_request["date"]
        if isinstance(plan_date, str):
            plan_datetime = datetime.fromisoformat(plan_date)
        else:
            plan_datetime = plan_date
        
        # If no participant emails provided, it's a solo plan
        if not confirmation_request.participant_emails:
            # Solo plan - add to creator's outing history
            outing_data = {
                "user_id": creator_user_id,
                "plan_id": plan_id,
                "plan_name": f"Solo Outing - {selected_plan.get('name', 'Unknown')}",
                "outing_date": plan_datetime.isoformat(),
                "outing_time": plan_datetime.strftime("%H:%M"),
                "group_size": 1,
                "city": original_request.get("location", {}).get("city", "Unknown"),
                "venue_types": [vt.value if hasattr(vt, 'value') else str(vt) for vt in original_request["venue_types"]],
                "selected_plan": selected_plan,
                "creator_user_id": creator_user_id,
                "participants": participants,
                "is_group_outing": False,
                "confirmed": True
            }
            
            # Add to creator's outing history
            success = await outing_profile_client.add_outing_history(outing_data)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to store plan in database")
            
            logger.info(f"Created solo plan in outing history: {plan_id}")
            
            return {
                "message": "Plan confirmed successfully for creator",
                "plan_id": plan_id,
                "plan": outing_data,
                "participants_added": 0,
                "total_participants": 1
            }
        
        else:
            # Group plan - add invited participants
            for email in confirmation_request.participant_emails:
                # Try to find user by email
                user_info = await user_service_client.get_user_by_email(email)
                
                if user_info:
                    participants.append({
                        "user_id": user_info["id"],
                        "email": email,
                        "name": user_info.get("username", "Unknown"),
                        "status": "pending",
                        "invited_at": datetime.utcnow().isoformat()
                    })
                    logger.info(f"Added participant: {email}")
                else:
                    logger.warning(f"User not found for email: {email}")
                    # Continue without this user - don't fail the whole request
                    continue
            
            # Validate group size
            max_additional = original_request["group_size"] - 1  # minus creator
            if len(confirmation_request.participant_emails) > max_additional:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Too many participants. Maximum additional participants: {max_additional}"
                )
            
            # Create group plan - add to each participant's outing history
            for participant in participants:
                try:
                    # Determine if this participant has confirmed (creator = True, others = False)
                    is_confirmed = participant["user_id"] == creator_user_id
                    
                    outing_data = {
                        "user_id": participant["user_id"],
                        "plan_id": plan_id,
                        "plan_name": f"Group Outing - {selected_plan.get('name', 'Unknown')}",
                        "outing_date": plan_datetime.isoformat(),
                        "outing_time": plan_datetime.strftime("%H:%M"),
                        "group_size": len(participants),
                        "city": original_request.get("location", {}).get("city", "Unknown"),
                        "venue_types": [vt.value if hasattr(vt, 'value') else str(vt) for vt in original_request["venue_types"]],
                        "selected_plan": selected_plan,
                        "creator_user_id": creator_user_id,
                        "participants": participants,
                        "is_group_outing": True,
                        "confirmed": is_confirmed  # Creator = True, others = False
                    }
                    
                    # Add to participant's outing history
                    await outing_profile_client.add_outing_history(outing_data)
                    logger.info(f"Added outing to history for user {participant['user_id']}")
                    
                except Exception as e:
                    logger.error(f"Failed to add outing to history for user {participant['user_id']}: {e}")
            
            logger.info(f"Created group plan in outing history: {plan_id} with {len(participants)} participants")
            
            return {
                "message": "Plan confirmed successfully",
                "plan_id": plan_id,
                "plan": {
                    "plan_id": plan_id,
                    "creator_user_id": creator_user_id,
                    "participants": participants,
                    "group_size": len(participants),
                    "is_group_outing": True
                },
                "participants_added": len(participants) - 1,  # excluding creator
                "total_participants": len(participants)
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to confirm plan: {str(e)}")

@router.post("/plans/{plan_id}/select", response_model=Dict[str, Any])
async def select_plan(plan_id: str, selection_request: PlanSelectionRequest):
    """
    Select a plan for the creator only (Step 1: Creator selects their preferred plan)
    This creates a plan in the database with only the creator confirmed.
    """
    try:
        # Verify the plan exists
        if plan_id not in plan_store:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        if selection_request.plan_id != plan_id:
            raise HTTPException(status_code=400, detail="Plan ID mismatch")
        
        plan_data = plan_store[plan_id]
        original_request = plan_requests_store.get(plan_id)
        
        if not original_request:
            raise HTTPException(status_code=404, detail="Original plan request not found")
        
        # Verify the selected plan index is valid
        plans = plan_data.get("plans", [])
        if selection_request.selected_plan_index >= len(plans):
            raise HTTPException(status_code=400, detail="Invalid plan index")
        
        selected_plan = plans[selection_request.selected_plan_index]
        creator_user_id = original_request["user_id"]
        
        logger.info(f"Selecting plan {plan_id}, selected index: {selection_request.selected_plan_index} for creator only")
        
        # Get creator's information from users service
        creator_info = await user_service_client.get_user_by_id(creator_user_id)
        
        # Create participant list with only the creator
        participants = [
            {
                "user_id": creator_user_id,
                "email": creator_info.get("email", "unknown@email.com"),
                "name": creator_info.get("username", "Unknown"),
                "status": "confirmed",
                "confirmed_at": datetime.utcnow().isoformat()
            }
        ]
        
        # Handle date conversion
        plan_date = original_request["date"]
        if isinstance(plan_date, str):
            plan_datetime = datetime.fromisoformat(plan_date)
        else:
            plan_datetime = plan_date
        
        # Add plan to creator's outing history
        outing_data = {
            "user_id": creator_user_id,
            "plan_id": plan_id,
            "plan_name": f"Solo Outing - {selected_plan.get('name', 'Unknown')}",
            "outing_date": plan_datetime.isoformat(),
            "outing_time": plan_datetime.strftime("%H:%M"),
            "group_size": 1,
            "city": original_request.get("location", {}).get("city", "Unknown"),
            "venue_types": [vt.value if hasattr(vt, 'value') else str(vt) for vt in original_request["venue_types"]],
            "selected_plan": selected_plan,
            "creator_user_id": creator_user_id,
            "participants": participants,
            "is_group_outing": False,
            "confirmed": True
        }
        
        # Add to creator's outing history
        success = await outing_profile_client.add_outing_history(outing_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store plan in database")
        
        logger.info(f"Created plan in outing history for creator: {creator_user_id}")
        
        return {
            "message": "Plan selected successfully for creator",
            "plan_id": plan_id,
            "selected_plan_index": selection_request.selected_plan_index,
            "creator_user_id": creator_user_id,
            "plan_details": selected_plan,
            "plan": outing_data,
            "next_step": f"Use POST /plans/{plan_id}/invite to add other participants"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to select plan: {str(e)}")

@router.post("/plans/{plan_id}/invite", response_model=Dict[str, Any])
async def invite_participants(plan_id: str, invitation_request: PlanInvitationRequest):
    """
    Invite participants to an already selected plan (Step 2: Creator invites others)
    This adds the plan to all invited participants' outing history.
    """
    try:
        # Get the existing plan from outing history
        plan_data = await outing_profile_client.get_plan(plan_id)
        if not plan_data:
            raise HTTPException(status_code=404, detail="Plan not found. Please select a plan first.")
        
        creator_user_id = plan_data.get("creator_user_id")
        selected_plan = plan_data.get("selected_plan", {})
        current_participants = plan_data.get("participants", [])
        
        logger.info(f"Inviting participants to plan {plan_id}")
        
        # Add invited participants
        new_participants = []
        for email in invitation_request.participant_emails:
            # Check if already invited
            if any(p.get("email") == email for p in current_participants):
                logger.warning(f"User with email {email} is already invited")
                continue
                
            # Try to find user by email
            user_info = await user_service_client.get_user_by_email(email)
            
            if user_info:
                # Check if this is the creator trying to invite themselves
                if user_info["id"] == creator_user_id:
                    logger.warning(f"Creator {email} cannot invite themselves")
                    continue
                
                new_participant = {
                    "user_id": user_info["id"],
                    "email": email,
                    "name": user_info.get("username", "Unknown"),
                    "status": "pending",
                    "invited_at": datetime.utcnow().isoformat()
                }
                new_participants.append(new_participant)
                current_participants.append(new_participant)
                logger.info(f"Added participant: {email}")
            else:
                logger.warning(f"User not found for email: {email}")
                raise HTTPException(status_code=404, detail=f"User not found for email: {email}")
        
        # Add plan to each NEW participant's outing history (excluding creator)
        for participant in new_participants:
            try:
                # Extract plan details from the stored plan data
                plan_date = plan_data.get("outing_date")
                plan_time = plan_data.get("outing_time")
                
                outing_data = {
                    "user_id": participant["user_id"],
                    "plan_id": plan_id,
                    "plan_name": plan_data.get("plan_name", "Group Outing"),
                    "outing_date": plan_date,
                    "outing_time": plan_time,
                    "group_size": plan_data.get("group_size", len(current_participants)),
                    "city": plan_data.get("city", "Unknown"),
                    "venue_types": plan_data.get("venue_types", []),
                    "selected_plan": selected_plan,
                    "participants": current_participants,
                    "creator_user_id": creator_user_id,
                    "is_group_outing": True,
                    "confirmed": False  # Invited users start as unconfirmed
                }
                
                # Add to participant's outing history
                await outing_profile_client.add_outing_history(outing_data)
                logger.info(f"Added outing to history for invited user {participant['user_id']}")
                
            except Exception as e:
                logger.error(f"Failed to add outing to history for user {participant['user_id']}: {e}")
        
        # Update the creator's existing plan to reflect the new participants
        try:
            # Update the existing plan in the creator's outing history with new participants
            await outing_profile_client.add_participants_to_plan(plan_id, new_participants)
            logger.info(f"Updated creator's outing history to group outing")
            
        except Exception as e:
            logger.error(f"Failed to update creator's outing history: {e}")
        
        logger.info(f"Successfully invited {len(new_participants)} participants to plan {plan_id}")
        
        return {
            "message": "Participants invited successfully",
            "plan_id": plan_id,
            "participants_invited": len(new_participants),
            "total_participants": len(current_participants),
            "plan": {
                "plan_id": plan_id,
                "creator_user_id": creator_user_id,
                "participants": current_participants,
                "group_size": len(current_participants),
                "is_group_outing": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inviting participants: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to invite participants: {str(e)}")

@router.get("/plans/{plan_id}/confirmed", response_model=Dict[str, Any])
async def get_confirmed_plan(plan_id: str):
    """Get details of a confirmed plan from database"""
    plan_data = await outing_profile_client.get_plan(plan_id)
    if not plan_data:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan_data

@router.post("/plans/{plan_id}/participants/{user_id}/respond", response_model=Dict[str, Any])
async def respond_to_plan_invitation(
    plan_id: str, 
    user_id: str, 
    response_data: Dict[str, Any] = Body(...)
):
    """Allow invited users to confirm or decline participation"""
    try:
        response_status = response_data.get("status")  # "confirmed" or "declined"
        
        if response_status not in ["confirmed", "declined"]:
            raise HTTPException(status_code=400, detail="Status must be 'confirmed' or 'declined'")
        
        # Use the outing profile client to respond to invitation
        success = await outing_profile_client.respond_to_plan_invitation(plan_id, user_id, response_status)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update invitation response")
        
        # Handle outing history based on response
        if response_status == "confirmed":
            # Update confirmation status for this user (the outing should already be in their history)
            try:
                await outing_profile_client.update_outing_confirmation(plan_id, user_id, confirmed=True)
                logger.info(f"Updated outing confirmation to True for user {user_id}")
                
            except Exception as e:
                logger.error(f"Failed to update outing confirmation for user {user_id}: {e}")
                
        elif response_status == "declined":
            # Update outing status and confirmation for declined invitation
            try:
                await outing_profile_client.update_outing_status(plan_id, user_id, "cancelled")
                await outing_profile_client.update_outing_confirmation(plan_id, user_id, confirmed=False)
                logger.info(f"Updated outing to cancelled for user {user_id} who declined")
            except Exception as e:
                logger.warning(f"Failed to update outing status for declined invitation: {e}")
        
        logger.info(f"User {user_id} {response_status} invitation for plan {plan_id}")
        
        return {
            "message": f"Response recorded: {response_status}",
            "plan_id": plan_id,
            "user_id": user_id,
            "status": response_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error responding to plan invitation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to respond to invitation: {str(e)}")



@router.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check dependency services
    user_service_healthy = await user_service_client.health_check()
    
    return {
        "status": "healthy",
        "service": "Planning Service",
        "timestamp": datetime.utcnow().isoformat(),
        "active_plans": len(plan_store),
        "pending_requests": len(plan_requests_store),
        "dependencies": {
            "users_service": "healthy" if user_service_healthy else "unhealthy"
        }
    }
