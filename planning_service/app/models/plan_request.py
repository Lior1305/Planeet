"""
Models for plan requests and responses between Planning Service and Venues Service
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class VenueType(str, Enum):
    RESTAURANT = "restaurant"
    BAR = "bar"
    CAFE = "cafe"
    MUSEUM = "museum"
    THEATER = "theater"
    PARK = "park"
    SHOPPING_CENTER = "shopping_center"
    SPORTS_FACILITY = "sports_facility"
    SPA = "spa"
    OTHER = "other"

class Location(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    address: Optional[str] = Field(None, description="Human-readable address")
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="Country name")

class PlanRequest(BaseModel):
    """Request from Planning Service to Venues Service for venue discovery"""
    user_id: str = Field(..., description="User identifier")
    plan_id: Optional[str] = Field(None, description="Unique plan identifier")
    
    # Venue requirements
    venue_types: List[VenueType] = Field(..., description="Types of venues needed")
    location: Location = Field(..., description="Target location for the outing")
    radius_km: float = Field(10.0, gt=0, le=100, description="Search radius in kilometers")
    
    # Timing requirements
    date: datetime = Field(..., description="Date and time for the outing")
    duration_hours: Optional[float] = Field(None, description="Expected duration in hours")
    
    # Group and preferences
    group_size: int = Field(..., ge=1, description="Number of people")
    budget_range: Optional[str] = Field(None, description="Budget range ($, $$, $$$)")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum venue rating")
    
    # Special requirements
    amenities: Optional[List[str]] = Field(None, description="Required amenities")
    dietary_restrictions: Optional[List[str]] = Field(None, description="Dietary requirements")
    accessibility_needs: Optional[List[str]] = Field(None, description="Accessibility requirements")
    
    # Planning preferences
    use_personalization: bool = Field(True, description="Whether to use user preferences")
    max_venues: int = Field(5, ge=1, le=20, description="Maximum number of venues to suggest")
    include_links: bool = Field(True, description="Whether to include venue links")
    
    @field_validator('date')
    @classmethod
    def validate_start_time_15_minute_intervals(cls, v: datetime) -> datetime:
        """
        Validate that the start time is in 15-minute intervals
        Valid times: XX:00, XX:15, XX:30, XX:45
        """
        if v.minute not in [0, 15, 30, 45]:
            valid_times = ["XX:00", "XX:15", "XX:30", "XX:45"]
            raise ValueError(
                f"Start time must be in 15-minute intervals. "
                f"Valid minutes are: {', '.join(valid_times)}. "
                f"Received: {v.strftime('%H:%M')}"
            )
        
        if v.second != 0 or v.microsecond != 0:
            raise ValueError(
                f"Start time must not include seconds or microseconds. "
                f"Received: {v.strftime('%H:%M:%S.%f')}"
            )
        
        return v

class VenueSuggestion(BaseModel):
    """Individual venue suggestion for the plan"""
    venue_id: str = Field(..., description="Venue identifier")
    name: str = Field(..., description="Venue name")
    venue_type: VenueType = Field(..., description="Type of venue")
    location: Location = Field(..., description="Venue location")
    rating: Optional[float] = Field(None, description="Venue rating")
    price_range: Optional[str] = Field(None, description="Price range")
    amenities: Optional[List[str]] = Field(None, description="Available amenities")
    links: Optional[List[Dict[str, str]]] = Field(None, description="Venue links")
    personalization_score: Optional[float] = Field(None, description="How well it matches user preferences")
    
    # Enhanced timing information
    start_time: Optional[str] = Field(None, description="Calculated start time for this venue (HH:MM)")
    end_time: Optional[str] = Field(None, description="Calculated end time for this venue (HH:MM)")
    duration_minutes: Optional[int] = Field(None, description="Estimated duration at this venue in minutes")
    travel_time_from_previous: Optional[int] = Field(None, description="Travel time from previous venue in minutes")
    travel_distance_km: Optional[float] = Field(None, description="Distance from previous venue in kilometers")

class PlanResponse(BaseModel):
    """Response from Venues Service to Planning Service with venue suggestions"""
    plan_id: str = Field(..., description="Plan identifier")
    user_id: str = Field(..., description="User identifier")
    
    # Venue suggestions
    suggested_venues: List[VenueSuggestion] = Field(..., description="List of suggested venues")
    total_venues_found: int = Field(..., description="Total venues found in search")
    
    # Plan details
    estimated_total_duration: Optional[float] = Field(None, description="Estimated total duration in hours")
    travel_route: Optional[List[Dict[str, Any]]] = Field(None, description="Suggested travel route between venues")
    
    # Personalization info
    personalization_applied: bool = Field(..., description="Whether personalization was applied")
    average_personalization_score: Optional[float] = Field(None, description="Average personalization score")
    
    # Metadata
    search_criteria_used: Dict[str, Any] = Field(..., description="Search criteria that were applied")
    generated_at: datetime = Field(..., description="When the plan was generated")
    
    # Status
    status: str = Field("completed", description="Plan generation status")
    message: Optional[str] = Field(None, description="Additional information or warnings") 