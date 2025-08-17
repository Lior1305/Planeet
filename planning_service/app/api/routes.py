from fastapi import APIRouter, Query, HTTPException, Body
from datetime import datetime
from typing import Dict, Any
import uuid
import logging

from app.models.plan_request import PlanRequest, PlanResponse
from app.services.venues_service_client import venues_service_client
from app.services.outing_profile_client import outing_profile_client

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage (replace with database in production)
plan_store = {}
plan_requests_store = {}

@router.get("/")
def home():
    return {"message": "Planning Service Running"}

@router.post("/plans/create", response_model=Dict[str, Any])
async def create_plan(plan_request: PlanRequest):
    """
    Create a new outing plan based on user requirements
    
    This endpoint receives user input and creates a plan request that will be
    sent to the Venues Service for venue discovery and planning.
    """
    try:
        # Generate unique plan ID
        plan_id = str(uuid.uuid4())
        plan_request.plan_id = plan_id
        
        # Store the plan request
        plan_requests_store[plan_id] = plan_request.dict()
        
        # Send to Venues Service for plan generation
        venues_plan_response = await venues_service_client.generate_venue_plan(plan_request.dict())
        
        if venues_plan_response:
            # Store the complete plan
            plan_store[plan_id] = venues_plan_response
            
            # Return success response
            return {
                "message": "Plan created successfully",
                "plan_id": plan_id,
                "status": "completed",
                "venues_found": venues_plan_response.get("total_venues_found", 0),
                "estimated_duration": venues_plan_response.get("estimated_total_duration")
            }
        else:
            # Plan generation failed
            plan_store[plan_id] = {
                "plan_id": plan_id,
                "status": "failed",
                "message": "Failed to generate venue plan"
            }
            
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate venue plan"
            )
            
    except Exception as e:
        logger.error(f"Error creating plan: {e}")
        raise HTTPException(status_code=500, detail=f"Plan creation failed: {str(e)}")

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

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Planning Service",
        "timestamp": datetime.utcnow().isoformat(),
        "active_plans": len(plan_store),
        "pending_requests": len(plan_requests_store)
    }
