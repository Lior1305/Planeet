from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from typing import List, Optional
from datetime import datetime
import uuid
import logging
from bson import ObjectId
from datetime import datetime
from typing import List, Dict


from app.models.schemas import (
    Venue, VenueCreate, VenueUpdate, VenueLink,
    SearchRequest, SearchResponse, PersonalizedSearchRequest, PersonalizedSearchResponse,
    MessageResponse, PaginatedResponse, UserPreferences,
    VenueType, TimeSlot, TimeSlotCreate, TimeSlotUpdate, TimeSlotSearchRequest, TimeSlotSearchResponse, TimeSlotStatus,
    VenueDiscoveryRequest, VenueDiscoveryResponse
)

# Initialize router
router = APIRouter(prefix="/api/v1", tags=["venues"])

# Initialize logger
logger = logging.getLogger(__name__)

# Import database storage and services
from app.db import get_venues_collection, get_time_slots_collection
from app.services.planning_integration import planning_integration
from app.services.personalization import personalization_service
from app.services.venue_discovery import venue_discovery

# Helper functions
def get_venue_by_id(venue_id: str) -> Venue:
    """Get venue by ID from MongoDB - supports both MongoDB ObjectId and Google place_id"""
    venues_collection = get_venues_collection()
    
    try:
        # First try to find by Google place_id
        venue_doc = venues_collection.find_one({"google_place_id": venue_id})
        
        # If not found, try MongoDB ObjectId (for backward compatibility)
        if not venue_doc:
            try:
                venue_doc = venues_collection.find_one({"_id": ObjectId(venue_id)})
            except:
                pass  # Invalid ObjectId format
        
        if not venue_doc:
            raise HTTPException(status_code=404, detail="Venue not found")
        
        # Set the id field to Google place_id if available, otherwise MongoDB ObjectId
        venue_doc["id"] = venue_doc.get("google_place_id", str(venue_doc["_id"]))
        return Venue(**venue_doc)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail="Invalid venue ID")

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    import math
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# --- Normalize incoming venue ---
def normalize_venue(venue: Dict) -> Dict:
    """Extract and normalize fields from Google Places venue data."""
    return {
        "venue_name": venue.get("venue_name", venue.get("name", "Unknown Venue")),
        "venue_type": venue.get("venue_type", "other"),
        "opening_hours": venue.get("opening_hours", {"open_at": "", "close_at": ""}),  # Dictionary format
        "time_slots": venue.get("time_slots", []),  # Empty for now
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

# --- Save discovered venues directly into Mongo ---
async def save_discovered_venues_to_db(venues: List[dict]):
    logger.info(f"Starting to save {len(venues)} venues to MongoDB")
    venues_collection = get_venues_collection()
    time_slots_collection = get_time_slots_collection()
    saved_count = 0

    for venue in venues:
        try:
            venue_data = normalize_venue(venue)

            # Use Google place_id as the venue ID for MongoDB
            venue_id = venue.get("venue_id", venue.get("id"))  # Support both field names
            
            # Avoid duplicates by checking Google place_id
            existing = venues_collection.find_one({"google_place_id": venue_id})
            if existing:
                logger.info(f"Venue with place_id {venue_id} already exists, skipping")
                continue
            
            # Add Google place_id to venue data
            venue_data["google_place_id"] = venue_id

            # Insert into MongoDB (venues)
            result = venues_collection.insert_one(venue_data)
            saved_count += 1
            logger.info(f"Saved venue: {venue_data['venue_name']} (ID: {result.inserted_id})")

            # --- Also insert into time_slots ---
            time_slot_doc = {
                "venue_id": venue_id,  # Use Google place_id
                "venue_name": venue_data["venue_name"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "date": None,
                "start_time": None,
                "end_time": None,
                "capacity": None,
                "status": "available"
            }
            time_slots_collection.insert_one(time_slot_doc)
            logger.info(f"Created initial time_slot for venue: {venue_data['venue_name']}")

        except Exception as e:
            logger.error(f"❌ Failed to save venue {venue.get('venue_name', venue.get('name'))}: {e}")
            continue

    logger.info(f"Successfully saved {saved_count} new venues")
    return saved_count



# Venue Discovery Endpoint (NEW!)
@router.post("/venues/discover", response_model=VenueDiscoveryResponse)
async def discover_venues(venue_request: VenueDiscoveryRequest):
    """
    Discover venues from Google Places API based on request criteria.
    
    This endpoint only handles venue discovery and returns raw venue data
    for the Planning Service to use in creating plans.
    """
    try:
        # Extract request data
        venue_types = venue_request.venue_types
        location = venue_request.location.dict()
        radius_km = venue_request.radius_km
        user_id = venue_request.user_id
        use_personalization = venue_request.use_personalization
        
        logger.info(f"Starting venue discovery for types: {venue_types}")
        
        # Get user preferences if personalization is enabled
        user_preferences = None
        if use_personalization and user_id:
            user_preferences = await planning_integration.get_user_preferences(user_id)
        
        # Discover venues for each requested type
        venues_by_type = {}
        total_venues_found = 0
        
        for venue_type in venue_types:
            venues = await venue_discovery.discover_venues_for_type(
                venue_type, location, radius_km, user_preferences, 20  # Get more venues for planning service to choose from
            )
            
            # Apply personalization and ranking within each venue type
            if user_preferences and use_personalization:
                ranked_venues = personalization_service.personalize_venue_list(
                    venues, user_preferences
                )
                # Extract venues and scores, keep top 20 for planning service
                venues_by_type[venue_type] = [venue for venue, score in ranked_venues[:20]]
            else:
                venues_by_type[venue_type] = venues
                
            total_venues_found += len(venues_by_type[venue_type])
            logger.info(f"Discovered {len(venues_by_type[venue_type])} venues for type {venue_type}")

        # Convert venues to dictionaries for JSON serialization
        serialized_venues_by_type = {}
        for venue_type, venues in venues_by_type.items():
            serialized_venues_by_type[venue_type] = [
                {
                    "id": venue.id,
                    "name": venue.name,
                    "description": venue.description,
                    "venue_type": venue.venue_type.value,
                    "location": {
                        "latitude": venue.location.latitude,
                        "longitude": venue.location.longitude,
                        "address": venue.location.address,
                        "city": venue.location.city,
                        "country": venue.location.country
                    },
                    "rating": venue.rating,
                    "price_range": venue.price_range,
                    "amenities": venue.amenities or [],
                    "links": [
                        {
                            "type": link.type,
                            "url": link.url,
                            "title": link.title,
                            "description": link.description
                        } for link in venue.links
                    ] if venue.links else [],
                    "created_at": venue.created_at.isoformat() if venue.created_at else None,
                    "updated_at": venue.updated_at.isoformat() if venue.updated_at else None
                }
                for venue in venues
            ]

        response = VenueDiscoveryResponse(
            venues_by_type=serialized_venues_by_type,
            total_venues_found=total_venues_found,
            venue_types_requested=venue_types,
            location=venue_request.location,
            radius_km=radius_km,
            personalization_applied=use_personalization and user_preferences is not None,
            discovered_at=datetime.utcnow().isoformat()
        )

        # Save discovered venues to MongoDB
        all_venues_for_saving = []
        for venues in venues_by_type.values():
            for venue in venues:
                venue_dict = {
                    "id": venue.id,  # Google place_id (for compatibility with save function)
                    "venue_name": venue.name,
                    "venue_type": venue.venue_type.value,
                    "opening_hours": {  # Dictionary format
                        "open_at": "",
                        "close_at": ""
                    },
                    "time_slots": []  # Empty for now
                }
                all_venues_for_saving.append(venue_dict)

        if all_venues_for_saving:
            logger.info(f"Saving {len(all_venues_for_saving)} discovered venues to MongoDB...")
            await save_discovered_venues_to_db(all_venues_for_saving)

        return response

    except Exception as e:
        logger.error(f"Error in venue discovery endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Venue discovery failed: {str(e)}")

# Plan Generation Endpoint (DEPRECATED - keeping for backward compatibility)
@router.post("/plans/generate", response_model=dict)
async def generate_venue_plan(plan_request: dict):
    """
    DEPRECATED: Generate a comprehensive venue plan based on Planning Service request.
    
    This endpoint is deprecated. Use /venues/discover for venue discovery and 
    let the Planning Service handle plan creation.
    """
    try:
        # Validate required fields
        required_fields = ["user_id", "plan_id", "venue_types", "location"]
        for field in required_fields:
            if field not in plan_request:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )

        # Generate the plan (calls Google Places)
        logger.info("Starting plan generation...")
        plan_response = await plan_generator.generate_plan(plan_request)
        logger.info(f"Plan generated. Keys: {list(plan_response.keys()) if plan_response else 'None'}")

        # Pick the right key for venues (normalize possible variations)
        venues_to_save = (
            plan_response.get("venues")
            or plan_response.get("suggested_venues")
            or plan_response.get("venues_list")
        )

        # Save to Mongo if venues found
        if venues_to_save:
            logger.info(f"Discovered {len(venues_to_save)} venues, saving to MongoDB...")
            await save_discovered_venues_to_db(venues_to_save)
            logger.info("Save function completed")
        else:
            logger.warning("⚠️ No venues found in plan response")

        return plan_response

    except Exception as e:
        logger.error(f"Error in plan generation endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")








# Venue endpoints
@router.post("/venues", response_model=Venue, status_code=status.HTTP_201_CREATED)
async def create_venue(venue: VenueCreate):
    """Create a new venue"""
    venues_collection = get_venues_collection()
    
    venue_data = venue.dict()
    venue_data["created_at"] = datetime.utcnow()
    venue_data["updated_at"] = datetime.utcnow()
    
    result = venues_collection.insert_one(venue_data)
    venue_data["id"] = str(result.inserted_id)
    
    return Venue(**venue_data)

@router.get("/venues", response_model=PaginatedResponse)
async def get_venues(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    venue_type: Optional[VenueType] = Query(None, description="Filter by venue type"),
    city: Optional[str] = Query(None, description="Filter by city"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating")
):
    """Get all venues with optional filtering and pagination"""
    venues_collection = get_venues_collection()
    
    # Build filter
    filter_query = {}
    if venue_type:
        filter_query["venue_type"] = venue_type
    if city:
        filter_query["location.city"] = {"$regex": city, "$options": "i"}
    if min_rating is not None:
        filter_query["rating"] = {"$gte": min_rating}
    
    # Get total count
    total = venues_collection.count_documents(filter_query)
    
    # Get paginated results
    skip = (page - 1) * size
    venues_cursor = venues_collection.find(filter_query).skip(skip).limit(size)
    
    venues = []
    for venue_doc in venues_cursor:
        venue_doc["id"] = str(venue_doc["_id"])
        venues.append(Venue(**venue_doc))
    
    return PaginatedResponse(
        items=venues,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )

@router.get("/venues/{venue_id}", response_model=Venue)
async def get_venue(venue_id: str = Path(..., description="Venue ID")):
    """Get a specific venue by ID"""
    return get_venue_by_id(venue_id)

@router.put("/venues/{venue_id}", response_model=Venue)
async def update_venue(
    venue_update: VenueUpdate,
    venue_id: str = Path(..., description="Venue ID")
):
    """Update an existing venue"""
    venues_collection = get_venues_collection()
    
    try:
        update_data = venue_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        result = venues_collection.update_one(
            {"_id": ObjectId(venue_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Venue not found")
        
        # Return updated venue
        venue_doc = venues_collection.find_one({"_id": ObjectId(venue_id)})
        venue_doc["id"] = str(venue_doc["_id"])
        return Venue(**venue_doc)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail="Invalid venue ID")

@router.delete("/venues/{venue_id}", response_model=MessageResponse)
async def delete_venue(venue_id: str = Path(..., description="Venue ID")):
    """Delete a venue"""
    venues_collection = get_venues_collection()
    
    try:
        # Get venue name before deletion for response message
        venue_doc = venues_collection.find_one({"_id": ObjectId(venue_id)})
        if not venue_doc:
            raise HTTPException(status_code=404, detail="Venue not found")
        
        venue_name = venue_doc.get("name", "Unknown")
        
        # Delete the venue
        result = venues_collection.delete_one({"_id": ObjectId(venue_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Venue not found")
        
        return MessageResponse(
            message=f"Venue '{venue_name}' deleted successfully",
            success=True
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail="Invalid venue ID")

# Link management endpoints
@router.post("/venues/{venue_id}/links", response_model=Venue, status_code=status.HTTP_200_OK)
async def add_venue_link(
    link: VenueLink,
    venue_id: str = Path(..., description="Venue ID")
):
    """Add a new link to a venue"""
    venues_collection = get_venues_collection()
    
    try:
        # Get current venue
        venue_doc = venues_collection.find_one({"_id": ObjectId(venue_id)})
        if not venue_doc:
            raise HTTPException(status_code=404, detail="Venue not found")
        
        # Add link to venue
        if "links" not in venue_doc:
            venue_doc["links"] = []
        
        venue_doc["links"].append(link.dict())
        venue_doc["updated_at"] = datetime.utcnow()
        
        # Update venue in database
        venues_collection.update_one(
            {"_id": ObjectId(venue_id)},
            {"$set": {"links": venue_doc["links"], "updated_at": venue_doc["updated_at"]}}
        )
        
        venue_doc["id"] = str(venue_doc["_id"])
        return Venue(**venue_doc)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail="Invalid venue ID")

@router.put("/venues/{venue_id}/links/{link_index}", response_model=Venue)
async def update_venue_link(
    link: VenueLink,
    venue_id: str = Path(..., description="Venue ID"),
    link_index: int = Path(..., ge=0, description="Index of the link to update")
):
    """Update a specific link for a venue"""
    venues_collection = get_venues_collection()
    
    try:
        # Get current venue
        venue_doc = venues_collection.find_one({"_id": ObjectId(venue_id)})
        if not venue_doc:
            raise HTTPException(status_code=404, detail="Venue not found")
        
        if "links" not in venue_doc or link_index >= len(venue_doc["links"]):
            raise HTTPException(status_code=404, detail="Link not found")
        
        # Update link
        venue_doc["links"][link_index] = link.dict()
        venue_doc["updated_at"] = datetime.utcnow()
        
        # Update venue in database
        venues_collection.update_one(
            {"_id": ObjectId(venue_id)},
            {"$set": {"links": venue_doc["links"], "updated_at": venue_doc["updated_at"]}}
        )
        
        venue_doc["id"] = str(venue_doc["_id"])
        return Venue(**venue_doc)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail="Invalid venue ID")

@router.delete("/venues/{venue_id}/links/{link_index}", response_model=Venue)
async def delete_venue_link(
    venue_id: str = Path(..., description="Venue ID"),
    link_index: int = Path(..., description="Index of the link to delete")
):
    """Delete a specific link from a venue"""
    venues_collection = get_venues_collection()
    
    try:
        # Get current venue
        venue_doc = venues_collection.find_one({"_id": ObjectId(venue_id)})
        if not venue_doc:
            raise HTTPException(status_code=404, detail="Venue not found")
        
        if "links" not in venue_doc or link_index >= len(venue_doc["links"]):
            raise HTTPException(status_code=404, detail="Link not found")
        
        # Remove link
        deleted_link = venue_doc["links"].pop(link_index)
        venue_doc["updated_at"] = datetime.utcnow()
        
        # Update venue in database
        venues_collection.update_one(
            {"_id": ObjectId(venue_id)},
            {"$set": {"links": venue_doc["links"], "updated_at": venue_doc["updated_at"]}}
        )
        
        venue_doc["id"] = str(venue_doc["_id"])
        return Venue(**venue_doc)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail="Invalid venue ID")

@router.get("/venues/{venue_id}/links", response_model=List[VenueLink])
async def get_venue_links(venue_id: str = Path(..., description="Venue ID")):
    """Get all links for a specific venue"""
    venue = get_venue_by_id(venue_id)
    return venue.links or []


# Utility endpoints
@router.get("/venue-types", response_model=List[str])
async def get_venue_types():
    """Get all available venue types"""
    return [vt.value for vt in VenueType]

@router.get("/health", response_model=MessageResponse)
async def health_check():
    """Health check endpoint"""
    return MessageResponse(
        message="Venues Service is running",
        success=True
    )

@router.get("/stats", response_model=dict)
async def get_service_stats():
    """Get service statistics"""
    venues_collection = get_venues_collection()
    
    # Get total venues count
    total_venues = venues_collection.count_documents({})
    
    # Get venue types distribution
    venue_types = {}
    for vt in VenueType:
        count = venues_collection.count_documents({"venue_type": vt.value})
        venue_types[vt.value] = count
    
    return {
        "total_venues": total_venues,
        "venue_types": venue_types
    }

