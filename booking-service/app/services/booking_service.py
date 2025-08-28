from bson import ObjectId
from datetime import datetime
from typing import Optional, Dict, Any
from app.database import get_venues_collection
from app.models import BookingRequest, BookingResponse, BookingError
import uuid
import os

class BookingService:
    
    @staticmethod
    async def check_availability(venue_id: str, time_slot: str) -> Dict[str, Any]:
        """
        Check if a time slot is available for booking
        """
        try:
            venues_collection = get_venues_collection()
            
            # Find the venue by ID
            venue = await venues_collection.find_one({"_id": ObjectId(venue_id)})
            
            if not venue:
                return {
                    "available": False,
                    "error": "Venue not found"
                }
            
            # Find the specific time slot
            for slot in venue.get("time_slots", []):
                if slot.get("hours") == time_slot:
                    counter = slot.get("counter", 0)
                    return {
                        "available": counter > 0,
                        "counter": counter,
                        "venue_name": venue.get("venue_name"),
                        "time_slot": time_slot
                    }
            
            return {
                "available": False,
                "error": "Time slot not found"
            }
            
        except Exception as e:
            return {
                "available": False,
                "error": f"Database error: {str(e)}"
            }
    
    @staticmethod
    async def make_booking(booking_request: BookingRequest) -> BookingResponse:
        """
        Make a booking by decrementing the counter for the selected time slot
        """
        try:
            venues_collection = get_venues_collection()
            
            # First check availability
            availability = await BookingService.check_availability(
                booking_request.venue_id, 
                booking_request.time_slot
            )
            
            if not availability.get("available"):
                raise Exception(availability.get("error", "Time slot not available"))
            
            # Use atomic operation to decrement counter and ensure consistency
            result = await venues_collection.update_one(
                {
                    "_id": ObjectId(booking_request.venue_id),
                    "time_slots.hours": booking_request.time_slot,
                    "time_slots.counter": {"$gt": 0}
                },
                {
                    "$inc": {"time_slots.$.counter": -1}
                }
            )
            
            if result.modified_count == 0:
                raise Exception("Failed to book - no slots available or venue not found")
            
            # Get venue name for response
            venue = await venues_collection.find_one({"_id": ObjectId(booking_request.venue_id)})
            venue_name = venue.get("venue_name", "Unknown Venue") if venue else "Unknown Venue"
            
            # Create booking response
            booking_response = BookingResponse(
                booking_id=str(uuid.uuid4()),
                venue_id=booking_request.venue_id,
                venue_name=venue_name,
                time_slot=booking_request.time_slot,
                user_id=booking_request.user_id,
                booking_date=datetime.utcnow(),
                status="confirmed"
            )
            
            return booking_response
            
        except Exception as e:
            raise Exception(f"Booking failed: {str(e)}")
    
    @staticmethod
    async def get_venue_availability(venue_id: str) -> Dict[str, Any]:
        """
        Get all time slots and their availability for a venue
        """
        try:
            venues_collection = get_venues_collection()
            
            venue = await venues_collection.find_one({"_id": ObjectId(venue_id)})
            
            if not venue:
                return {
                    "error": "Venue not found"
                }
            
            return {
                "venue_id": venue_id,
                "venue_name": venue.get("venue_name"),
                "venue_type": venue.get("venue_type"),
                "open_hours": venue.get("open_hours"),
                "time_slots": venue.get("time_slots", [])
            }
            
        except Exception as e:
            return {
                "error": f"Database error: {str(e)}"
            }
