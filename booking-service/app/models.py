from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TimeSlot(BaseModel):
    hours: str = Field(..., description="Time slot in format HH:MM-HH:MM")
    counter: int = Field(..., description="Number of available slots")

class OpenHours(BaseModel):
    start: str = Field(..., description="Opening time in HH:MM format")
    end: str = Field(..., description="Closing time in HH:MM format")

class Venue(BaseModel):
    venue_name: str = Field(..., description="Name of the venue")
    venue_type: str = Field(..., description="Type of venue")
    open_hours: OpenHours = Field(..., description="Opening and closing hours")
    time_slots: List[TimeSlot] = Field(..., description="Available time slots with counters")

class BookingRequest(BaseModel):
    google_place_id: str = Field(..., description="Google Place ID of the venue to book")
    time_slot: str = Field(..., description="Time slot to book in format HH:MM-HH:MM")
    user_id: str = Field(..., description="ID of the user making the booking")
    group_size: int = Field(default=1, description="Number of people in the group")

class BookingResponse(BaseModel):
    booking_id: str
    venue_id: str
    venue_name: str
    time_slot: str
    user_id: str
    booking_date: datetime
    status: str = "confirmed"

class BookingError(BaseModel):
    error: str
    message: str

class TimeSlotGenerationRequest(BaseModel):
    venue_id: str = Field(..., description="ID of the venue to generate time slots for")
    default_counter: int = Field(default=100, description="Default number of available slots per time slot")

class TimeSlotGenerationResponse(BaseModel):
    venue_id: str
    venue_name: str
    open_hours: OpenHours
    time_slots: List[TimeSlot]
    message: str
