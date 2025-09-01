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

@router.post("/book", response_model=BookingResponse)
async def make_booking(booking_request: BookingRequest):
    """
    Make a booking for a specific venue and time slot
    """
    try:
        booking_response = await BookingService.make_booking(booking_request)
        return booking_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/book/validate")
async def validate_booking(booking_request: BookingRequest):
    """
    Validate if a booking can be made without actually making it
    """
    try:
        availability = await BookingService.check_availability(
            booking_request.venue_id, 
            booking_request.time_slot
        )
        
        if not availability.get("available"):
            return {
                "valid": False,
                "error": availability.get("error", "Time slot not available"),
                "available_slots": availability.get("counter", 0)
            }
        
        return {
            "valid": True,
            "available_slots": availability.get("counter", 0),
            "venue_name": availability.get("venue_name"),
            "time_slot": booking_request.time_slot
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

# @router.post("/generate-time-slots/{venue_id}")
# async def generate_time_slots_for_venue(
#     venue_id: str, 
#     default_counter: int = 100
# ):
#     """
#     Generate time slots for a specific venue by ID
#     """
#     try:
#         request = TimeSlotGenerationRequest(
#             venue_id=venue_id,
#             default_counter=default_counter
#         )
#         response = await BookingService.generate_venue_time_slots(request)
#         return response
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


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
