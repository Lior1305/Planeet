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
    VenueType, TimeSlot, TimeSlotCreate, TimeSlotUpdate, TimeSlotSearchRequest, TimeSlotSearchResponse, TimeSlotStatus
)

# Initialize router
router = APIRouter(prefix="/api/v1", tags=["venues"])

# Initialize logger
logger = logging.getLogger(__name__)

# Import database storage and services
from app.db import get_venues_collection, get_time_slots_collection
from app.services.planning_integration import planning_integration
from app.services.personalization import personalization_service
from app.services.plan_generator import plan_generator

# Helper functions
def get_venue_by_id(venue_id: str) -> Venue:
    """Get venue by ID from MongoDB"""
    venues_collection = get_venues_collection()
    
    try:
        venue_doc = venues_collection.find_one({"_id": ObjectId(venue_id)})
        if not venue_doc:
            raise HTTPException(status_code=404, detail="Venue not found")
        
        venue_doc["id"] = str(venue_doc["_id"])
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
        "name": venue.get("name", "Unknown Venue"),
        "description": venue.get("description", "Discovered via Google Places API"),
        "venue_type": venue.get("venue_type", "other"),
        "location": venue.get("location", {}),
        "rating": venue.get("rating"),
        "price_range": venue.get("price_range"),
        "opening_hours": venue.get("opening_hours"),
        "contact_info": venue.get("contact_info"),
        "amenities": venue.get("amenities", []),
        "images": venue.get("images", []),
        "links": venue.get("links", []),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

# --- Save discovered venues directly into Mongo ---
async def save_discovered_venues_to_db(venues: List[dict]):
    logger.info(f"Starting to save {len(venues)} venues to MongoDB")
    venues_collection = get_venues_collection()
    saved_count = 0

    for venue in venues:
        try:
            venue_data = normalize_venue(venue)

            # Avoid duplicates (by name + city)
            existing = venues_collection.find_one({
                "name": venue_data["name"],
                "location.city": venue_data["location"].get("city")
            })
            if existing:
                logger.info(f"Venue {venue_data['name']} already exists, skipping")
                continue

            # Insert into MongoDB
            result = venues_collection.insert_one(venue_data)
            saved_count += 1

            logger.info(f"✅ Saved venue: {venue_data['name']} (ID: {result.inserted_id})")

        except Exception as e:
            logger.error(f"❌ Failed to save venue {venue.get('name')}: {e}")
            continue

    logger.info(f"Successfully saved {saved_count} new venues")
    return saved_count



# Plan Generation Endpoint (NEW!)
@router.post("/plans/generate", response_model=dict)
async def generate_venue_plan(plan_request: dict):
    """
    Generate a comprehensive venue plan based on Planning Service request.
    
    This endpoint receives plan requests from the Planning Service and returns
    a complete plan with venue suggestions, costs, durations, and travel routes.
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


async def save_discovered_venues_to_db(venues: List[dict]):
    """
    Save discovered venues from Google Places API to MongoDB
    """
    logger.info(f"Starting to save {len(venues)} venues to MongoDB")
    
    venues_collection = get_venues_collection()
    saved_count = 0
    
    for venue in venues:
        try:
            logger.info(f"Processing venue: {venue.get('name')}")
            
            # Check if venue already exists (by name and location)
            existing_venue = venues_collection.find_one({
                "name": venue.get("name"),
                "location.city": venue.get("location", {}).get("city")
            })
            
            if existing_venue:
                logger.info(f"Venue {venue.get('name')} already exists in database, skipping")
                continue
            
            # Prepare venue data for MongoDB
            venue_data = {
                "name": venue.get("name"),
                "description": venue.get("description", f"Discovered via Google Places API"),
                "venue_type": venue.get("venue_type"),
                "location": venue.get("location"),
                "rating": venue.get("rating"),
                "price_range": venue.get("price_range"),
                "opening_hours": venue.get("opening_hours"),
                "contact_info": venue.get("contact_info"),
                "amenities": venue.get("amenities", []),
                "images": venue.get("images", []),
                "links": venue.get("links", []),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            logger.info(f"Attempting to insert venue data: {venue_data}")
            
            # Insert into MongoDB
            result = venues_collection.insert_one(venue_data)
            venue_data["_id"] = result.inserted_id
            saved_count += 1
            
            logger.info(f"Successfully saved venue to MongoDB: {venue.get('name')} (ID: {result.inserted_id})")
            
        except Exception as e:
            logger.error(f"Failed to save venue {venue.get('name')} to MongoDB: {e}")
            logger.error(f"Error details: {str(e)}")
            continue
    
    logger.info(f"Successfully saved {saved_count} new venues to MongoDB")
    return saved_count





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

# Personalized search endpoints
@router.post("/search/personalized", response_model=PersonalizedSearchResponse)
async def personalized_search_venues(request: PersonalizedSearchRequest):
    """Search for venues with personalization based on user preferences"""
    # Get user preferences from planning service
    user_preferences = None
    if request.use_preferences:
        user_preferences = await planning_integration.get_user_preferences(request.user_id)
    
    # Perform base search
    matching_venues = await _perform_base_search(request)
    
    # Apply personalization if preferences are available
    if user_preferences and request.use_preferences:
        # Personalize the venue list
        personalized_venues = personalization_service.personalize_venue_list(matching_venues, user_preferences)
        
        # Extract venues and scores
        venues_with_scores = personalized_venues
        venues = [venue for venue, score in venues_with_scores]
        
        # Calculate average personalization score
        if venues_with_scores:
            avg_score = sum(score for _, score in venues_with_scores) / len(venues_with_scores)
        else:
            avg_score = 0.0
    else:
        venues = matching_venues
        avg_score = None
    
    # Apply pagination
    total_count = len(venues)
    limit = request.limit or 20
    offset = request.offset or 0
    
    paginated_venues = venues[offset:offset + limit]
    has_more = offset + limit < total_count
    
    return PersonalizedSearchResponse(
        venues=paginated_venues,
        total_count=total_count,
        has_more=has_more,
        user_preferences_used=user_preferences,
        personalization_score=avg_score
    )

@router.get("/recommendations/{user_id}", response_model=List[Venue])
async def get_personalized_recommendations(
    user_id: str = Path(..., description="User ID"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations")
):
    """Get personalized venue recommendations for a user"""
    # Get user preferences
    user_preferences = await planning_integration.get_user_preferences(user_id)
    
    if not user_preferences:
        raise HTTPException(status_code=404, detail="No preferences found for user")
    
    # Get all venues from MongoDB
    venues_collection = get_venues_collection()
    venues_cursor = venues_collection.find({})
    
    all_venues = []
    for venue_doc in venues_cursor:
        venue_doc["id"] = str(venue_doc["_id"])
        all_venues.append(Venue(**venue_doc))
    
    # Get personalized recommendations
    recommendations = personalization_service.get_personalized_recommendations(
        all_venues, user_preferences, limit
    )
    
    # Return just the venues (without scores)
    return [venue for venue, score in recommendations]

# Search endpoints
@router.post("/search", response_model=SearchResponse)
async def search_venues(request: SearchRequest):
    """Search for venues based on criteria"""
    matching_venues = await _perform_base_search(request)
    
    # Apply pagination
    total_count = len(matching_venues)
    limit = request.limit or 20
    offset = request.offset or 0
    
    # Pagination
    paginated_venues = matching_venues[offset:offset + limit]
    has_more = offset + limit < total_count
    
    return SearchResponse(
        venues=paginated_venues,
        total_count=total_count,
        has_more=has_more
    )

@router.get("/search/quick", response_model=SearchResponse)
async def quick_search(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results")
):
    """Quick search by text query"""
    venues_collection = get_venues_collection()
    
    # Build text search query
    search_query = {
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"location.city": {"$regex": query, "$options": "i"}}
        ]
    }
    
    # Get matching venues
    venues_cursor = venues_collection.find(search_query).limit(limit)
    
    matching_venues = []
    for venue_doc in venues_cursor:
        venue_doc["id"] = str(venue_doc["_id"])
        matching_venues.append(Venue(**venue_doc))
    
    total_count = len(matching_venues)
    
    return SearchResponse(
        venues=matching_venues,
        total_count=total_count,
        has_more=False
    )

# Helper function for base search logic
async def _perform_base_search(request) -> List[Venue]:
    """Perform base search filtering logic using MongoDB"""
    venues_collection = get_venues_collection()
    
    # Build filter query
    filter_query = {}
    
    # Type filtering
    if request.venue_types:
        filter_query["venue_type"] = {"$in": request.venue_types}
    
    # Rating filtering
    if request.min_rating is not None:
        filter_query["rating"] = {"$gte": request.min_rating}
    
    # Price filtering (simplified - could be enhanced)
    if request.max_price is not None:
        # This is a simplified approach - you might want to store actual price ranges
        # or implement more sophisticated price filtering
        pass
    
    # Amenities filtering
    if request.amenities:
        filter_query["amenities"] = {"$all": request.amenities}
    
    # Get venues from MongoDB
    venues_cursor = venues_collection.find(filter_query)
    
    matching_venues = []
    for venue_doc in venues_cursor:
        venue_doc["id"] = str(venue_doc["_id"])
        venue = Venue(**venue_doc)
        
        # Location-based filtering (post-query since we need to calculate distances)
        if request.location:
            distance = calculate_distance(
                request.location.latitude, request.location.longitude,
                venue.location.latitude, venue.location.longitude
            )
            if distance > request.radius_km:
                continue
        
        # Price filtering (post-query)
        if request.max_price is not None:
            # Simple price range parsing (could be enhanced)
            if venue.price_range == "$$$" and request.max_price < 50:
                continue
            elif venue.price_range == "$$" and request.max_price < 25:
                continue
            elif venue.price_range == "$" and request.max_price < 10:
                continue
        
        matching_venues.append(venue)
    
    return matching_venues

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

# Add time slot endpoints
@router.post("/time-slots", response_model=TimeSlot, status_code=status.HTTP_201_CREATED)
async def create_time_slot(time_slot: TimeSlotCreate):
    """Create a new time slot"""
    time_slots_collection = get_time_slots_collection()
    
    time_slot_data = time_slot.dict()
    time_slot_data["created_at"] = datetime.utcnow()
    time_slot_data["updated_at"] = datetime.utcnow()
    time_slot_data["current_bookings"] = 0
    
    result = time_slots_collection.insert_one(time_slot_data)
    time_slot_data["id"] = str(result.inserted_id)
    
    return TimeSlot(**time_slot_data)

@router.get("/time-slots", response_model=TimeSlotSearchResponse)
async def search_time_slots(
    venue_id: Optional[str] = Query(None, description="Filter by venue ID"),
    date: Optional[str] = Query(None, description="Filter by date"),
    start_date: Optional[str] = Query(None, description="Filter by start date"),
    end_date: Optional[str] = Query(None, description="Filter by end date"),
    status: Optional[TimeSlotStatus] = Query(None, description="Filter by status"),
    min_capacity: Optional[int] = Query(None, description="Minimum capacity required"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    limit: int = Query(20, gt=0, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """Search time slots with filtering"""
    time_slots_collection = get_time_slots_collection()
    
    # Build filter
    filter_query = {}
    if venue_id:
        filter_query["venue_id"] = venue_id
    if date:
        filter_query["date"] = date
    if start_date and end_date:
        filter_query["date"] = {"$gte": start_date, "$lte": end_date}
    elif start_date:
        filter_query["date"] = {"$gte": start_date}
    elif end_date:
        filter_query["date"] = {"$lte": end_date}
    if status:
        filter_query["status"] = status
    if min_capacity:
        filter_query["capacity"] = {"$gte": min_capacity}
    if max_price:
        filter_query["price"] = {"$lte": max_price}
    
    # Get total count
    total = time_slots_collection.count_documents(filter_query)
    
    # Get paginated results
    time_slots_cursor = time_slots_collection.find(filter_query).skip(offset).limit(limit)
    
    time_slots = []
    for slot_doc in time_slots_cursor:
        slot_doc["id"] = str(slot_doc["_id"])
        time_slots.append(TimeSlot(**slot_doc))
    
    return TimeSlotSearchResponse(
        time_slots=time_slots,
        total_count=total,
        has_more=offset + limit < total
    )

@router.get("/time-slots/{time_slot_id}", response_model=TimeSlot)
async def get_time_slot(time_slot_id: str = Path(..., description="Time slot ID")):
    """Get a specific time slot by ID"""
    time_slots_collection = get_time_slots_collection()
    
    try:
        slot_doc = time_slots_collection.find_one({"_id": ObjectId(time_slot_id)})
        if not slot_doc:
            raise HTTPException(status_code=404, detail="Time slot not found")
        
        slot_doc["id"] = str(slot_doc["_id"])
        return TimeSlot(**slot_doc)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid time slot ID")

@router.put("/time-slots/{time_slot_id}", response_model=TimeSlot)
async def update_time_slot(
    time_slot_id: str = Path(..., description="Time slot ID"),
    time_slot_update: TimeSlotUpdate = None
):
    """Update a time slot"""
    time_slots_collection = get_time_slots_collection()
    
    try:
        update_data = time_slot_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        result = time_slots_collection.update_one(
            {"_id": ObjectId(time_slot_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Time slot not found")
        
        # Return updated time slot
        slot_doc = time_slots_collection.find_one({"_id": ObjectId(time_slot_id)})
        slot_doc["id"] = str(slot_doc["_id"])
        return TimeSlot(**slot_doc)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid time slot ID")

@router.delete("/time-slots/{time_slot_id}", response_model=MessageResponse)
async def delete_time_slot(time_slot_id: str = Path(..., description="Time slot ID")):
    """Delete a time slot"""
    time_slots_collection = get_time_slots_collection()
    
    try:
        result = time_slots_collection.delete_one({"_id": ObjectId(time_slot_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Time slot not found")
        
        return MessageResponse(message="Time slot deleted successfully", success=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid time slot ID")
