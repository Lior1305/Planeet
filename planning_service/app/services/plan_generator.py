"""
Plan generation service for creating multiple venue plans with randomization logic
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging
import random
import hashlib
import time

from app.models.plan_request import PlanRequest
from app.services.time_calculator import time_calculator

logger = logging.getLogger(__name__)

class PlanGenerator:
    """Service for generating multiple venue plans with randomization and venue selection"""
    
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
    
    def _apply_controlled_randomness(self, venues: List[Dict], seed: int, selection_factor: float = 0.7) -> List[Dict]:
        """
        Apply controlled randomness to venue list while maintaining quality
        
        Args:
            venues: List of venue dictionaries (assumed to be pre-sorted by quality/personalization)
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
    
    async def generate_multiple_plans(
        self, 
        venues_by_type: Dict[str, List[Dict]], 
        plan_request: PlanRequest
    ) -> Dict[str, Any]:
        """
        Generate exactly 3 different venue plans with balanced venue types.
        
        Args:
            venues_by_type: Dictionary mapping venue types to lists of venue dictionaries
            plan_request: Original plan request
            
        Returns:
            Complete plan response with 3 different plans
        """
        try:
            max_venues = plan_request.max_venues
            venue_types = list(venues_by_type.keys())
            
            # Validate max_venues constraint
            if max_venues > len(venue_types):
                raise ValueError(f"max_venues ({max_venues}) cannot be greater than number of venue types ({len(venue_types)})")
            
            # Generate randomness seed for this request
            randomness_seed = self._generate_randomness_seed(plan_request.dict())
            logger.info(f"Generated randomness seed: {randomness_seed}")
            
            # Apply controlled randomness to venues within each type
            for venue_type in venues_by_type:
                venues_by_type[venue_type] = self._apply_controlled_randomness(
                    venues_by_type[venue_type], randomness_seed + hash(venue_type)
                )
            
            # Generate multiple plans with different venue type combinations
            all_plans = await self._generate_multiple_plans(venues_by_type, max_venues, plan_request, randomness_seed)
            
            # Create the final response
            response = {
                "plan_id": plan_request.plan_id,
                "user_id": plan_request.user_id,
                "total_plans_generated": len(all_plans),
                "plans": all_plans,
                "total_venues_found": sum(len(venues) for venues in venues_by_type.values()),
                "generated_at": datetime.utcnow().isoformat(),
                "status": "completed",
                "message": f"Successfully generated {len(all_plans)} plans with {max_venues} venues each from {len(venue_types)} categories"
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating plans: {e}")
            raise

    async def _generate_multiple_plans(
        self, 
        venues_by_type: Dict[str, List[Dict]], 
        max_venues: int, 
        plan_request: PlanRequest, 
        randomness_seed: int
    ) -> List[Dict[str, Any]]:
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
                available_venues = [v for v in venues_by_type[venue_type] if v["id"] not in used_venues]
                if available_venues:
                    # Instead of always taking the first, select randomly from top venues
                    # This adds randomness while still favoring quality venues
                    selection_count = min(3, len(available_venues))  # Consider top 3 available venues
                    top_available = available_venues[:selection_count]
                    selected_venue = random.choice(top_available)
                    
                    venues_for_plan.append(selected_venue)
                    used_venues.add(selected_venue["id"])
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
                    f"{plan_request.plan_id}-plan{plan_index+1}",
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
                    
                unused = [v for v in venues if v["id"] not in used_venues]
                if unused and len(venues_for_plan) < max_venues:
                    # Add randomness to fallback selection too
                    selected_venue = random.choice(unused) if len(unused) > 1 else unused[0]
                    venues_for_plan.append(selected_venue)
                    used_venues.add(selected_venue["id"])
                    types_used.append(venue_type)
                    categories_used_in_plan.add(venue_type)  # Track category usage in this plan
            
            if venues_for_plan:
                plan = await self._create_single_plan(
                    venues_for_plan,
                    types_used,
                    f"{plan_request.plan_id}-plan{plan_index+1}",
                    plan_request
                )
                all_plans.append(plan)
            else:
                # If no more unused venues, break to avoid infinite loop
                break
        
        return all_plans[:3]  # Return exactly 3 plans

    async def _create_single_plan(
        self, 
        venues: List[Dict], 
        venue_types: List[str], 
        plan_id: str, 
        plan_request: PlanRequest
    ) -> Dict[str, Any]:
        """Helper method to create a single plan with the given venues"""
        
        # Validate that all venue categories are unique within this plan
        venue_categories = [venue["venue_type"] for venue in venues]
        unique_categories = set(venue_categories)
        if len(venue_categories) != len(unique_categories):
            logger.warning(f"Plan {plan_id} contains duplicate venue categories: {venue_categories}")
            # Log but don't fail - this shouldn't happen with our new logic but good to catch
        
        # Optimize venue order considering logical flow, opening hours, and travel time
        optimized_venues = time_calculator.optimize_venue_order(venues, plan_request.date)
        
        # Calculate timing for all venues
        timed_venues = time_calculator.calculate_plan_timing(
            optimized_venues, 
            plan_request.date,  # Start time from user request
            plan_request.group_size
        )
        
        # Get plan timing summary
        timing_summary = time_calculator.get_plan_summary(timed_venues)
        
        # Create simplified venue structure with timing information
        simplified_venues = []
        for i, venue in enumerate(timed_venues):
            # Get the first website link if available, otherwise null
            url_link = None
            if venue.get("links") and len(venue["links"]) > 0:
                url_link = venue["links"][0].get("url")
            
            simplified_venue = {
                "venue_id": venue["id"],
                "name": venue["name"],
                "venue_type": venue["venue_type"],
                "location": {
                    "latitude": venue["location"]["latitude"],
                    "longitude": venue["location"]["longitude"]
                },
                "rating": venue.get("rating"),
                "price_range": venue.get("price_range"),
                "amenities": venue.get("amenities", []),
                "address": venue["location"].get("address", ""),
                "url_link": url_link,
                
                # Enhanced timing information
                "start_time": venue.get("start_time"),
                "end_time": venue.get("end_time"),
                "duration_minutes": venue.get("duration_minutes"),
                "travel_time_from_previous": venue.get("travel_time_from_previous"),
                "travel_distance_km": venue.get("travel_distance_km")
            }
            simplified_venues.append(simplified_venue)
        
        # Calculate total duration in hours for backward compatibility
        total_duration_hours = timing_summary.get("total_duration_minutes", 0) / 60.0
        
        # Create enhanced plan structure with timing information
        plan = {
            "plan_id": plan_id,
            "user_id": plan_request.user_id,
            "suggested_venues": simplified_venues,
            "venue_types_included": venue_types,
            "estimated_total_duration": round(total_duration_hours, 2),
            "personalization_applied": plan_request.use_personalization,
            "generated_at": datetime.utcnow().isoformat(),
            "status": "completed",
            "message": f"Plan with {len(venues)} venues from {len(venue_types)} venue types",
            
            # Enhanced timing summary
            "timing_summary": timing_summary
        }
        
        return plan

# Global instance
plan_generator = PlanGenerator()
