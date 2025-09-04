from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import Dict, Any
from app.models import BookingRequest, BookingResponse, BookingError, TimeSlotGenerationRequest, TimeSlotGenerationResponse
from app.services.booking_service import BookingService
from app.database import connect_to_mongo, get_venues_collection  # ✅ Fixed import
from bson import ObjectId


router = APIRouter()

@router.get("/")
def home():
    return {"message": "Booking Service Running"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Booking Service",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/availability/{venue_id}")
async def check_venue_availability(venue_id: str):
    """
    Check availability for all time slots of a venue
    """
    try:
        availability = await BookingService.get_venue_availability(venue_id)
        
        if "error" in availability:
            raise HTTPException(status_code=404, detail=availability["error"])
        
        return availability
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/availability/{venue_id}/{time_slot}")
async def check_specific_availability(venue_id: str, time_slot: str):
    """
    Check availability for a specific time slot
    """
    try:
        availability = await BookingService.check_availability(venue_id, time_slot)
        
        if not availability.get("available") and "error" in availability:
            raise HTTPException(status_code=404, detail=availability["error"])
        
        return availability
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/availability/{venue_id}/overlapping/{time_slot}")
async def check_overlapping_availability(venue_id: str, time_slot: str):
    """
    Check availability for overlapping time slots
    This handles cases where a user wants to book 10:00-12:00 but we have 09:00-11:00 and 11:00-13:00
    """
    try:
        availability = await BookingService.check_overlapping_availability(venue_id, time_slot)
        
        if not availability.get("available") and "error" in availability:
            raise HTTPException(status_code=404, detail=availability["error"])
        
        return availability
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/book", response_model=BookingResponse)
async def make_booking(booking_request: BookingRequest):
    """
    Make a booking using Google Place ID
    """
    try:
        booking_response = await BookingService.make_booking_by_google_place_id(booking_request)
        
        if "error" in booking_response:
            raise HTTPException(status_code=400, detail=booking_response["error"])
        
        return booking_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/book/validate")
async def validate_booking(booking_request: BookingRequest):
    """
    Validate if a booking can be made without actually making it
    Uses overlapping time slot logic
    """
    try:
        availability = await BookingService.check_overlapping_availability(
            booking_request.venue_id, 
            booking_request.time_slot
        )
        
        if not availability.get("available"):
            return {
                "valid": False,
                "error": availability.get("error", "Time slot not available"),
                "available_slots": availability.get("counter", 0),
                "overlapping_slots": availability.get("overlapping_slots", [])
            }
        
        return {
            "valid": True,
            "available_slots": availability.get("counter", 0),
            "venue_name": availability.get("venue_name"),
            "time_slot": booking_request.time_slot,
            "overlapping_slots": availability.get("overlapping_slots", []),
            "total_available": availability.get("total_available", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-time-slots", response_model=TimeSlotGenerationResponse)
async def generate_venue_time_slots(request: TimeSlotGenerationRequest):
    """
    Generate time slots for a venue based on its opening hours
    This endpoint is called by the venues and activities service
    """
    try:
        response = await BookingService.generate_venue_time_slots(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-time-slots/{venue_id}")
async def generate_time_slots_for_venue(
    venue_id: str, 
    default_counter: int = 100
):
    """
    Generate time slots for a specific venue by ID
    and update the venues collection with the generated slots
    """
    try:
        request = TimeSlotGenerationRequest(
            venue_id=venue_id,
            default_counter=default_counter
        )
        response = await BookingService.generate_venue_time_slots(request)

        # --- Save generated slots into venues collection ---
        venues_collection = get_venues_collection()
        venues_collection.update_one(
            {"_id": ObjectId(venue_id)},
            {"$set": {"time_slots": response.time_slots}}
        )

        return {
            "message": "Time slots generated and saved successfully",
            "venue_id": venue_id,
            "time_slots": response.time_slots
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/venue/google-place/{google_place_id}")
async def find_venue_by_google_place_id(google_place_id: str):
    """
    Find a venue by Google Place ID and return its MongoDB ID and basic info
    This allows the UI to get venue details using Google Place ID
    """
    try:
        venue_info = await BookingService.find_venue_by_google_place_id(google_place_id)
        
        if not venue_info.get("found"):
            raise HTTPException(status_code=404, detail=venue_info["error"])
        
        return venue_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/venue/google-place/batch")
async def find_venues_by_google_place_ids(google_place_ids: list[str]):
    """
    Find multiple venues by Google Place IDs and return their MongoDB IDs and basic info
    This is useful for batch operations
    """
    try:
        venues_info = await BookingService.find_venues_by_google_place_ids(google_place_ids)
        
        if not venues_info.get("found"):
            raise HTTPException(status_code=404, detail=venues_info["error"])
        
        return venues_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
