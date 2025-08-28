"""
Plan generation service for creating comprehensive venue plans
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging
import random
import hashlib
import time

from app.models.schemas import Venue, UserPreferences, VenueType, Location, VenueLink
from app.services.personalization import personalization_service
from app.services.planning_integration import planning_integration
from app.services.planning_service_client import planning_service_client
from app.services.place_finder import search_places, get_place_details
from app.core.config import VENUES_PER_TYPE

logger = logging.getLogger(__name__)

class PlanGenerator:
    """Service for generating comprehensive venue plans with randomization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def _generate_randomness_seed(self, plan_request: Dict[str, Any]) -> int:
        """
        Generate a pseudo-random seed based on current time and request hash
        This ensures different results for identical requests at different times
        """
        # Use current timestamp for time-based randomness
        current_time = int(time.time() * 1000)  # milliseconds for better granularity
        
        # Create a hash from request parameters (excluding timestamp-sensitive fields)
        request_hash_data = {
            "user_id": plan_request.get("user_id"),
            "venue_types": sorted(plan_request.get("venue_types", [])),  # sort for consistency
            "location": plan_request.get("location", {}),
            "group_size": plan_request.get("group_size"),
            "budget_range": plan_request.get("budget_range"),
            "use_personalization": plan_request.get("use_personalization", True)
        }
        
        # Convert to string and hash
        request_str = str(sorted(request_hash_data.items()))
        request_hash = hashlib.md5(request_str.encode()).hexdigest()
        
        # Combine time and request hash for seed
        seed = current_time + int(request_hash[:8], 16)
        return seed
    
    def _apply_controlled_randomness(self, venues: List[Venue], seed: int, selection_factor: float = 0.7) -> List[Venue]:
        """
        Apply controlled randomness to venue list while maintaining quality
        
        Args:
            venues: List of venues (assumed to be pre-sorted by quality/personalization)
            seed: Random seed for reproducible randomness within this request
            selection_factor: Factor determining how much of the top venues to consider (0.7 = top 70%)
        
        Returns:
            Randomly shuffled list with bias toward higher-quality venues
        """
        if not venues:
            return venues
            
        # Set random seed for this operation
        random.seed(seed)
        
        # Take top selection_factor of venues for primary selection
        top_count = max(1, int(len(venues) * selection_factor))
        top_venues = venues[:top_count]
        remaining_venues = venues[top_count:]
        
        # Shuffle top venues (these are most likely to be selected)
        random.shuffle(top_venues)
        
        # Shuffle remaining venues
        random.shuffle(remaining_venues)
        
        # Combine with bias toward top venues
        return top_venues + remaining_venues
    
    async def generate_plan(self, plan_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate multiple venue plans based on the request
        
        Args:
            plan_request: Plan request from Planning Service
            
        Returns:
            Multiple plan responses with different venue type combinations
        """
        try:
            # Extract request data
            user_id = plan_request.get("user_id")
            plan_id = plan_request.get("plan_id")
            venue_types = plan_request.get("venue_types", [])
            location = plan_request.get("location", {})
            radius_km = plan_request.get("radius_km", 10.0)
            max_venues = plan_request.get("max_venues", 5)
            use_personalization = plan_request.get("use_personalization", True)
            
            # Validate max_venues constraint
            if max_venues > len(venue_types):
                raise ValueError(f"max_venues ({max_venues}) cannot be greater than number of venue types ({len(venue_types)})")
            
            # Notify Planning Service that we're processing
            await planning_service_client.update_plan_status(
                plan_id, "processing", "Generating multiple venue plans with different combinations"
            )
            
            # Generate randomness seed for this request
            randomness_seed = self._generate_randomness_seed(plan_request)
            logger.info(f"Generated randomness seed: {randomness_seed}")
            
            # Get user preferences if personalization is enabled
            user_preferences = None
            if use_personalization:
                user_preferences = await planning_integration.get_user_preferences(user_id)
            
            # Discover venues for each requested type (exactly VENUES_PER_TYPE per type)
            venues_by_type = {}
            total_venues_found = 0
            
            for venue_type in venue_types:
                venues = await self._discover_venues_for_type(
                    venue_type, location, radius_km, user_preferences, VENUES_PER_TYPE
                )
                venues_by_type[venue_type] = venues
                total_venues_found += len(venues)
                logger.info(f"Discovered {len(venues)} venues for type {venue_type}")
            
            # Apply personalization and ranking within each venue type
            if user_preferences and use_personalization:
                for venue_type in venues_by_type:
                    venues = venues_by_type[venue_type]
                    ranked_venues = personalization_service.personalize_venue_list(
                        venues, user_preferences
                    )
                    # Extract venues and scores, keep top VENUES_PER_TYPE
                    top_venues = [venue for venue, score in ranked_venues[:VENUES_PER_TYPE]]
                    
                    # Apply controlled randomness to the personalized venues
                    venues_by_type[venue_type] = self._apply_controlled_randomness(
                        top_venues, randomness_seed + hash(venue_type)
                    )
            else:
                # Apply randomness even without personalization
                for venue_type in venues_by_type:
                    venues_by_type[venue_type] = self._apply_controlled_randomness(
                        venues_by_type[venue_type], randomness_seed + hash(venue_type)
                    )
            
            # Generate multiple plans with different venue type combinations
            all_plans = await self._generate_multiple_plans(venues_by_type, max_venues, plan_request, randomness_seed)
            
            # Create the final response
            response = {
                "plan_id": plan_request.get("plan_id"),
                "user_id": plan_request.get("user_id"),
                "total_plans_generated": len(all_plans),
                "plans": all_plans,
                "total_venues_found": total_venues_found,
                "generated_at": datetime.utcnow().isoformat(),
                "status": "completed",
                "message": f"Successfully generated {len(all_plans)} plans with {max_venues} venues each from {len(venue_types)} categories"
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating plan: {e}")
            # Update status to failed
            await planning_service_client.update_plan_status(
                plan_request.get("plan_id"), "failed", f"Error: {str(e)}"
            )
            raise
    
    async def _discover_venues_for_type(
        self, 
        venue_type: str, 
        location: Dict[str, Any], 
        radius_km: float,
        user_preferences: Optional[UserPreferences],
        max_venues_per_type: int
    ) -> List[Venue]:
        """
        Discover venues for a specific type using Google Places API
        
        Args:
            venue_type: Type of venue to search for
            location: Location coordinates and address
            radius_km: Search radius in kilometers
            user_preferences: User preferences for filtering
            max_venues_per_type: Maximum number of venues to discover for each type
            
        Returns:
            List of discovered venues (limited to max_venues_per_type)
        """
        try:
            # Extract location coordinates
            lat = location.get("latitude")
            lng = location.get("longitude")
            
            if not lat or not lng:
                logger.warning(f"Missing coordinates for venue type {venue_type}")
                return []
            
            # Convert radius to meters (Google Places API uses meters)
            radius_meters = int(radius_km * 1000)
            
            # Map venue types to Google Places API types
            google_place_type = self._map_venue_type_to_google(venue_type)
            
            # Search for places using Google Places API
            # Request more results than we need to ensure quality selection
            places = search_places(
                lat=lat,
                lng=lng,
                place_type=google_place_type,
                keyword=venue_type.replace("_", " "),
                radius=radius_meters,
                max_results=30  # Request up to 30 to ensure we have quality venues to choose from
            )
            
            if not places:
                logger.info(f"No places found for venue type {venue_type}")
                return []
            
            # Limit to max_venues_per_type (Google API might return more)
            places = places[:max_venues_per_type]
            
            # Convert Google Places to Venue objects
            venues = []
            for place in places:
                try:
                    venue = await self._convert_google_place_to_venue(place, venue_type)
                    if venue:
                        venues.append(venue)
                        # Stop if we've reached the limit
                        if len(venues) >= max_venues_per_type:
                            break
                except Exception as e:
                    logger.error(f"Error converting place {place.get('place_id')}: {e}")
                    continue
            
            logger.info(f"Discovered {len(venues)} venues for type {venue_type} (limited to {max_venues_per_type})")
            return venues
            
        except Exception as e:
            logger.error(f"Error discovering venues for type {venue_type}: {e}")
            return []
    
    def _map_venue_type_to_google(self, venue_type: str) -> str:
        """Map our venue types to Google Places API types"""
        type_mapping = {
            "restaurant": "restaurant",
            "cafe": "cafe",
            "bar": "bar",
            "museum": "museum",
            "theater": "movie_theater",  # Google uses movie_theater
            "park": "park",
            "shopping_center": "shopping_mall",
            "sports_facility": "gym",  # Google uses gym
            "hotel": "lodging",
            "other": "establishment"  # Generic establishment
        }
        return type_mapping.get(venue_type, "establishment")
    
    async def _convert_google_place_to_venue(self, place: Dict[str, Any], venue_type: str) -> Optional[Venue]:
        """
        Convert Google Place data to Venue object
        
        Args:
            place: Google Place data
            venue_type: The type of venue this represents
            
        Returns:
            Venue object if successful, None otherwise
        """
        try:
            place_id = place.get("place_id")
            if not place_id:
                return None
            
            # Get additional details for the place
            details = get_place_details(place_id)
            
            # Extract location data
            geometry = place.get("geometry", {})
            location_data = geometry.get("location", {})
            
            # Create Location object
            location = Location(
                latitude=location_data.get("lat", 0.0),
                longitude=location_data.get("lng", 0.0),
                address=place.get("vicinity", ""),
                city=self._extract_city_from_vicinity(place.get("vicinity", "")),
                country="Unknown"  # Google Places API doesn't always provide country
            )
            
            # Extract rating and price level
            rating = place.get("rating")
            price_level = place.get("price_level")
            price_range = self._convert_price_level_to_range(price_level)
            
            # Extract amenities from place types
            amenities = self._extract_amenities_from_types(place.get("types", []))
            
            # Create venue links
            links = []
            
            # Add official website if available
            website = details.get("website")
            if website:
                links.append(VenueLink(
                    type="website",
                    url=website,
                    title="Official Website",
                    description="Official website"
                ))
            
      
            # Create Venue object
            venue = Venue(
                id=str(uuid.uuid4()),  # Generate new UUID
                name=place.get("name", "Unknown Venue"),
                description=f"Discovered via Google Places API",
                venue_type=VenueType(venue_type),
                location=location,
                rating=rating,
                price_range=price_range,
                amenities=amenities,
                links=links,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return venue
            
        except Exception as e:
            logger.error(f"Error converting Google place to venue: {e}")
            return None
    
    def _extract_city_from_vicinity(self, vicinity: str) -> str:
        """Extract city name from Google Places vicinity string"""
        if not vicinity:
            return "Unknown"
        
        # Vicinity usually contains neighborhood, city, state
        # Try to extract city (usually the second part)
        parts = vicinity.split(", ")
        if len(parts) >= 2:
            return parts[1]  # Second part is usually city
        elif len(parts) == 1:
            return parts[0]  # Only one part
        else:
            return "Unknown"
    
    def _convert_price_level_to_range(self, price_level: Optional[int]) -> Optional[str]:
        """Convert Google Places price level to our price range format"""
        if price_level is None:
            return None
        
        price_mapping = {
            0: "$",      # Free
            1: "$",      # Inexpensive
            2: "$$",     # Moderate
            3: "$$$",    # Expensive
            4: "$$$"     # Very Expensive
        }
        return price_mapping.get(price_level, "$$")
    
    def _extract_amenities_from_types(self, place_types: List[str]) -> List[str]:
        """Extract amenities from Google Places types"""
        amenities = []
        
        # Map Google place types to amenities
        type_to_amenity = {
            "wheelchair_accessible_entrance": "wheelchair_accessible",
            "parking": "parking",
            "wifi": "wifi",
            "outdoor_seating": "outdoor_seating",
            "delivery": "delivery",
            "takeout": "takeout",
            "reservations": "reservations",
            "live_music": "live_music",
            "family_friendly": "family_friendly",
            "romantic": "romantic",
            "casual": "casual",
            "upscale": "upscale"
        }
        
        for place_type in place_types:
            if place_type in type_to_amenity:
                amenities.append(type_to_amenity[place_type])
        
        return amenities

    async def _generate_multiple_plans(self, venues_by_type: Dict[str, List[Venue]], max_venues: int, plan_request: Dict[str, Any], randomness_seed: int) -> List[Dict[str, Any]]:
        """
        Generate exactly 3 different venue plans with balanced venue types.
        
        Requirements:
        1. Each plan has different venue types (balanced distribution)
        2. Each plan has different specific venues (no duplicates across plans)
        3. Max venues ≤ Number of venue types selected
        4. Balanced venue type distribution in each plan
        """
        all_plans = []
        venue_types = list(venues_by_type.keys())
        
        # Track which venues have been used to avoid duplicates across plans
        used_venues = set()
        
        # Always create exactly 3 plans with balanced venue types
        for plan_index in range(3):
            venues_for_plan = []
            types_used = []
            
            # Use randomness to create different venue type selections for each plan
            random.seed(randomness_seed + plan_index)  # Different seed for each plan
            
            # Create different type selection strategies with randomness
            if plan_index == 0:
                # First plan: use first max_venues types but with some randomness
                selected_types = venue_types[:max_venues]
            elif plan_index == 1:
                # Second plan: use middle max_venues types
                start = (len(venue_types) - max_venues) // 2
                selected_types = venue_types[start:start + max_venues]
            else:
                # Third plan: use last max_venues types
                selected_types = venue_types[-max_venues:]
            
            # Shuffle the selected types for variety
            selected_types = list(selected_types)
            random.shuffle(selected_types)
            
            # Track venue categories used in this specific plan to prevent duplicates
            categories_used_in_plan = set()
            
            # Get venues for each selected venue type
            for venue_type in selected_types:
                # Skip if we've already used this category in this plan
                if venue_type in categories_used_in_plan:
                    continue
                    
                # Find unused venues of this type
                available_venues = [v for v in venues_by_type[venue_type] if v.id not in used_venues]
                if available_venues:
                    # Instead of always taking the first, select randomly from top venues
                    # This adds randomness while still favoring quality venues
                    selection_count = min(3, len(available_venues))  # Consider top 3 available venues
                    top_available = available_venues[:selection_count]
                    selected_venue = random.choice(top_available)
                    
                    venues_for_plan.append(selected_venue)
                    used_venues.add(selected_venue.id)
                    types_used.append(venue_type)
                    categories_used_in_plan.add(venue_type)  # Track category usage in this plan
                    
                    # If we've reached max_venues, stop adding more
                    if len(venues_for_plan) >= max_venues:
                        break
            
            # Create the plan if we have venues
            if venues_for_plan:
                plan = await self._create_single_plan(
                    venues_for_plan,
                    types_used,
                    f"{plan_request.get('plan_id')}-plan{plan_index+1}",
                    plan_request
                )
                all_plans.append(plan)
        
        # If we don't have 3 plans yet, create additional plans with remaining venues
        while len(all_plans) < 3:
            plan_index = len(all_plans)
            venues_for_plan = []
            types_used = []
            
            # Set random seed for this fallback plan
            random.seed(randomness_seed + plan_index + 100)  # +100 to differentiate from main plans
            
            # Track venue categories used in this specific fallback plan to prevent duplicates
            categories_used_in_plan = set()
            
            # Try to create a plan with remaining unused venues
            for venue_type, venues in venues_by_type.items():
                # Skip if we've already used this category in this plan
                if venue_type in categories_used_in_plan:
                    continue
                    
                unused = [v for v in venues if v.id not in used_venues]
                if unused and len(venues_for_plan) < max_venues:
                    # Add randomness to fallback selection too
                    selected_venue = random.choice(unused) if len(unused) > 1 else unused[0]
                    venues_for_plan.append(selected_venue)
                    used_venues.add(selected_venue.id)
                    types_used.append(venue_type)
                    categories_used_in_plan.add(venue_type)  # Track category usage in this plan
            
            if venues_for_plan:
                plan = await self._create_single_plan(
                    venues_for_plan,
                    types_used,
                    f"{plan_request.get('plan_id')}-plan{plan_index+1}",
                    plan_request
                )
                all_plans.append(plan)
            else:
                # If no more unused venues, break to avoid infinite loop
                break
        
        return all_plans[:3]  # Return exactly 3 plans

    async def _create_single_plan(self, venues: List[Venue], venue_types: List[str], plan_id: str, plan_request: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method to create a single plan with the given venues"""
        
        # Validate that all venue categories are unique within this plan
        venue_categories = [venue.venue_type.value for venue in venues]
        unique_categories = set(venue_categories)
        if len(venue_categories) != len(unique_categories):
            logger.warning(f"Plan {plan_id} contains duplicate venue categories: {venue_categories}")
            # Log but don't fail - this shouldn't happen with our new logic but good to catch
        
        # Calculate total duration (assuming 1 hour per venue + travel time)
        total_duration = len(venues) * 1.0  # Base duration per venue
        
        # Create simplified venue structure with only essential fields
        simplified_venues = []
        for i, venue in enumerate(venues):
            # Get the first website link if available, otherwise null
            url_link = None
            if venue.links and len(venue.links) > 0:
                url_link = venue.links[0].get('url') if hasattr(venue.links[0], 'get') else venue.links[0].url
            
            simplified_venue = {
                "venue_id": venue.id,
                "name": venue.name,
                "venue_type": venue.venue_type.value,
                "location": {
                    "latitude": venue.location.latitude,
                    "longitude": venue.location.longitude
                },
                "rating": venue.rating,
                "price_range": venue.price_range,
                "amenities": venue.amenities or [],
                "address": venue.location.address,
                "url_link": url_link
            }
            simplified_venues.append(simplified_venue)
        
        # Create simplified plan structure
        plan = {
            "plan_id": plan_id,
            "user_id": plan_request.get('user_id'),
            "suggested_venues": simplified_venues,
            "venue_types_included": venue_types,
            "estimated_total_duration": total_duration,
            "personalization_applied": plan_request.get('use_personalization', False),
            "generated_at": datetime.utcnow().isoformat(),
            "status": "completed",
            "message": f"Plan with {len(venues)} venues from {len(venue_types)} venue types"
        }
        
        return plan

# Global instance
plan_generator = PlanGenerator() 