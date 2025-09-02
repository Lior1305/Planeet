from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from typing import List, Optional
from datetime import datetime
import uuid
import logging
import httpx  # Add this import
from bson import ObjectId
from datetime import datetime
from typing import List, Dict
import os
import asyncio


from app.models.schemas import (
    Venue, VenueCreate, VenueUpdate, VenueLink,
    MessageResponse, PaginatedResponse,
    VenueType,
    VenueDiscoveryRequest, VenueDiscoveryResponse
)

# Initialize router
router = APIRouter(prefix="/api/v1", tags=["venues"])

# Initialize logger
logger = logging.getLogger(__name__)

# Import database storage and services
from ..db import get_venues_collection  # ✅ Use relative import


from app.services.venue_discovery import venue_discovery

# Add this function after the imports and before the other functions
async def generate_time_slots_for_venue(venue_id: str, venue_name: str) -> bool:
    """
    Generate time slots for a venue by calling the booking service
    """
    try:
        # Get the booking service URL from environment or use the correct internal service name
        booking_service_url = os.getenv("BOOKING_SERVICE_URL", "http://booking-service:8004")
        
        logger.info(f"🔗 Calling booking service at: {booking_service_url}")
        
        # First, check if the booking service is healthy
        try:
            async with httpx.AsyncClient(timeout=10.0) as health_client:
                health_response = await health_client.get(f"{booking_service_url}/health")
                if health_response.status_code != 200:
                    logger.warning(f"⚠️ Booking service health check failed: {health_response.status_code}")
                    return False
                logger.info(f"✅ Booking service is healthy")
        except Exception as health_error:
            logger.warning(f"⚠️ Health check failed: {health_error}")
            # Continue anyway, the service might be starting up
        
        # Make HTTP request to booking service with better timeout configuration
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=15.0,    # Connection timeout
                read=60.0,       # Read timeout (longer for time slot generation)
                write=15.0,      # Write timeout
                pool=30.0        # Pool timeout
            )
        ) as client:
            logger.info(f"📤 Sending time slot generation request for venue: {venue_name}")
            
            response = await client.post(
                f"{booking_service_url}/generate-time-slots",   # ✅ FIXED
                json={"venue_id": venue_id, "default_counter": 100},
                 headers={"Content-Type": "application/json"}
        )

            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Time slots generated for {venue_name}: {result.get('message', 'Success')}")
                return True
            else:
                logger.error(f"❌ Failed to generate time slots for {venue_name}: {response.status_code} - {response.text}")
                return False
                
    except httpx.TimeoutException as timeout_error:
        logger.error(f"⏰ Timeout calling booking service for {venue_name}: {timeout_error}")
        return False
    except httpx.ConnectError as connect_error:
        logger.error(f"🔌 Connection error to booking service for {venue_name}: {connect_error}")
        return False
    except Exception as e:
        logger.error(f"❌ Error calling booking service for {venue_name}: {e}")
        return False



# --- generate_time_slots_for_venue ---
async def generate_time_slots_for_venue(venue_id: str, venue_name: str) -> bool:
    """
    Generate time slots for a venue by calling the booking service
    """
    try:
        booking_service_url = os.getenv("BOOKING_SERVICE_URL", "http://booking-service:8004")
        logger.info(f"🔗 Calling booking service at: {booking_service_url}")

        # Health check
        try:
            async with httpx.AsyncClient(timeout=10.0) as health_client:
                health_response = await health_client.get(f"{booking_service_url}/v1/health")  # ✅ with /v1
                if health_response.status_code != 200:
                    logger.warning(f"⚠️ Booking service health check failed: {health_response.status_code}")
                    return False
                logger.info("✅ Booking service is healthy")
        except Exception as health_error:
            logger.warning(f"⚠️ Health check failed: {health_error}")
            # Continue anyway

        # Call booking service
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(connect=15.0, read=60.0, write=15.0, pool=30.0)
        ) as client:
            logger.info(f"📤 Sending time slot generation request for venue: {venue_name}")

            response = await client.post(
                f"{booking_service_url}/v1/generate-time-slots",   # ✅ with /v1
                json={"venue_id": venue_id, "default_counter": 100},
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Time slots generated for {venue_name}: {result.get('message', 'Success')}")
                return True
            else:
                logger.error(
                    f"❌ Failed to generate time slots for {venue_name}: "
                    f"{response.status_code} - {response.text}"
                )
                return False

    except httpx.TimeoutException as timeout_error:
        logger.error(f"⏰ Timeout calling booking service for {venue_name}: {timeout_error}")
        return False
    except httpx.ConnectError as connect_error:
        logger.error(f"🔌 Connection error to booking service for {venue_name}: {connect_error}")
        return False
    except Exception as e:
        logger.error(f"❌ Error calling booking service for {venue_name}: {e}")
        return False


# --- debug_booking_service_connectivity ---
async def debug_booking_service_connectivity():
    """
    Debug function to test booking service connectivity
    """
    booking_service_url = os.getenv("BOOKING_SERVICE_URL", "http://booking-service:8004")
    logger.info(f"🔍 Debugging connectivity to: {booking_service_url}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{booking_service_url}/v1/health")  # ✅ with /v1
            logger.info(f"✅ Health check: {response.status_code}")
            logger.info(f"📄 Response: {response.text}")
            return True
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False

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
        "opening_hours": venue.get("opening_hours", {"open_at": "", "close_at": ""}),
        "time_slots": venue.get("time_slots", []),  # Add this line to preserve time_slots
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

# --- Save discovered venues directly into Mongo ---
async def save_discovered_venues_to_db(venues: List[dict]):
    logger.info(f"Starting to save {len(venues)} venues to MongoDB")
    venues_collection = get_venues_collection()
    saved_venues = []
    time_slots_generated = 0

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
            
            # Add the saved venue to our list with the MongoDB _id
            saved_venue = venue_data.copy()
            saved_venue["_id"] = result.inserted_id
            saved_venues.append(saved_venue)
            
            logger.info(f"Saved venue: {venue_data['venue_name']} (ID: {result.inserted_id})")
            
            # Generate time slots immediately after saving
            venue_name = venue_data.get('venue_name', 'Unknown')
            
            try:
                # Call the function that makes HTTP request to booking service with retry
                logger.info(f"🔄 Starting time slot generation for venue: {venue_name} (ID: {result.inserted_id})")
                
                time_slots_result = await generate_time_slots_for_venue(str(result.inserted_id), venue_name)
                
                if time_slots_result:
                    time_slots_generated += 1
                    logger.info(f"✅ Time slots generated for: {venue_name}")
                    
                    # 🔍 DEBUG: Verify the time slots were actually saved
                    try:
                        updated_venue = venues_collection.find_one({"_id": result.inserted_id})
                        if updated_venue and updated_venue.get("time_slots"):
                            logger.info(f"✅ Verified: {len(updated_venue['time_slots'])} time slots saved for {venue_name}")
                        else:
                            logger.warning(f"⚠️ Time slots not found in database for {venue_name} after generation")
                    except Exception as verify_error:
                        logger.error(f"❌ Error verifying time slots for {venue_name}: {verify_error}")
                else:
                    logger.warning(f"⚠️ Failed to generate time slots for {venue_name} after all retries")
                    
            except Exception as e:
                logger.error(f"❌ Error generating time slots for {venue_name}: {e}")

        except Exception as e:
            logger.error(f"❌ Failed to save venue {venue.get('venue_name', venue.get('name'))}: {e}")
            continue

    logger.info(f"Successfully saved {len(saved_venues)} new venues")
    logger.info(f"✅ Generated time slots for {time_slots_generated} venues")
    return saved_venues



# Venue Discovery Endpoint (NEW!)
@router.post("/venues/discover", response_model=VenueDiscoveryResponse)
async def discover_venues(venue_request: VenueDiscoveryRequest):
    """
    Discover venues from Google Places API based on request criteria.
    
    This endpoint handles venue discovery, saves venues to MongoDB,
    and automatically generates time slots via the booking service.
    """
    try:
        # 🔍 DEBUG: Test booking service connectivity first
        logger.info("🔍 Testing booking service connectivity before venue discovery...")
        connectivity_ok = await debug_booking_service_connectivity()
        if not connectivity_ok:
            logger.warning("⚠️ Booking service connectivity test failed - time slots may not be generated")
        
        # Extract request data
        venue_types = venue_request.venue_types
        location = venue_request.location.dict()
        radius_km = venue_request.radius_km
        
        logger.info(f"Starting venue discovery for types: {venue_types}")
        

        
        # Discover venues for each requested type
        venues_by_type = {}
        total_venues_found = 0
        
        for venue_type in venue_types:
            venues = await venue_discovery.discover_venues_for_type(
                venue_type, location, radius_km, 10  # Get more venues for planning service to choose from
            )
            
            # No personalization here - planning service will handle it
            # Just return raw venue data for the planning service to process
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
            discovered_at=datetime.utcnow().isoformat()
        )

        # Save discovered venues to MongoDB (time slots will be generated automatically)
        all_venues_for_saving = []
        for venues in venues_by_type.values():
            for venue in venues:
                venue_dict = {
                    "id": venue.id,  # Google place_id
                    "venue_name": venue.name,
                    "venue_type": venue.venue_type.value,
                    "opening_hours": venue.opening_hours if hasattr(venue, 'opening_hours') else {"open_at": "", "close_at": ""},
                    "time_slots": []
                }
                all_venues_for_saving.append(venue_dict)

        if all_venues_for_saving:
            logger.info(f"Saving {len(all_venues_for_saving)} discovered venues to MongoDB...")
            saved_venues = await save_discovered_venues_to_db(all_venues_for_saving)
            logger.info(f"✅ Venue discovery and time slot generation completed for {len(saved_venues)} venues")

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
        # plan_response = await plan_generator.generate_plan(plan_request) # plan_generator is not defined
        # logger.info(f"Plan generated. Keys: {list(plan_response.keys()) if plan_response else 'None'}")

        # Pick the right key for venues (normalize possible variations)
        venues_to_save = (
            # plan_response.get("venues") # plan_response is not defined
            # or plan_response.get("suggested_venues")
            # or plan_response.get("venues_list")
        )

        # Save to Mongo if venues found
        if venues_to_save:
            logger.info(f"Discovered {len(venues_to_save)} venues, saving to MongoDB...")
            await save_discovered_venues_to_db(venues_to_save)
            logger.info("Save function completed")
        else:
            logger.warning("⚠️ No venues found in plan response")

        return {} # Return an empty dict as plan_response is not defined

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


