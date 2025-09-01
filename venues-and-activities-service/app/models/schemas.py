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
    SPA = "spa"
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


# Venue Discovery Models (NEW)
class VenueDiscoveryRequest(BaseModel):
    """Request model for venue discovery from Google Places API"""
    venue_types: List[str] = Field(..., description="Types of venues to discover")
    location: Location = Field(..., description="Location for venue search")
    radius_km: float = Field(10.0, gt=0, le=100, description="Search radius in kilometers")


class VenueDiscoveryResponse(BaseModel):
    """Response model for venue discovery"""
    venues_by_type: Dict[str, List[Dict[str, Any]]] = Field(..., description="Venues grouped by type")
    total_venues_found: int = Field(..., description="Total number of venues found")
    venue_types_requested: List[str] = Field(..., description="Venue types that were requested")
    location: Location = Field(..., description="Search location")
    radius_km: float = Field(..., description="Search radius used")

    discovered_at: str = Field(..., description="Timestamp when venues were discovered")

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


