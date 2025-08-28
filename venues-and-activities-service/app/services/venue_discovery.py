"""
Venue discovery service for finding venues using Google Places API
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging

from app.models.schemas import Venue, UserPreferences, VenueType, Location, VenueLink
from app.services.personalization import personalization_service
from app.services.planning_integration import planning_integration
from app.services.place_finder import search_places, get_place_details

logger = logging.getLogger(__name__)

class VenueDiscovery:
    """Service for discovering venues from Google Places API"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def discover_venues_for_type(
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

# Global instance
venue_discovery = VenueDiscovery()
