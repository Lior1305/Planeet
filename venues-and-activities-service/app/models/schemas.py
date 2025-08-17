from pydantic import BaseModel, Field
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
    HOTEL = "hotel"
    OTHER = "other"

class Location(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    address: Optional[str] = Field(None, description="Human-readable address")
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="Country name")

class VenueLink(BaseModel):
    type: str = Field(..., description="Type of link (website, social_media, booking, menu, etc.)")
    url: str = Field(..., description="The actual URL")
    title: Optional[str] = Field(None, description="Display title for the link")
    description: Optional[str] = Field(None, description="Description of what this link provides")

class Venue(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier")
    name: str = Field(..., description="Venue name")
    description: Optional[str] = Field(None, description="Venue description")
    venue_type: VenueType = Field(..., description="Type of venue")
    location: Location = Field(..., description="Venue location")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating (0-5)")
    price_range: Optional[str] = Field(None, description="Price range (e.g., $, $$, $$$)")
    opening_hours: Optional[Dict[str, str]] = Field(None, description="Opening hours by day")
    contact_info: Optional[Dict[str, str]] = Field(None, description="Contact information")
    amenities: Optional[List[str]] = Field(None, description="List of available amenities")
    images: Optional[List[str]] = Field(None, description="List of image URLs")
    links: Optional[List[VenueLink]] = Field(None, description="List of related links (website, social media, booking, etc.)")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

# User Preference Models (for integration with Planning Service)
class UserPreferences(BaseModel):
    user_id: str = Field(..., description="User identifier")
    preferred_venue_types: Optional[List[VenueType]] = Field(None, description="Preferred venue types")
    preferred_price_range: Optional[str] = Field(None, description="Preferred price range")
    preferred_amenities: Optional[List[str]] = Field(None, description="Preferred amenities")
    preferred_cities: Optional[List[str]] = Field(None, description="Preferred cities")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum preferred rating")
    dietary_restrictions: Optional[List[str]] = Field(None, description="Dietary restrictions (e.g., vegetarian, vegan)")
    accessibility_needs: Optional[List[str]] = Field(None, description="Accessibility requirements")
    activity_level: Optional[str] = Field(None, description="Preferred activity level (low, medium, high)")
    group_size: Optional[int] = Field(None, description="Typical group size for outings")
    time_preferences: Optional[Dict[str, str]] = Field(None, description="Preferred times for different activities")
    special_interests: Optional[List[str]] = Field(None, description="Special interests or hobbies")

class PersonalizedSearchRequest(BaseModel):
    user_id: str = Field(..., description="User identifier for personalized search")
    query: Optional[str] = Field(None, description="Search query text")
    location: Optional[Location] = Field(None, description="Search location")
    radius_km: Optional[float] = Field(10.0, gt=0, le=100, description="Search radius in kilometers")
    venue_types: Optional[List[VenueType]] = Field(None, description="Filter by venue types (overrides user preferences)")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum rating filter (overrides user preferences)")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price filter (overrides user preferences)")
    amenities: Optional[List[str]] = Field(None, description="Required amenities (overrides user preferences)")
    open_now: Optional[bool] = Field(None, description="Filter for currently open venues")
    limit: Optional[int] = Field(20, gt=0, le=100, description="Maximum number of results")
    offset: Optional[int] = Field(0, ge=0, description="Pagination offset")
    use_preferences: bool = Field(True, description="Whether to use user preferences for personalization")

class SearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Search query text")
    location: Optional[Location] = Field(None, description="Search location")
    radius_km: Optional[float] = Field(10.0, gt=0, le=100, description="Search radius in kilometers")
    venue_types: Optional[List[VenueType]] = Field(None, description="Filter by venue types")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum rating filter")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price filter")
    amenities: Optional[List[str]] = Field(None, description="Required amenities")
    open_now: Optional[bool] = Field(None, description="Filter for currently open venues")
    limit: Optional[int] = Field(20, gt=0, le=100, description="Maximum number of results")
    offset: Optional[int] = Field(0, ge=0, description="Pagination offset")

class SearchResponse(BaseModel):
    venues: List[Venue] = Field(..., description="List of matching venues")
    total_count: int = Field(..., description="Total number of results")
    has_more: bool = Field(..., description="Whether there are more results available")

class PersonalizedSearchResponse(BaseModel):
    venues: List[Venue] = Field(..., description="List of matching venues")
    total_count: int = Field(..., description="Total number of results")
    has_more: bool = Field(..., description="Whether there are more results available")
    user_preferences_used: Optional[UserPreferences] = Field(None, description="User preferences that were applied")
    personalization_score: Optional[float] = Field(None, description="How well the results match user preferences (0-1)")

class VenueCreate(BaseModel):
    name: str = Field(..., description="Venue name")
    description: Optional[str] = Field(None, description="Venue description")
    venue_type: VenueType = Field(..., description="Type of venue")
    location: Location = Field(..., description="Venue location")
    price_range: Optional[str] = Field(None, description="Price range")
    opening_hours: Optional[Dict[str, str]] = Field(None, description="Opening hours")
    contact_info: Optional[str] = Field(None, description="Contact information")
    amenities: Optional[List[str]] = Field(None, description="Available amenities")
    images: Optional[List[str]] = Field(None, description="Image URLs")
    links: Optional[List[VenueLink]] = Field(None, description="Related links")

class VenueUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Venue name")
    description: Optional[str] = Field(None, description="Venue description")
    venue_type: Optional[VenueType] = Field(None, description="Type of venue")
    location: Optional[Location] = Field(None, description="Venue location")
    price_range: Optional[str] = Field(None, description="Price range")
    opening_hours: Optional[Dict[str, str]] = Field(None, description="Opening hours")
    contact_info: Optional[str] = Field(None, description="Contact information")
    amenities: Optional[List[str]] = Field(None, description="Available amenities")
    images: Optional[List[str]] = Field(None, description="Image URLs")
    links: Optional[List[VenueLink]] = Field(None, description="Related links")

class MessageResponse(BaseModel):
    message: str = Field(..., description="Response message")
    success: bool = Field(..., description="Operation success status")

class PaginatedResponse(BaseModel):
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
