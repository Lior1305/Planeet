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
    async def check_overlapping_availability(venue_id: str, requested_time_slot: str) -> Dict[str, Any]:
        """
        Check availability for overlapping time slots
        This handles cases where a user wants to book 10:00-12:00 but we have 09:00-11:00 and 11:00-13:00
        """
        try:
            venues_collection = get_venues_collection()
            venue = await venues_collection.find_one({"_id": ObjectId(venue_id)})
            
            if not venue:
                return {
                    "available": False,
                    "error": "Venue not found"
                }
            
            # Parse requested time range
            try:
                req_start, req_end = requested_time_slot.split("-")
                req_start = datetime.strptime(req_start.strip(), "%H:%M")
                req_end = datetime.strptime(req_end.strip(), "%H:%M")
            except ValueError:
                return {
                    "available": False,
                    "error": "Invalid time slot format. Use HH:MM-HH:MM"
                }
            
            # Find overlapping slots
            overlapping_slots = []
            total_available = 0
            
            for slot in venue.get("time_slots", []):
                slot_start, slot_end = slot["hours"].split("-")
                slot_start = datetime.strptime(slot_start.strip(), "%H:%M")
                slot_end = datetime.strptime(slot_end.strip(), "%H:%M")
                
                # Check if slots overlap
                if slot_start < req_end and req_start < slot_end:
                    overlapping_slots.append({
                        "hours": slot["hours"],
                        "counter": slot["counter"],
                        "overlap_start": max(slot_start, req_start),
                        "overlap_end": min(slot_end, req_end)
                    })
                    total_available += slot["counter"]
            
            if not overlapping_slots:
                return {
                    "available": False,
                    "error": "No overlapping time slots found for the requested time"
                }
            
            # Check if all overlapping slots have availability
            min_available = min(slot["counter"] for slot in overlapping_slots)
            
            return {
                "available": min_available > 0,
                "counter": min_available,
                "venue_name": venue.get("venue_name"),
                "time_slot": requested_time_slot,
                "overlapping_slots": overlapping_slots,
                "total_available": total_available
            }
            
        except Exception as e:
            logger.error(f"Error checking overlapping availability: {e}")
            return {
                "available": False,
                "error": f"Database error: {str(e)}"
            }

    @staticmethod
    async def check_overlapping_availability_by_google_place_id(google_place_id: str, requested_time_slot: str) -> Dict[str, Any]:
        """
        Check availability for overlapping time slots using Google Place ID
        """
        try:
            venues_collection = get_venues_collection()
            venue = await venues_collection.find_one({"google_place_id": google_place_id})
            
            if not venue:
                return {
                    "available": False,
                    "error": "Venue not found with the provided Google Place ID"
                }
            
            # Parse requested time range
            try:
                req_start, req_end = requested_time_slot.split("-")
                req_start = datetime.strptime(req_start.strip(), "%H:%M")
                req_end = datetime.strptime(req_end.strip(), "%H:%M")
            except ValueError:
                return {
                    "available": False,
                    "error": "Invalid time slot format. Use HH:MM-HH:MM"
                }
            
            # Find overlapping slots
            overlapping_slots = []
            total_available = 0
            
            for slot in venue.get("time_slots", []):
                slot_start, slot_end = slot["hours"].split("-")
                slot_start = datetime.strptime(slot_start.strip(), "%H:%M")
                slot_end = datetime.strptime(slot_end.strip(), "%H:%M")
                
                # Check if slots overlap
                if slot_start < req_end and req_start < slot_end:
                    overlapping_slots.append({
                        "hours": slot["hours"],
                        "counter": slot["counter"],
                        "overlap_start": max(slot_start, req_start),
                        "overlap_end": min(slot_end, req_end)
                    })
                    total_available += slot["counter"]
            
            if not overlapping_slots:
                return {
                    "available": False,
                    "error": "No overlapping time slots found for the requested time"
                }
            
            # Check if all overlapping slots have availability
            min_available = min(slot["counter"] for slot in overlapping_slots)
            
            return {
                "available": min_available > 0,
                "counter": min_available,
                "venue_name": venue.get("venue_name"),
                "time_slot": requested_time_slot,
                "overlapping_slots": overlapping_slots,
                "total_available": total_available
            }
            
        except Exception as e:
            logger.error(f"Error checking overlapping availability by Google Place ID: {e}")
            return {
                "available": False,
                "error": f"Database error: {str(e)}"
            }

    @staticmethod
    async def make_booking(request: BookingRequest) -> Dict[str, Any]:
        """
        Make a booking for overlapping time slots
        """
        try:
            venues_collection = get_venues_collection()
            venue = await venues_collection.find_one({"_id": ObjectId(request.venue_id)})
            
            if not venue:
                return {"error": "Venue not found"}
            
            # Parse requested time range
            try:
                req_start, req_end = request.time_slot.split("-")
                req_start = datetime.strptime(req_start.strip(), "%H:%M")
                req_end = datetime.strptime(req_end.strip(), "%H:%M")
            except ValueError:
                return {"error": "Invalid time slot format. Use HH:MM-HH:MM"}
            
            # Find overlapping slots
            overlapping_slots = []
            for slot in venue.get("time_slots", []):
                slot_start, slot_end = slot["hours"].split("-")
                slot_start = datetime.strptime(slot_start.strip(), "%H:%M")
                slot_end = datetime.strptime(slot_end.strip(), "%H:%M")
                
                # Check if slots overlap
                if slot_start < req_end and req_start < slot_end:
                    overlapping_slots.append(slot)
            
            if not overlapping_slots:
                return {"error": "No overlapping time slots found for the requested time"}
            
            # Check if all overlapping slots have availability
            if not all(slot["counter"] > 0 for slot in overlapping_slots):
                return {"error": "One or more overlapping time slots are fully booked"}
            
            # Decrement availability for all overlapping slots
            for slot in overlapping_slots:
                slot["counter"] -= 1
            
            # Update the venue in the database
            result = await venues_collection.update_one(
                {"_id": ObjectId(request.venue_id)},
                {"$set": {"time_slots": venue["time_slots"]}}
            )
            
            if result.modified_count == 0:
                return {"error": "Failed to update venue availability"}
            
            # Generate booking ID
            booking_id = str(uuid.uuid4())
            
            # Create booking response
            return {
                "success": True,
                "booking_id": booking_id,
                "venue_id": request.venue_id,
                "venue_name": venue.get("venue_name"),
                "time_slot": request.time_slot,
                "user_id": request.user_id,
                "booking_date": datetime.utcnow(),
                "status": "confirmed",
                "reserved_slots": [slot["hours"] for slot in overlapping_slots],
                "message": f"Successfully booked {request.time_slot} at {venue.get('venue_name')}"
            }
            
        except Exception as e:
            logger.error(f"Error making booking: {e}")
            return {"error": f"Booking failed: {str(e)}"}

    @staticmethod
    async def make_booking_by_google_place_id(request) -> Dict[str, Any]:
        """
        Make a booking using Google Place ID instead of MongoDB ID
        """
        try:
            venues_collection = get_venues_collection()
            
            # First, find the venue by Google Place ID
            venue = await venues_collection.find_one({"google_place_id": request.google_place_id})
            
            if not venue:
                return {"error": "Venue not found with the provided Google Place ID"}
            
            # Parse requested time range
            try:
                req_start, req_end = request.time_slot.split("-")
                req_start = datetime.strptime(req_start.strip(), "%H:%M")
                req_end = datetime.strptime(req_end.strip(), "%H:%M")
            except ValueError:
                return {"error": "Invalid time slot format. Use HH:MM-HH:MM"}
            
            # Find overlapping slots
            overlapping_slots = []
            for slot in venue.get("time_slots", []):
                slot_start, slot_end = slot["hours"].split("-")
                slot_start = datetime.strptime(slot_start.strip(), "%H:%M")
                slot_end = datetime.strptime(slot_end.strip(), "%H:%M")
                
                # Check if slots overlap
                if slot_start < req_end and req_start < slot_end:
                    overlapping_slots.append(slot)
            
            if not overlapping_slots:
                return {"error": "No overlapping time slots found for the requested time"}
            
            # Check if all overlapping slots have availability
            if not all(slot["counter"] > 0 for slot in overlapping_slots):
                return {"error": "One or more overlapping time slots are fully booked"}
            
            # Decrement availability for all overlapping slots
            for slot in overlapping_slots:
                slot["counter"] -= 1
            
            # Update the venue in the database
            result = await venues_collection.update_one(
                {"_id": venue["_id"]},
                {"$set": {"time_slots": venue["time_slots"]}}
            )
            
            if result.modified_count == 0:
                return {"error": "Failed to update venue availability"}
            
            # Generate booking ID
            booking_id = str(uuid.uuid4())
            
            # Create booking response
            return {
                "success": True,
                "booking_id": booking_id,
                "venue_id": str(venue["_id"]),
                "venue_name": venue.get("venue_name"),
                "time_slot": request.time_slot,
                "user_id": request.user_id,
                "booking_date": datetime.utcnow(),
                "status": "confirmed",
                "reserved_slots": [slot["hours"] for slot in overlapping_slots],
                "message": f"Successfully booked {request.time_slot} at {venue.get('venue_name')}"
            }
            
        except Exception as e:
            logger.error(f"Error making booking by Google Place ID: {e}")
            return {"error": f"Booking failed: {str(e)}"}

    
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
                "opening_hours": venue.get("opening_hours"),
                "time_slots": venue.get("time_slots", [])
            }
            
        except Exception as e:
            return {
                "error": f"Database error: {str(e)}"
            }

    @staticmethod
    async def find_venue_by_google_place_id(google_place_id: str) -> Dict[str, Any]:
        """
        Find a venue by Google Place ID and return its MongoDB ID and basic info
        """
        try:
            venues_collection = get_venues_collection()
            
            # Find the venue by Google Place ID
            venue = await venues_collection.find_one({"google_place_id": google_place_id})
            
            if not venue:
                return {
                    "found": False,
                    "error": "Venue not found with the provided Google Place ID"
                }
            
            return {
                "found": True,
                "venue_id": str(venue["_id"]),  # Convert ObjectId to string
                "venue_name": venue.get("venue_name"),
                "venue_type": venue.get("venue_type"),
                "opening_hours": venue.get("opening_hours"),
                "google_place_id": venue.get("google_place_id"),
                "has_time_slots": len(venue.get("time_slots", [])) > 0
            }
            
        except Exception as e:
            logger.error(f"Error finding venue by Google Place ID: {e}")
            return {
                "found": False,
                "error": f"Database error: {str(e)}"
            }

    @staticmethod
    async def find_venues_by_google_place_ids(google_place_ids: list) -> Dict[str, Any]:
        """
        Find multiple venues by Google Place IDs and return their MongoDB IDs and basic info
        """
        try:
            venues_collection = get_venues_collection()
            
            # Find venues by Google Place IDs
            venues = await venues_collection.find(
                {"google_place_id": {"$in": google_place_ids}}
            ).to_list(length=None)
            
            if not venues:
                return {
                    "found": False,
                    "error": "No venues found with the provided Google Place IDs",
                    "venues": []
                }
            
            # Format the response
            venue_list = []
            for venue in venues:
                venue_list.append({
                    "venue_id": str(venue["_id"]),
                    "venue_name": venue.get("venue_name"),
                    "venue_type": venue.get("venue_type"),
                    "opening_hours": venue.get("opening_hours"),
                    "google_place_id": venue.get("google_place_id"),
                    "has_time_slots": len(venue.get("time_slots", [])) > 0
                })
            
            return {
                "found": True,
                "count": len(venue_list),
                "venues": venue_list
            }
            
        except Exception as e:
            logger.error(f"Error finding venues by Google Place IDs: {e}")
            return {
                "found": False,
                "error": f"Database error: {str(e)}",
                "venues": []
            }

    @staticmethod
    def generate_time_slots(start_time: str, end_time: str, default_counter: int = 100) -> list:
        """
        Generate time slots in 2-hour intervals from start_time to end_time
        Format: "HH:MM-HH:MM"
        Handles overnight hours (closing time after midnight)
        """
        slots = []
        
        try:
            # Parse start and end times
            start_hour = int(start_time.split(':')[0])
            end_hour = int(end_time.split(':')[0])
            
            # Handle overnight hours (e.g., 10:00 to 01:00 means 10:00 AM to 1:00 AM next day)
            if end_hour < start_hour:
                # This is an overnight venue (closes after midnight)
                end_hour += 24  # Add 24 hours to make it 25:00 (1:00 AM next day)
                logger.info(f"Overnight venue detected: {start_time} to {end_time} (adjusted to {start_hour}:00 to {end_hour}:00)")
            
            # Now start_hour = 10, end_hour = 25 (instead of 1)
            # 10 < 25 is TRUE, so we continue
            
            # Generate 2-hour slots
            current_hour = start_hour  # 10
            while current_hour < end_hour:  # 10 < 25
                slot_start = f"{current_hour % 24:02d}:00"  # 10 % 24 = 10, so "10:00"
                
                # Calculate slot end
                if current_hour + 2 <= end_hour:
                    slot_end = f"{(current_hour + 2) % 24:02d}:00"  # 12 % 24 = 12, so "12:00"
                else:
                    slot_end = f"{end_hour % 24:02d}:00"  # 25 % 24 = 1, so "01:00"
                
                slot = {
                    "hours": f"{slot_start}-{slot_end}",
                    "counter": default_counter
                }
                slots.append(slot)
                
                current_hour += 2
            
            logger.info(f"Generated {len(slots)} time slots from {start_time} to {end_time}")
            return slots
            
        except Exception as e:
            logger.error(f"Error generating time slots: {e}")
            return []
    
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
            
            # Get opening hours - handle the correct field name from venues service
            opening_hours = venue.get("opening_hours", {})
            
            # Extract open_at and close_at times
            start_time = opening_hours.get("open_at")
            end_time = opening_hours.get("close_at")
            
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
