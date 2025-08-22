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

logger = logging.getLogger(__name__)

class PlanGenerator:
    """Service for generating comprehensive venue plans"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def generate_plan(self, plan_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive venue plan based on the request
        
        Args:
            plan_request: Plan request from Planning Service
            
        Returns:
            Complete plan response with venue suggestions
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
            
            # Notify Planning Service that we're processing
            await planning_service_client.update_plan_status(
                plan_id, "processing", "Venue discovery in progress"
            )
            
            # Get user preferences if personalization is enabled
            user_preferences = None
            if use_personalization:
                user_preferences = await planning_integration.get_user_preferences(user_id)
            
            # Discover venues for each requested type
            all_venues = []
            for venue_type in venue_types:
                venues = await self._discover_venues_for_type(
                    venue_type, location, radius_km, user_preferences
                )
                all_venues.extend(venues)
            
            # Apply personalization and ranking
            if user_preferences and use_personalization:
                ranked_venues = personalization_service.personalize_venue_list(
                    all_venues, user_preferences
                )
                # Extract venues and scores
                all_venues = [venue for venue, score in ranked_venues]
            
            # Select top venues based on max_venues
            selected_venues = all_venues[:max_venues]
            
            # Generate venue suggestions with additional data
            venue_suggestions = await self._create_venue_suggestions(
                selected_venues, plan_request
            )
            
            # Calculate plan metrics
            total_duration = self._calculate_total_duration(venue_suggestions, plan_request)
            travel_route = self._generate_travel_route(venue_suggestions)
            
            # Create plan response
            plan_response = {
                "plan_id": plan_id,
                "user_id": user_id,
                "suggested_venues": venue_suggestions,
                "total_venues_found": len(all_venues),
                "venues_list": all_venues,
                "estimated_total_duration": total_duration,
                "travel_route": travel_route,
                "personalization_applied": use_personalization and user_preferences is not None,
                "average_personalization_score": self._calculate_average_score(selected_venues, user_preferences),
                "search_criteria_used": {
                    "venue_types": venue_types,
                    "location": location,
                    "radius_km": radius_km,
                    "max_venues": max_venues,
                    "use_personalization": use_personalization
                },
                "generated_at": datetime.utcnow().isoformat(),
                "status": "completed",
                "message": f"Successfully generated plan with {len(venue_suggestions)} venues"
            }
            
            # Notify completion
            await planning_service_client.notify_plan_completion(plan_id, len(venue_suggestions))
            
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
        user_preferences: Optional[UserPreferences]
    ) -> List[Venue]:
        """
        Discover venues for a specific type using Google Places API
        
        Args:
            venue_type: Type of venue to search for
            location: Location coordinates and address
            radius_km: Search radius in kilometers
            user_preferences: User preferences for filtering
            
        Returns:
            List of discovered venues
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
            places = search_places(
                lat=lat,
                lng=lng,
                place_type=google_place_type,
                keyword=venue_type.replace("_", " "),
                radius=radius_meters
            )
            
            if not places:
                logger.info(f"No places found for venue type {venue_type}")
                return []
            
            # Convert Google Places to Venue objects
            venues = []
            for place in places:
                try:
                    venue = await self._convert_google_place_to_venue(place, venue_type)
                    if venue:
                        venues.append(venue)
                except Exception as e:
                    logger.error(f"Error converting place {place.get('place_id')}: {e}")
                    continue
            
            logger.info(f"Discovered {len(venues)} venues for type {venue_type}")
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

# Global instance
plan_generator = PlanGenerator() 