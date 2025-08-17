"""
Personalization service for scoring venues based on user preferences
and providing personalized venue recommendations.
"""

from typing import List, Tuple, Optional
from app.models.schemas import Venue, UserPreferences
import logging

logger = logging.getLogger(__name__)

class VenuePersonalizationService:
    """Service for personalizing venue recommendations based on user preferences"""
    
    def __init__(self):
        self.weights = {
            'venue_type': 0.25,
            'price_range': 0.20,
            'amenities': 0.15,
            'rating': 0.15,
            'location': 0.15,
            'dietary': 0.10
        }
    
    def calculate_personalization_score(self, venue: Venue, preferences: UserPreferences) -> float:
        """
        Calculate how well a venue matches user preferences (0-1 scale)
        
        Args:
            venue: The venue to score
            preferences: User preferences to match against
            
        Returns:
            Personalization score between 0 and 1
        """
        if not preferences:
            return 0.5  # Neutral score if no preferences
        
        total_score = 0.0
        total_weight = 0.0
        
        # Venue type matching
        if preferences.preferred_venue_types:
            type_score = 1.0 if venue.venue_type in preferences.preferred_venue_types else 0.0
            total_score += type_score * self.weights['venue_type']
            total_weight += self.weights['venue_type']
        
        # Price range matching
        if preferences.preferred_price_range and venue.price_range:
            price_score = self._calculate_price_match(venue.price_range, preferences.preferred_price_range)
            total_score += price_score * self.weights['price_range']
            total_weight += self.weights['price_range']
        
        # Amenities matching
        if preferences.preferred_amenities and venue.amenities:
            amenities_score = self._calculate_amenities_match(venue.amenities, preferences.preferred_amenities)
            total_score += amenities_score * self.weights['amenities']
            total_weight += self.weights['amenities']
        
        # Rating matching
        if preferences.min_rating and venue.rating:
            rating_score = self._calculate_rating_match(venue.rating, preferences.min_rating)
            total_score += rating_score * self.weights['rating']
            total_weight += self.weights['rating']
        
        # Location matching (city preference)
        if preferences.preferred_cities and venue.location.city:
            location_score = self._calculate_location_match(venue.location.city, preferences.preferred_cities)
            total_score += location_score * self.weights['location']
            total_weight += self.weights['location']
        
        # Dietary restrictions matching
        if preferences.dietary_restrictions and venue.amenities:
            dietary_score = self._calculate_dietary_match(venue.amenities, preferences.dietary_restrictions)
            total_score += dietary_score * self.weights['dietary']
            total_weight += self.weights['dietary']
        
        # Normalize score if we have weights
        if total_weight > 0:
            return total_score / total_weight
        
        return 0.5  # Default neutral score
    
    def _calculate_price_match(self, venue_price: str, preferred_price: str) -> float:
        """Calculate price range compatibility score"""
        price_mapping = {'$': 1, '$$': 2, '$$$': 3}
        
        venue_level = price_mapping.get(venue_price, 2)
        preferred_level = price_mapping.get(preferred_price, 2)
        
        # Perfect match
        if venue_level == preferred_level:
            return 1.0
        
        # Close match (within 1 level)
        if abs(venue_level - preferred_level) <= 1:
            return 0.7
        
        # Far match
        return 0.3
    
    def _calculate_amenities_match(self, venue_amenities: List[str], preferred_amenities: List[str]) -> float:
        """Calculate amenities compatibility score"""
        if not venue_amenities or not preferred_amenities:
            return 0.5
        
        # Convert to lowercase for comparison
        venue_amenities_lower = [a.lower() for a in venue_amenities]
        preferred_amenities_lower = [a.lower() for a in preferred_amenities]
        
        # Count matching amenities
        matches = sum(1 for pref in preferred_amenities_lower if pref in venue_amenities_lower)
        
        if matches == 0:
            return 0.0
        elif matches == len(preferred_amenities_lower):
            return 1.0
        else:
            return matches / len(preferred_amenities_lower)
    
    def _calculate_rating_match(self, venue_rating: float, min_preferred_rating: float) -> float:
        """Calculate rating compatibility score"""
        if venue_rating >= min_preferred_rating:
            # Bonus for exceeding minimum
            if venue_rating >= min_preferred_rating + 1:
                return 1.0
            else:
                return 0.8
        else:
            # Penalty for being below minimum
            rating_diff = min_preferred_rating - venue_rating
            if rating_diff <= 0.5:
                return 0.6
            elif rating_diff <= 1.0:
                return 0.4
            else:
                return 0.2
    
    def _calculate_location_match(self, venue_city: str, preferred_cities: List[str]) -> float:
        """Calculate location compatibility score"""
        venue_city_lower = venue_city.lower()
        preferred_cities_lower = [c.lower() for c in preferred_cities]
        
        if venue_city_lower in preferred_cities_lower:
            return 1.0
        else:
            return 0.3
    
    def _calculate_dietary_match(self, venue_amenities: List[str], dietary_restrictions: List[str]) -> float:
        """Calculate dietary restrictions compatibility score"""
        if not venue_amenities or not dietary_restrictions:
            return 0.5
        
        venue_amenities_lower = [a.lower() for a in venue_amenities]
        dietary_restrictions_lower = [d.lower() for d in dietary_restrictions]
        
        # Check for dietary accommodation amenities
        dietary_keywords = {
            'vegetarian': ['vegetarian', 'vegan', 'plant-based'],
            'vegan': ['vegan', 'plant-based'],
            'gluten-free': ['gluten-free', 'gluten free', 'celiac'],
            'halal': ['halal'],
            'kosher': ['kosher']
        }
        
        score = 0.5  # Base score
        
        for restriction in dietary_restrictions_lower:
            if restriction in dietary_keywords:
                # Check if venue has any of the relevant keywords
                relevant_keywords = dietary_keywords[restriction]
                if any(keyword in venue_amenities_lower for keyword in relevant_keywords):
                    score += 0.3  # Bonus for accommodating this restriction
                else:
                    score -= 0.2  # Penalty for not accommodating
        
        return max(0.0, min(1.0, score))
    
    def personalize_venue_list(self, venues: List[Venue], preferences: UserPreferences) -> List[Tuple[Venue, float]]:
        """
        Personalize a list of venues by scoring them against user preferences
        
        Args:
            venues: List of venues to personalize
            preferences: User preferences to match against
            
        Returns:
            List of tuples (venue, personalization_score) sorted by score descending
        """
        if not preferences:
            # Return venues with neutral scores if no preferences
            return [(venue, 0.5) for venue in venues]
        
        # Score each venue
        scored_venues = []
        for venue in venues:
            score = self.calculate_personalization_score(venue, preferences)
            scored_venues.append((venue, score))
        
        # Sort by score (highest first)
        scored_venues.sort(key=lambda x: x[1], reverse=True)
        
        return scored_venues
    
    def get_personalized_recommendations(self, venues: List[Venue], preferences: UserPreferences, 
                                       limit: int = 10) -> List[Tuple[Venue, float]]:
        """
        Get top personalized venue recommendations
        
        Args:
            venues: List of venues to choose from
            preferences: User preferences to match against
            limit: Maximum number of recommendations to return
            
        Returns:
            List of top personalized venue recommendations with scores
        """
        personalized_venues = self.personalize_venue_list(venues, preferences)
        return personalized_venues[:limit]

# Global instance
personalization_service = VenuePersonalizationService() 