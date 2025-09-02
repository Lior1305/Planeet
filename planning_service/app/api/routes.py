from fastapi import APIRouter, Query, HTTPException, Body
from datetime import datetime
from typing import Dict, Any
import uuid
import logging

from app.models.plan_request import PlanRequest, PlanResponse, PlanConfirmationRequest, ConfirmedPlan, Participant
from app.services.venues_service_client import venues_service_client
from app.services.outing_profile_client import outing_profile_client
from app.services.user_service_client import user_service_client

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage (replace with database in production)
plan_store = {}
plan_requests_store = {}
confirmed_plans_store = {}  # Storage for confirmed plans with participants

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
    """Get a specific plan by ID"""
    plan = plan_store.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.get("/plans", response_model=Dict[str, Any])
async def get_user_plans(user_id: str = Query(...)):
    """Get all plans for a specific user"""
    user_plans = {
        plan_id: plan for plan_id, plan in plan_store.items()
        if plan.get("user_id") == user_id
    }
    
    if not user_plans:
        return {"plans": [], "total": 0}
    
    return {
        "plans": list(user_plans.values()),
        "total": len(user_plans)
    }

@router.post("/plans/{plan_id}/status", response_model=Dict[str, Any])
async def update_plan_status(
    plan_id: str,
    status_update: Dict[str, Any] = Body(...)
):
    """Update plan status (called by Venues Service)"""
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
    
    # Store the complete plan response
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
    Confirm a plan selection and optionally add participants by email.
    This will add the plan to all participants' future outings.
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
            Participant(
                user_id=creator_user_id,
                email=creator_info.get("email", "unknown@email.com"),
                name=creator_info.get("username", "Unknown"),
                status="confirmed",
                confirmed_at=datetime.utcnow()
            )
        ]
        
        # Add invited participants
        for email in confirmation_request.participant_emails:
            # Try to find user by email
            user_info = await user_service_client.get_user_by_email(email)
            
            if user_info:
                participants.append(
                    Participant(
                        user_id=user_info["id"],
                        email=email,
                        name=user_info.get("username", "Unknown"),
                        status="pending"
                    )
                )
            else:
                # User not found - we could still add them as pending with no user_id
                # or skip them with a warning
                logger.warning(f"User with email {email} not found in system")
                continue
        
        # Validate group size
        max_additional = original_request["group_size"] - 1  # minus creator
        if len(confirmation_request.participant_emails) > max_additional:
            raise HTTPException(
                status_code=400, 
                detail=f"Too many participants. Maximum additional participants: {max_additional}"
            )
        
        # Create confirmed plan
        confirmed_plan = ConfirmedPlan(
            plan_id=plan_id,
            selected_plan_index=confirmation_request.selected_plan_index,
            creator_user_id=creator_user_id,
            participants=participants,
            plan_details=selected_plan,
            group_size=len(participants)
        )
        
        # Store confirmed plan
        confirmed_plans_store[plan_id] = confirmed_plan.dict()
        
        # Add to each participant's outing history
        for participant in participants:
            try:
                # Handle date conversion properly
                plan_date = original_request["date"]
                if isinstance(plan_date, str):
                    plan_datetime = datetime.fromisoformat(plan_date)
                else:
                    plan_datetime = plan_date
                
                outing_data = {
                    "user_id": participant.user_id,
                    "plan_id": plan_id,
                    "plan_name": f"Group Outing - {selected_plan.get('name', 'Unknown')}",
                    "outing_date": plan_datetime.isoformat(),
                    "outing_time": plan_datetime.strftime("%H:%M"),
                    "group_size": len(participants),
                    "city": original_request.get("location", {}).get("city", "Unknown"),
                    "venue_types": [vt for vt in original_request["venue_types"]],
                    "selected_plan": selected_plan,
                    "participants": [
                        {
                            "user_id": p.user_id,
                            "email": p.email,
                            "name": p.name,
                            "status": p.status,
                            "invited_at": p.invited_at.isoformat() if hasattr(p, 'invited_at') and p.invited_at else None,
                            "confirmed_at": p.confirmed_at.isoformat() if hasattr(p, 'confirmed_at') and p.confirmed_at else None
                        } for p in participants
                    ],
                    "creator_user_id": creator_user_id,
                    "is_group_outing": True
                }
                
                # Add to participant's outing history
                await outing_profile_client.add_outing_history(outing_data)
                logger.info(f"Added outing to history for user {participant.user_id}")
                
            except Exception as e:
                logger.error(f"Failed to add outing to history for user {participant.user_id}: {e}")
        
        logger.info(f"Successfully confirmed plan {plan_id} with {len(participants)} participants")
        
        return {
            "message": "Plan confirmed successfully",
            "plan_id": plan_id,
            "confirmed_plan": confirmed_plan.dict(),
            "participants_added": len(participants) - 1,  # excluding creator
            "total_participants": len(participants)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to confirm plan: {str(e)}")

@router.get("/plans/{plan_id}/confirmed", response_model=Dict[str, Any])
async def get_confirmed_plan(plan_id: str):
    """Get details of a confirmed plan"""
    confirmed_plan = confirmed_plans_store.get(plan_id)
    if not confirmed_plan:
        raise HTTPException(status_code=404, detail="Confirmed plan not found")
    return confirmed_plan

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
        
        # Get confirmed plan
        confirmed_plan = confirmed_plans_store.get(plan_id)
        if not confirmed_plan:
            raise HTTPException(status_code=404, detail="Confirmed plan not found")
        
        # Find participant
        participants = confirmed_plan.get("participants", [])
        participant_found = False
        
        for participant in participants:
            if participant["user_id"] == user_id:
                participant["status"] = response_status
                if response_status == "confirmed":
                    participant["confirmed_at"] = datetime.utcnow().isoformat()
                participant_found = True
                break
        
        if not participant_found:
            raise HTTPException(status_code=404, detail="User not found in plan participants")
        
        # Update stored plan
        confirmed_plans_store[plan_id] = confirmed_plan
        
        # Handle outing history based on response
        if response_status == "confirmed":
            # Add outing to user's history when they confirm
            try:
                # Get original plan request to build outing data
                original_request = plan_requests_store.get(plan_id, {})
                selected_plan = confirmed_plan.get("plan_details", {})
                
                # Handle date conversion properly
                plan_date = original_request.get("date")
                if isinstance(plan_date, str):
                    plan_datetime = datetime.fromisoformat(plan_date)
                else:
                    plan_datetime = plan_date
                
                outing_data = {
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "plan_name": f"Group Outing - {selected_plan.get('name', 'Unknown')}",
                    "outing_date": plan_datetime.isoformat() if plan_datetime else datetime.utcnow().isoformat(),
                    "outing_time": plan_datetime.strftime("%H:%M") if plan_datetime else "19:00",
                    "group_size": len(participants),
                    "city": original_request.get("location", {}).get("city", "Unknown"),
                    "venue_types": original_request.get("venue_types", []),
                    "selected_plan": selected_plan,
                    "participants": [
                        {
                            "user_id": p.get("user_id"),
                            "email": p.get("email"),
                            "name": p.get("name"),
                            "status": p.get("status"),
                            "invited_at": p.get("invited_at"),
                            "confirmed_at": p.get("confirmed_at")
                        } for p in participants
                    ],
                    "creator_user_id": confirmed_plan.get("creator_user_id"),
                    "is_group_outing": True
                }
                
                await outing_profile_client.add_outing_history(outing_data)
                logger.info(f"Added outing to history for user {user_id} who confirmed invitation")
                
            except Exception as e:
                logger.error(f"Failed to add outing to history for confirming user {user_id}: {e}")
                
        elif response_status == "declined":
            # Update outing status for declined invitation
            try:
                await outing_profile_client.update_outing_status(plan_id, user_id, "cancelled")
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
        "confirmed_plans": len(confirmed_plans_store),
        "dependencies": {
            "users_service": "healthy" if user_service_healthy else "unhealthy"
        }
    }
