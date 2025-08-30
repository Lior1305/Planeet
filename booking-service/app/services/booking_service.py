from bson import ObjectId
from datetime import datetime
from typing import Optional, Dict, Any
from app.database import get_venues_collection
from app.models import BookingRequest, BookingResponse, BookingError, TimeSlotGenerationRequest, TimeSlotGenerationResponse
import uuid
import os
import logging
import httpx

logger = logging.getLogger(__name__)

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

    @staticmethod
    def generate_time_slots(start_time: str, end_time: str, default_counter: int = 100) -> list:
        """
        Generate time slots in 2-hour intervals from start_time to end_time
        Format: "HH:MM-HH:MM"
        """
        slots = []
        
        # Parse start and end times
        start_hour = int(start_time.split(':')[0])
        end_hour = int(end_time.split(':')[0])
        
        # Generate 2-hour slots
        for hour in range(start_hour, end_hour - 1, 2):
            slot_start = f"{hour:02d}:00"
            slot_end = f"{hour + 2:02d}:00"
            slot = {
                "hours": f"{slot_start}-{slot_end}",
                "counter": default_counter
            }
            slots.append(slot)
        
        return slots
    
    @staticmethod
    async def generate_venue_time_slots(request: TimeSlotGenerationRequest) -> TimeSlotGenerationResponse:
        """
        Generate time slots for a venue based on its opening hours
        """
        try:
            venues_collection = get_venues_collection()
            
            # Find the venue by ID
            venue = await venues_collection.find_one({"_id": ObjectId(request.venue_id)})
            
            if not venue:
                raise Exception("Venue not found")
            
            # Get opening hours - handle different formats
            open_hours = venue.get("open_hours", {})
            
            # Try different possible formats
            start_time = None
            end_time = None
            
            if open_hours:
                # Format 1: start/end
                start_time = open_hours.get("start")
                end_time = open_hours.get("end")
                
                # Format 2: open_at/close_at
                if not start_time:
                    start_time = open_hours.get("open_at")
                if not end_time:
                    end_time = open_hours.get("close_at")
            
            # If no opening hours defined, use default hours
            if not start_time or not end_time:
                logger.info(f"No opening hours found for venue {venue.get('venue_name')}, using default hours")
                start_time = "10:00"  # Default opening time
                end_time = "22:00"    # Default closing time
            
            # Generate time slots
            time_slots = BookingService.generate_time_slots(
                start_time, 
                end_time, 
                request.default_counter
            )
            
            # Update the venue with generated time slots
            result = await venues_collection.update_one(
                {"_id": ObjectId(request.venue_id)},
                {"$set": {"time_slots": time_slots}}
            )
            
            if result.modified_count == 0:
                raise Exception("Failed to update venue with time slots")
            
            # Return the response
            return TimeSlotGenerationResponse(
                venue_id=request.venue_id,
                venue_name=venue.get("venue_name", "Unknown Venue"),
                open_hours={"start": start_time, "end": end_time},
                time_slots=time_slots,
                message=f"Successfully generated {len(time_slots)} time slots for {venue.get('venue_name')}"
            )
            
        except Exception as e:
            raise Exception(f"Failed to generate time slots: {str(e)}")
