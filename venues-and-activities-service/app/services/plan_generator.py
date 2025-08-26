"""
Plan generation service for creating comprehensive venue plans
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid
import logging

from app.models.schemas import Venue, UserPreferences, VenueType, Location, VenueLink
from app.services.personalization import personalization_service
from app.services.planning_integration import planning_integration
from app.services.planning_service_client import planning_service_client
from app.services.place_finder import search_places, get_place_details, geocode_address
from app.services.ontopo_scraper import get_reservation_link
from app.core.config import VENUES_PER_TYPE, MAX_TOTAL_VENUES

logger = logging.getLogger(__name__)

class PlanGenerator:
    """Service for generating comprehensive venue plans"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
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
                    venues_by_type[venue_type] = [venue for venue, score in ranked_venues[:VENUES_PER_TYPE]]
            
            # Generate multiple plans with different venue type combinations
            all_plans = await self._generate_multiple_plans(venues_by_type, max_venues, plan_request)
            
            # Create comprehensive response
            plan_response = {
                "plan_id": plan_id,
                "user_id": user_id,
                "total_plans_generated": len(all_plans),
                "plans": all_plans,
                "total_venues_found": total_venues_found,
                "venues_by_type": venues_by_type,  # Show all discovered venues organized by type
                "search_criteria_used": {
                    "venue_types": venue_types,
                    "location": location,
                    "radius_km": radius_km,
                    "max_venues": max_venues,
                    "venues_per_type": VENUES_PER_TYPE,
                    "use_personalization": use_personalization
                },
                "generated_at": datetime.utcnow().isoformat(),
                "status": "completed",
                "message": f"Successfully generated {len(all_plans)} plans with {max_venues} venues each from {len(venue_types)} categories"
            }
            
            # Notify completion
            await planning_service_client.notify_plan_completion(plan_id, len(all_plans))
            
            return plan_response
            
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
            
            # Add Ontopo reservation link for restaurants and cafes
            # NOTE: Temporarily disabled due to MongoDB connection issues
            # TODO: Re-enable once MongoDB connection is fixed
            if venue_type in ["restaurant", "cafe"]:
                try:
                    # Temporarily disabled for testing
                    # venue_name = place.get("name", "")
                    # if venue_name:
                    #     ontopo_link = get_reservation_link(venue_name)
                    #     if ontopo_link:
                    #         links.append(VenueLink(
                    #             type="booking",
                    #             url=ontopo_link,
                    #             title="Make Reservation",
                    #             description="Book your table via Ontopo"
                    #         ))
                    #         logger.info(f"Added Ontopo reservation link for {venue_name}")
                    #     else:
                    #         logger.info(f"No Ontopo reservation link found for {venue_name}")
                    logger.info(f"Ontopo integration temporarily disabled for {place.get('name')}")
                except Exception as e:
                    logger.warning(f"Failed to get Ontopo link for {place.get('name')}: {e}")
            
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
    
    async def _create_venue_suggestions(
        self, 
        venues: List[Venue], 
        plan_request: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create venue suggestions with additional planning data"""
        suggestions = []
        
        for i, venue in enumerate(venues):
            # Calculate travel time from previous venue
            travel_time = 0
            if i > 0:
                travel_time = self._estimate_travel_time(venues[i-1], venue)
            
            suggestion = {
                "venue_id": venue.id,
                "name": venue.name,
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
                "amenities": venue.amenities,
                "links": self._format_venue_links(venue.links),
                "personalization_score": getattr(venue, 'personalization_score', None),
                "travel_time_from_previous": travel_time
            }
            
            suggestions.append(suggestion)
        
        return suggestions
    
    def _format_venue_links(self, links) -> List[Dict[str, str]]:
        """Format venue links for the response"""
        if not links:
            return []
        
        formatted_links = []
        for link in links:
            formatted_links.append({
                "type": link.type,
                "url": link.url,
                "title": link.title or link.type,
                "description": link.description
            })
        
        return formatted_links
    
    def _estimate_travel_time(self, venue1: Venue, venue2: Venue) -> float:
        """Estimate travel time between two venues in minutes"""
        # Simple estimation - in real implementation, you'd use a mapping service
        # For now, using a basic calculation based on distance
        
        from app.api.routes import calculate_distance
        
        distance = calculate_distance(
            venue1.location.latitude, venue1.location.longitude,
            venue2.location.latitude, venue2.location.longitude
        )
        
        # Assume average speed of 30 km/h in city
        # Convert to minutes
        travel_time_hours = distance / 30.0
        return travel_time_hours * 60.0
    
    def _calculate_total_duration(self, venue_suggestions: List[Dict[str, Any]], plan_request: Dict[str, Any]) -> Optional[float]:
        """Calculate total estimated duration for the plan"""
        # Base duration per venue (varies by type)
        venue_durations = {
            "restaurant": 1.5,  # hours
            "cafe": 0.75,
            "bar": 2.0,
            "museum": 2.0,
            "theater": 2.5,
            "park": 1.0,
            "shopping_center": 1.5,
            "sports_facility": 1.5,
            "hotel": 0.0,  # Just visiting
            "other": 1.0
        }
        
        total_duration = 0
        for suggestion in venue_suggestions:
            venue_type = suggestion.get("venue_type", "other")
            duration = venue_durations.get(venue_type, 1.0)
            total_duration += duration
        
        # Add travel time
        travel_times = [s.get("travel_time_from_previous", 0) for s in venue_suggestions[1:]]
        total_travel_time = sum(travel_times) / 60.0  # Convert minutes to hours
        
        return total_duration + total_travel_time
    
    def _generate_travel_route(self, venue_suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate travel route between venues"""
        if len(venue_suggestions) < 2:
            return []
        
        route = []
        for i in range(len(venue_suggestions) - 1):
            current = venue_suggestions[i]
            next_venue = venue_suggestions[i + 1]
            
            route_segment = {
                "from_venue": current["name"],
                "to_venue": next_venue["name"],
                "travel_time_minutes": next_venue.get("travel_time_from_previous", 0),
                "from_location": current["location"],
                "to_location": next_venue["location"]
            }
            
            route.append(route_segment)
        
        return route
    
    def _calculate_average_score(self, venues: List[Venue], user_preferences: Optional[UserPreferences]) -> Optional[float]:
        """Calculate average personalization score"""
        if not user_preferences or not venues:
            return None
        
        scores = []
        for venue in venues:
            score = personalization_service.calculate_personalization_score(venue, user_preferences)
            scores.append(score)
        
        return sum(scores) / len(scores) if scores else None

    def _select_balanced_venues(self, venues_by_type: Dict[str, List[Venue]], max_venues: int) -> List[Venue]:
        """
        Select a balanced number of venues from each type to meet max_venues.
        Ensures representation from each venue type when possible.
        """
        selected_venues = []
        venue_types = list(venues_by_type.keys())
        
        if not venue_types:
            return selected_venues
        
        # Calculate how many venues to take from each type
        venues_per_type = max(1, max_venues // len(venue_types))
        remaining_venues = max_venues % len(venue_types)
        
        logger.info(f"Selecting venues: {venues_per_type} per type, {remaining_venues} extra")
        
        for i, venue_type in enumerate(venue_types):
            venues_for_type = venues_by_type[venue_type]
            
            # Take venues_per_type from this type, plus one extra if we have remaining_venues
            extra = 1 if i < remaining_venues else 0
            venues_to_take = min(venues_per_type + extra, len(venues_for_type))
            
            if venues_to_take > 0:
                selected_from_type = venues_for_type[:venues_to_take]
                selected_venues.extend(selected_from_type)
                logger.info(f"Selected {len(selected_from_type)} venues from {venue_type}")
        
        # If we still have room and venues available, add more from types with higher ratings
        if len(selected_venues) < max_venues:
            remaining_needed = max_venues - len(selected_venues)
            logger.info(f"Adding {remaining_needed} more venues from highest-rated options")
            
            # Get all unselected venues and sort by rating
            all_unselected = []
            for venue_type, venues in venues_by_type.items():
                already_selected = len([v for v in selected_venues if v.venue_type == venue_type])
                unselected = venues[already_selected:]
                all_unselected.extend(unselected)
            
            # Sort by rating (highest first) and take remaining needed
            all_unselected.sort(key=lambda v: v.rating or 0, reverse=True)
            additional_venues = all_unselected[:remaining_needed]
            selected_venues.extend(additional_venues)
            
            logger.info(f"Added {len(additional_venues)} additional venues")
        
        logger.info(f"Final selection: {len(selected_venues)} venues from {len(venue_types)} types")
        return selected_venues

    async def _generate_multiple_plans(self, venues_by_type: Dict[str, List[Venue]], max_venues: int, plan_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate multiple venue plans with different combinations of venue types.
        Each plan will have exactly max_venues venues from different venue types.
        IMPORTANT: Each venue will appear in only ONE plan to ensure variety.
        
        NEW APPROACH: Geographic + Balance Strategy
        - Groups venue types that work well together geographically
        - Ensures balanced experiences across plans
        - Creates practical, enjoyable outing combinations
        """
        import itertools
        
        all_plans = []
        venue_types = list(venues_by_type.keys())
        
        # Track which venues have been used to avoid duplicates across plans
        used_venues = set()
        
        # NEW: Geographic + Balance Strategy
        # Define venue type groups that work well together geographically
        
        if max_venues == 1:
            # Single venue plans - each plan has one venue from a different type
            for i in range(min(3, len(venue_types))):
                venue_type = venue_types[i]
                # Find the first unused venue of this type
                available_venues = [v for v in venues_by_type[venue_type] if v.id not in used_venues]
                if available_venues:
                    venues_for_type = [available_venues[0]]  # Take first unused venue
                    used_venues.add(available_venues[0].id)  # Mark as used
                    
                    plan = await self._create_single_plan(
                        venues_for_type, 
                        [venue_type], 
                        f"{plan_request.get('plan_id')}-plan{i+1}",
                        plan_request
                    )
                    all_plans.append(plan)
                
        elif max_venues == 2:
            # Two venue plans - Geographic combinations
            geographic_combinations = self._get_geographic_combinations_2(venue_types)
            
            for i, (type1, type2) in enumerate(geographic_combinations):
                venues_for_plan = []
                
                # Get unused venue from type1
                available_type1 = [v for v in venues_by_type[type1] if v.id not in used_venues]
                if available_type1:
                    venues_for_plan.append(available_type1[0])
                    used_venues.add(available_type1[0].id)
                
                # Get unused venue from type2
                available_type2 = [v for v in venues_by_type[type2] if v.id not in used_venues]
                if available_type2:
                    venues_for_plan.append(available_type2[0])
                    used_venues.add(available_type2[0].id)
                
                if len(venues_for_plan) == 2:  # Only create plan if we have both venues
                    plan = await self._create_single_plan(
                        venues_for_plan,
                        [type1, type2],
                        f"{plan_request.get('plan_id')}-plan{i+1}",
                        plan_request
                    )
                    all_plans.append(plan)
                
        elif max_venues == 3:
            # Three venue plans - Geographic + Balance combinations
            geographic_combinations = self._get_geographic_combinations_3(venue_types)
            
            for i, (type1, type2, type3) in enumerate(geographic_combinations):
                venues_for_plan = []
                
                # Get unused venue from type1
                available_type1 = [v for v in venues_by_type[type1] if v.id not in used_venues]
                if available_type1:
                    venues_for_plan.append(available_type1[0])
                    used_venues.add(available_type1[0].id)
                
                # Get unused venue from type2
                available_type2 = [v for v in venues_by_type[type2] if v.id not in used_venues]
                if available_type2:
                    venues_for_plan.append(available_type2[0])
                    used_venues.add(available_type2[0].id)
                
                # Get unused venue from type3
                available_type3 = [v for v in venues_by_type[type3] if v.id not in used_venues]
                if available_type3:
                    venues_for_plan.append(available_type3[0])
                    used_venues.add(available_type3[0].id)
                
                if len(venues_for_plan) == 3:  # Only create plan if we have all three venues
                    plan = await self._create_single_plan(
                        venues_for_plan,
                        [type1, type2, type3],
                        f"{plan_request.get('plan_id')}-plan{i+1}",
                        plan_request
                    )
                    all_plans.append(plan)
                
        else:
            # For max_venues > 3, create balanced plans
            for i in range(3):
                # Create a plan with max_venues venues, distributed across different types
                venues_for_plan = []
                types_used = []
                
                # Distribute venues across different types
                venues_per_type = max_venues // len(venue_types)
                remaining = max_venues % len(venue_types)
                
                for j, venue_type in enumerate(venue_types):
                    venues_to_take = venues_per_type + (1 if j < remaining else 0)
                    if venues_to_take > 0:
                        # Get unused venues from this type
                        available_venues = [v for v in venues_by_type[venue_type] if v.id not in used_venues]
                        venues_to_add = min(venues_to_take, len(available_venues))
                        
                        for k in range(venues_to_add):
                            venues_for_plan.append(available_venues[k])
                            used_venues.add(available_venues[k].id)
                        
                        if venues_to_add > 0:
                            types_used.append(venue_type)
                
                if len(venues_for_plan) > 0:  # Only create plan if we have venues
                    plan = await self._create_single_plan(
                        venues_for_plan,
                        types_used,
                        f"{plan_request.get('plan_id')}-plan{i+1}",
                        plan_request
                    )
                    all_plans.append(plan)
        
        # Ensure we always return exactly 3 plans
        while len(all_plans) < 3:
            # Create additional plans if needed, using remaining unused venues
            plan_id = f"{plan_request.get('plan_id')}-plan{len(all_plans)+1}"
            
            # Find any unused venues from any type
            additional_venues = []
            for venue_type, venues in venues_by_type.items():
                unused = [v for v in venues if v.id not in used_venues]
                if unused:
                    additional_venues.append(unused[0])
                    used_venues.add(unused[0].id)
                    if len(additional_venues) >= max_venues:
                        break
            
            if additional_venues:
                additional_plan = await self._create_single_plan(
                    additional_venues,
                    [v.venue_type.value for v in additional_venues],
                    plan_id,
                    plan_request
                )
                all_plans.append(additional_plan)
            else:
                # If no more unused venues, break to avoid infinite loop
                break
        
        return all_plans[:3]  # Return exactly 3 plans
    
    def _get_geographic_combinations_2(self, venue_types: List[str]) -> List[tuple]:
        """
        Get geographic combinations for 2-venue plans.
        Groups venue types that work well together geographically.
        """
        # Define which venue types work well together geographically
        geographic_pairs = [
            # Food & Dining (often in same areas)
            ("restaurant", "cafe"),
            ("restaurant", "bar"),
            ("cafe", "bar"),
            
            # Entertainment District
            ("bar", "theater"),
            ("theater", "cafe"),
            
            # Outdoor & Relaxation
            ("park", "cafe"),
            ("park", "restaurant"),
            
            # Nightlife
            ("bar", "theater"),
            ("restaurant", "theater"),
        ]
        
        # Filter to only include pairs where both types are requested
        available_pairs = []
        for type1, type2 in geographic_pairs:
            if type1 in venue_types and type2 in venue_types:
                available_pairs.append((type1, type2))
        
        # If we don't have enough geographic pairs, create balanced combinations
        if len(available_pairs) < 3:
            # Fallback to balanced combinations
            available_pairs = [
                (venue_types[0], venue_types[1]),
                (venue_types[1], venue_types[2]) if len(venue_types) > 2 else (venue_types[0], venue_types[1]),
                (venue_types[0], venue_types[2]) if len(venue_types) > 2 else (venue_types[0], venue_types[1])
            ]
        
        return available_pairs[:3]  # Return exactly 3 combinations
    
    def _get_geographic_combinations_3(self, venue_types: List[str]) -> List[tuple]:
        """
        Get geographic combinations for 3-venue plans.
        Groups venue types that work well together geographically.
        """
        # Define which venue types work well together geographically
        geographic_trios = [
            # Food & Entertainment District
            ("restaurant", "cafe", "theater"),  # Dinner → Coffee → Movie
            ("bar", "restaurant", "cafe"),      # Drinks → Dinner → Coffee
            
            # Nightlife Experience
            ("bar", "theater", "cafe"),         # Pre-drinks → Show → After-party
            
            # Day Out Experience
            ("park", "restaurant", "cafe"),     # Walk → Lunch → Coffee
            
            # Cultural Experience
            ("museum", "restaurant", "cafe"),   # Culture → Dinner → Coffee
            ("theater", "restaurant", "bar"),   # Show → Dinner → Drinks
        ]
        
        # Filter to only include trios where all types are requested
        available_trios = []
        for type1, type2, type3 in geographic_trios:
            if type1 in venue_types and type2 in venue_types and type3 in venue_types:
                available_trios.append((type1, type2, type3))
        
        # If we don't have enough geographic trios, create balanced combinations
        if len(available_trios) < 3:
            # Fallback to balanced combinations
            if len(venue_types) >= 3:
                available_trios = [
                    (venue_types[0], venue_types[1], venue_types[2]),
                    (venue_types[1], venue_types[2], venue_types[3]) if len(venue_types) > 3 else (venue_types[0], venue_types[1], venue_types[2]),
                    (venue_types[0], venue_types[2], venue_types[3]) if len(venue_types) > 3 else (venue_types[0], venue_types[1], venue_types[2])
                ]
            else:
                # If we have fewer venue types, create plans with multiple venues from same type
                available_trios = [
                    (venue_types[0], venue_types[0], venue_types[0]),
                    (venue_types[0], venue_types[0], venue_types[1]) if len(venue_types) > 1 else (venue_types[0], venue_types[0], venue_types[0]),
                    (venue_types[0], venue_types[1], venue_types[1]) if len(venue_types) > 1 else (venue_types[0], venue_types[0], venue_types[0])
                ]
        
        return available_trios[:3]  # Return exactly 3 combinations
    
    async def _create_single_plan(self, venues: List[Venue], venue_types: List[str], plan_id: str, plan_request: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method to create a single plan with the given venues"""
        # Generate venue suggestions with additional data
        venue_suggestions = await self._create_venue_suggestions(venues, plan_request)
        
        # Calculate plan metrics
        total_duration = self._calculate_total_duration(venue_suggestions, plan_request)
        travel_route = self._generate_travel_route(venue_suggestions)
        
        # Create plan response
        plan_response = {
            "plan_id": plan_id,
            "user_id": plan_request.get("user_id"),
            "suggested_venues": venue_suggestions,
            "total_venues_found": len(venues),
            "venue_types_included": venue_types,
            "venues_list": venues,
            "estimated_total_duration": total_duration,
            "travel_route": travel_route,
            "personalization_applied": False,
            "average_personalization_score": None,
            "search_criteria_used": {
                "venue_types": venue_types,
                "location": plan_request.get("location"),
                "radius_km": plan_request.get("radius_km"),
                "max_venues": len(venues),
                "venues_per_type": VENUES_PER_TYPE,
                "use_personalization": False
            },
            "generated_at": datetime.utcnow().isoformat(),
            "status": "completed",
            "message": f"Plan with {len(venues)} venues from {len(venue_types)} venue types"
        }
        
        return plan_response

# Global instance
plan_generator = PlanGenerator() 