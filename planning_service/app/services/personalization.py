"""
Personalization service for ranking venues based on user rating history
and venue attributes for the Planning Service.
"""

from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class PlanningPersonalizationService:
    """Enhanced personalization service that combines user rating history with venue quality"""
    
    def __init__(self):
        self.weights = {
            'user_rating_history': 0.40,  # User's past ratings (most important)
            'venue_rating': 0.25,         # Google venue rating
            'venue_type_preference': 0.15, # Based on frequency in user history
            'price_compatibility': 0.10,   # Price range matching
            'novelty_bonus': 0.10         # Bonus for trying new venues
        }
    
    def personalize_venues(
        self, 
        venues_by_type: Dict[str, List[Dict]], 
        user_rating_history: Dict[str, float],
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, List[Tuple[Dict, float]]]:
        """
        Personalize venues by scoring them based on user rating history
        
        Args:
            venues_by_type: Venues grouped by type from Venues Service
            user_rating_history: User's venue rating history {venue_id: avg_rating}
            user_preferences: Optional user preferences from profile
            
        Returns:
            Venues with personalization scores, grouped by type
        """
        # Filter to only include highly rated venues (4+) for personalization
        highly_rated_history = self._filter_highly_rated_venues(user_rating_history)
        
        if highly_rated_history:
            logger.info(f"Using {len(highly_rated_history)} highly rated venues (4+) for personalization")
        else:
            logger.info("No highly rated venues found, using neutral personalization")
        
        personalized_venues = {}
        
        # Calculate user's venue type preferences from highly rated venues only
        type_preferences = self._calculate_type_preferences(highly_rated_history, venues_by_type)
        
        for venue_type, venues in venues_by_type.items():
            scored_venues = []
            
            for venue in venues:
                score = self._calculate_venue_score(
                    venue, 
                    highly_rated_history,  # Use filtered history
                    type_preferences, 
                    venue_type,
                    user_preferences
                )
                scored_venues.append((venue, score))
            
            # Sort by score (highest first)
            scored_venues.sort(key=lambda x: x[1], reverse=True)
            personalized_venues[venue_type] = scored_venues
            
            logger.info(f"Personalized {len(venues)} {venue_type} venues for user")
        
        return personalized_venues
    
    def _calculate_venue_score(
        self, 
        venue: Dict[str, Any], 
        user_rating_history: Dict[str, float],
        type_preferences: Dict[str, float],
        venue_type: str,
        user_preferences: Dict[str, Any] = None
    ) -> float:
        """Calculate personalization score for a single venue"""
        
        total_score = 0.0
        venue_id = venue.get("id")
        
        # 1. User Rating History (40% weight) - Only consider venues rated 4+
        if venue_id in user_rating_history:
            user_rating = user_rating_history[venue_id]
            # Since we're now using filtered history (4+ only), all ratings here are high
            rating_score = (user_rating - 1) / 4  # Normalize 1-5 to 0-1
            total_score += rating_score * self.weights['user_rating_history']
            logger.debug(f"Venue {venue.get('name', venue_id)} boosted by high user rating {user_rating}")
        else:
            # New venue - use average score
            total_score += 0.5 * self.weights['user_rating_history']
        
        # 2. Venue Rating (25% weight)
        venue_rating = venue.get("rating", 3.0)
        if venue_rating:
            rating_score = (venue_rating - 1) / 4  # Normalize 1-5 to 0-1
            total_score += rating_score * self.weights['venue_rating']
        else:
            total_score += 0.5 * self.weights['venue_rating']
        
        # 3. Venue Type Preference (15% weight)
        type_preference = type_preferences.get(venue_type, 0.5)
        total_score += type_preference * self.weights['venue_type_preference']
        
        # 4. Price Compatibility (10% weight)
        price_score = self._calculate_price_compatibility(venue, user_preferences)
        total_score += price_score * self.weights['price_compatibility']
        
        # 5. Novelty Bonus (10% weight)
        if venue_id not in user_rating_history:
            # Bonus for trying new venues
            total_score += 0.7 * self.weights['novelty_bonus']
        else:
            total_score += 0.3 * self.weights['novelty_bonus']
        
        return min(1.0, max(0.0, total_score))  # Clamp between 0-1
    
    def _calculate_type_preferences(
        self, 
        user_rating_history: Dict[str, float], 
        venues_by_type: Dict[str, List[Dict]]
    ) -> Dict[str, float]:
        """Calculate user's venue type preferences based on highly rated venues (4+) only"""
        
        type_ratings = {}
        type_counts = {}
        
        # Map venue_ids to their types
        venue_id_to_type = {}
        for venue_type, venues in venues_by_type.items():
            for venue in venues:
                venue_id_to_type[venue.get("id")] = venue_type
        
        # Aggregate ratings by venue type - Only highly rated venues (4+) are passed here
        for venue_id, rating in user_rating_history.items():
            venue_type = venue_id_to_type.get(venue_id)
            if venue_type:
                if venue_type not in type_ratings:
                    type_ratings[venue_type] = 0
                    type_counts[venue_type] = 0
                
                type_ratings[venue_type] += rating
                type_counts[venue_type] += 1
                logger.debug(f"Counting venue type {venue_type} with high rating {rating} for preferences")
        
        # Calculate average preferences based on highly rated venues only
        type_preferences = {}
        for venue_type in venues_by_type.keys():
            if venue_type in type_ratings:
                avg_rating = type_ratings[venue_type] / type_counts[venue_type]
                # Normalize 1-5 to 0-1
                type_preferences[venue_type] = (avg_rating - 1) / 4
                logger.info(f"Type {venue_type}: {type_counts[venue_type]} highly rated venues, avg rating {avg_rating:.2f}")
            else:
                # No highly rated venues for this type - neutral preference
                type_preferences[venue_type] = 0.5
                logger.info(f"Type {venue_type}: No highly rated venues, using neutral preference")
        
        return type_preferences
    
    def _calculate_price_compatibility(
        self, 
        venue: Dict[str, Any], 
        user_preferences: Dict[str, Any] = None
    ) -> float:
        """Calculate price range compatibility score"""
        
        if not user_preferences:
            return 0.5  # Neutral if no preferences
        
        venue_price = venue.get("price_range", "$$")
        preferred_price = user_preferences.get("preferred_price_range", "$$")
        
        price_mapping = {'$': 1, '$$': 2, '$$$': 3}
        venue_level = price_mapping.get(venue_price, 2)
        preferred_level = price_mapping.get(preferred_price, 2)
        
        # Perfect match
        if venue_level == preferred_level:
            return 1.0
        # Close match
        elif abs(venue_level - preferred_level) == 1:
            return 0.7
        # Far match
        else:
            return 0.3

    def _filter_highly_rated_venues(self, user_rating_history: Dict[str, float]) -> Dict[str, float]:
        """
        Filter user rating history to only include venues rated 4 or higher
        
        Args:
            user_rating_history: Raw user rating history
            
        Returns:
            Filtered history with only highly rated venues
        """
        highly_rated = {}
        for venue_id, rating in user_rating_history.items():
            if rating >= 4.0:
                highly_rated[venue_id] = rating
        
        logger.info(f"Filtered {len(user_rating_history)} total ratings to {len(highly_rated)} highly rated venues (4+)")
        return highly_rated

# Global instance
planning_personalization_service = PlanningPersonalizationService()
