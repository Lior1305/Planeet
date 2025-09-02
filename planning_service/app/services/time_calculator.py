"""
Time calculation service for venue plans
Calculates start/end times, durations, and travel times between venues
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import math
import logging
import re

logger = logging.getLogger(__name__)

class TimeCalculator:
    """Service for calculating realistic timing for venue plans"""
    
    # Default durations for different venue types (in minutes)
    VENUE_DURATIONS = {
        "restaurant": 90,      # Meal + dining experience
        "bar": 75,             # Drinks and socializing
        "cafe": 45,            # Coffee and light snacks
        "museum": 120,         # Exploring exhibitions
        "theater": 180,        # Show + intermission
        "park": 60,            # Walking and relaxation
        "shopping_center": 90, # Shopping and browsing
        "sports_facility": 120, # Activities and sports
        "spa": 90,             # Spa treatment session
        "other": 60            # Default duration
    }
    
    # Buffer time between venues (in minutes)
    TRANSITION_BUFFER = 15
    
    # Average travel speeds
    WALKING_SPEED_KMH = 4.5    # Average walking speed
    DRIVING_SPEED_KMH = 30     # Average city driving speed
    
    # Venue type priorities for logical day/night flow
    # Lower number = earlier in the day
    VENUE_TYPE_PRIORITIES = {
        "cafe": 1,             # Early day: breakfast, morning coffee
        "museum": 2,           # Mid-day: sightseeing, culture
        "park": 3,             # Afternoon: outdoor activities
        "shopping_center": 4,  # Afternoon: shopping
        "sports_facility": 5,  # Afternoon/early evening: activities
        "spa": 6,              # Afternoon/early evening: relaxation
        "restaurant": 7,       # Evening: dinner
        "theater": 8,          # Evening: shows
        "bar": 9,              # Night: drinks, nightlife
        "other": 5             # Default middle priority
    }
    
    # Typical opening hours for venue types (24-hour format)
    TYPICAL_OPENING_HOURS = {
        "cafe": {"open": 7, "close": 18},           # 7 AM - 6 PM
        "museum": {"open": 10, "close": 17},        # 10 AM - 5 PM
        "park": {"open": 6, "close": 22},           # 6 AM - 10 PM
        "shopping_center": {"open": 10, "close": 21}, # 10 AM - 9 PM
        "sports_facility": {"open": 6, "close": 22}, # 6 AM - 10 PM
        "spa": {"open": 9, "close": 20},            # 9 AM - 8 PM
        "restaurant": {"open": 11, "close": 23},    # 11 AM - 11 PM
        "theater": {"open": 18, "close": 23},       # 6 PM - 11 PM
        "bar": {"open": 17, "close": 2},            # 5 PM - 2 AM (next day)
        "other": {"open": 9, "close": 21}           # Default 9 AM - 9 PM
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_opening_hours(self, opening_hours: Dict[str, str]) -> Tuple[int, int]:
        """
        Parse opening hours from venue data
        
        Args:
            opening_hours: Dict with 'open_at' and 'close_at' times (e.g., "09:00", "21:30")
            
        Returns:
            Tuple of (open_hour, close_hour) in 24-hour format
        """
        try:
            open_str = opening_hours.get("open_at", "")
            close_str = opening_hours.get("close_at", "")
            
            if not open_str or not close_str:
                return None, None
            
            # Parse time strings like "09:00" or "21:30"
            open_match = re.match(r"(\d{1,2}):(\d{2})", open_str)
            close_match = re.match(r"(\d{1,2}):(\d{2})", close_str)
            
            if not open_match or not close_match:
                return None, None
            
            open_hour = int(open_match.group(1)) + (int(open_match.group(2)) / 60.0)
            close_hour = int(close_match.group(1)) + (int(close_match.group(2)) / 60.0)
            
            return open_hour, close_hour
            
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Failed to parse opening hours {opening_hours}: {e}")
            return None, None
    
    def is_venue_open_at_time(self, venue: Dict[str, Any], check_time: datetime) -> bool:
        """
        Check if a venue is open at a specific time
        
        Args:
            venue: Venue dictionary with opening_hours
            check_time: Time to check
            
        Returns:
            True if venue is open, False if closed or unknown
        """
        venue_type = venue.get("venue_type", "other").lower()
        opening_hours = venue.get("opening_hours", {})
        
        # Try to parse actual opening hours from venue data
        open_hour, close_hour = self.parse_opening_hours(opening_hours)
        
        # If no opening hours available, use typical hours for venue type
        if open_hour is None or close_hour is None:
            typical_hours = self.TYPICAL_OPENING_HOURS.get(venue_type, self.TYPICAL_OPENING_HOURS["other"])
            open_hour = typical_hours["open"]
            close_hour = typical_hours["close"]
        
        # Convert check time to hour (with minutes as fraction)
        check_hour = check_time.hour + (check_time.minute / 60.0)
        
        # Handle venues that close after midnight (like bars)
        if close_hour < open_hour:  # e.g., open at 17, close at 2 (next day)
            # Venue is open if time is after opening OR before closing (next day)
            return check_hour >= open_hour or check_hour <= close_hour
        else:
            # Normal hours: venue is open between open_hour and close_hour
            return open_hour <= check_hour <= close_hour
    
    def get_venue_priority_score(self, venue: Dict[str, Any], planned_start_time: datetime) -> float:
        """
        Calculate a priority score for venue ordering considering both:
        1. Logical day/night flow (venue type priority)
        2. How well the venue timing fits the planned start time
        
        Lower score = higher priority (should come earlier)
        """
        venue_type = venue.get("venue_type", "other").lower()
        
        # Base priority from venue type (1-9, lower is earlier)
        type_priority = self.VENUE_TYPE_PRIORITIES.get(venue_type, 5)
        
        # Time appropriateness score (0-2, lower is better match)
        time_score = self.calculate_time_appropriateness(venue_type, planned_start_time)
        
        # Combine scores (type priority is more important)
        total_score = type_priority + (time_score * 0.3)
        
        return total_score
    
    def calculate_time_appropriateness(self, venue_type: str, planned_time: datetime) -> float:
        """
        Calculate how appropriate a venue type is for a specific time
        
        Returns:
            0.0 = perfect time
            1.0 = acceptable time
            2.0 = inappropriate time
        """
        hour = planned_time.hour
        
        # Define ideal time ranges for each venue type
        time_appropriateness = {
            "cafe": {
                "perfect": (7, 11),    # Morning coffee
                "good": (11, 16),      # Afternoon coffee
                "poor": (16, 24)       # Evening/night (inappropriate)
            },
            "museum": {
                "perfect": (10, 15),   # Ideal museum hours
                "good": (9, 17),       # Acceptable hours
                "poor": (17, 24)       # Evening (closed)
            },
            "park": {
                "perfect": (8, 18),    # Daylight hours
                "good": (6, 20),       # Extended daylight
                "poor": (20, 6)        # Night time
            },
            "restaurant": {
                "perfect": (12, 14),   # Lunch
                "good": (18, 22),      # Dinner
                "poor": (3, 11)        # Very early morning
            },
            "bar": {
                "perfect": (19, 24),   # Evening/night
                "good": (17, 2),       # Happy hour to late night
                "poor": (6, 17)        # Daytime
            }
        }
        
        # Get appropriateness for this venue type
        appropriateness = time_appropriateness.get(venue_type, {
            "perfect": (9, 21),
            "good": (8, 22),
            "poor": (22, 8)
        })
        
        # Check which range the hour falls into
        perfect_start, perfect_end = appropriateness["perfect"]
        good_start, good_end = appropriateness["good"]
        
        # Handle time ranges that cross midnight
        def in_range(hour, start, end):
            if start <= end:
                return start <= hour <= end
            else:  # crosses midnight
                return hour >= start or hour <= end
        
        if in_range(hour, perfect_start, perfect_end):
            return 0.0  # Perfect time
        elif in_range(hour, good_start, good_end):
            return 1.0  # Good time
        else:
            return 2.0  # Poor time
    
    def round_time_to_15_minutes(self, dt: datetime) -> datetime:
        """
        Round datetime to nearest 15-minute interval
        Examples: 10:07 -> 10:00, 10:12 -> 10:15, 10:23 -> 10:30, 10:38 -> 10:45
        """
        # Get current minutes
        minutes = dt.minute
        
        # Round to nearest 15-minute interval
        rounded_minutes = round(minutes / 15) * 15
        
        # Handle hour overflow
        if rounded_minutes == 60:
            rounded_minutes = 0
            dt = dt + timedelta(hours=1)
        
        # Create new datetime with rounded minutes
        rounded_dt = dt.replace(minute=rounded_minutes, second=0, microsecond=0)
        
        return rounded_dt
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = R * c
        
        return round(distance, 2)
    
    def calculate_travel_time(self, distance_km: float, transportation_mode: str = "walking") -> int:
        """
        Calculate travel time based on distance and transportation mode
        Returns time in minutes
        """
        if distance_km <= 0:
            return 0
        
        if transportation_mode == "walking":
            # For short distances, assume walking
            time_hours = distance_km / self.WALKING_SPEED_KMH
        else:
            # For longer distances, assume driving/public transport
            time_hours = distance_km / self.DRIVING_SPEED_KMH
        
        travel_minutes = int(time_hours * 60)
        
        # Add minimum travel time for very short distances
        return max(travel_minutes, 5)
    
    def get_venue_duration(self, venue_type: str, group_size: int = 2) -> int:
        """
        Get estimated duration for a venue type, adjusted for group size
        Returns duration in minutes
        """
        base_duration = self.VENUE_DURATIONS.get(venue_type.lower(), self.VENUE_DURATIONS["other"])
        
        # Adjust for group size (larger groups typically spend more time)
        if group_size > 4:
            adjustment_factor = 1.2
        elif group_size > 2:
            adjustment_factor = 1.1
        else:
            adjustment_factor = 1.0
        
        adjusted_duration = int(base_duration * adjustment_factor)
        return adjusted_duration
    
    def calculate_plan_timing(
        self, 
        venues: List[Dict[str, Any]], 
        start_datetime: datetime,
        group_size: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Calculate timing for all venues in a plan with 15-minute time rounding
        
        Args:
            venues: List of venue dictionaries with location information
            start_datetime: When the plan should start
            group_size: Number of people in the group
            
        Returns:
            List of venues with calculated timing information
        """
        if not venues:
            return []
        
        timed_venues = []
        # Start time is already validated to be in 15-minute intervals
        current_time = start_datetime
        
        for i, venue in enumerate(venues):
            venue_copy = venue.copy()
            
            # Get venue duration
            venue_type = venue.get("venue_type", "other")
            duration_minutes = self.get_venue_duration(venue_type, group_size)
            
            # Calculate travel time from previous venue
            travel_time_minutes = 0
            travel_distance_km = 0.0
            
            if i > 0:  # Not the first venue
                prev_venue = venues[i-1]
                
                # Get coordinates
                prev_lat = prev_venue["location"]["latitude"]
                prev_lon = prev_venue["location"]["longitude"]
                curr_lat = venue["location"]["latitude"]
                curr_lon = venue["location"]["longitude"]
                
                # Calculate distance and travel time
                travel_distance_km = self.calculate_distance(prev_lat, prev_lon, curr_lat, curr_lon)
                
                # Choose transportation mode based on distance
                transport_mode = "walking" if travel_distance_km <= 2.0 else "driving"
                travel_time_minutes = self.calculate_travel_time(travel_distance_km, transport_mode)
                
                # Add travel time and buffer to current time
                current_time += timedelta(minutes=travel_time_minutes + self.TRANSITION_BUFFER)
                
                # Round the arrival time to nearest 15-minute interval for consistency
                current_time = self.round_time_to_15_minutes(current_time)
            
            # Set start time for this venue (already rounded)
            start_time = current_time.strftime("%H:%M")
            
            # Calculate end time and round it too
            end_datetime = current_time + timedelta(minutes=duration_minutes)
            end_datetime = self.round_time_to_15_minutes(end_datetime)
            end_time = end_datetime.strftime("%H:%M")
            
            # Recalculate actual duration based on rounded times
            actual_duration_minutes = int((end_datetime - current_time).total_seconds() / 60)
            
            # Check if venue is open during the planned time
            venue_open_at_start = self.is_venue_open_at_time(venue, current_time)
            venue_open_at_end = self.is_venue_open_at_time(venue, end_datetime)
            
            if not venue_open_at_start or not venue_open_at_end:
                venue_name = venue.get("name", "Unknown")
                venue_type = venue.get("venue_type", "unknown")
                self.logger.warning(
                    f"⚠️ {venue_name} ({venue_type}) may be closed during planned time {start_time}-{end_time}"
                )
            
            # Update venue with timing information
            venue_copy.update({
                "start_time": start_time,
                "end_time": end_time,
                "duration_minutes": actual_duration_minutes,
                "travel_time_from_previous": travel_time_minutes,
                "travel_distance_km": travel_distance_km
            })
            
            timed_venues.append(venue_copy)
            
            # Move current time to end of this venue (already rounded)
            current_time = end_datetime
            
            self.logger.info(
                f"Venue {i+1}: {venue.get('name', 'Unknown')} | "
                f"Start: {start_time} | End: {end_time} | "
                f"Duration: {actual_duration_minutes}min | Travel: {travel_time_minutes}min"
            )
        
        return timed_venues
    
    def optimize_venue_order(self, venues: List[Dict[str, Any]], start_time: datetime = None) -> List[Dict[str, Any]]:
        """
        Optimize venue order considering:
        1. Logical day/night flow (cafes → restaurants → bars)
        2. Opening hours validation
        3. Travel time optimization
        
        Args:
            venues: List of venue dictionaries
            start_time: When the plan starts (for time appropriateness calculation)
            
        Returns:
            Optimized venue list
        """
        if len(venues) <= 1:
            return venues
        
        # Use current time if no start time provided
        if start_time is None:
            start_time = datetime.now().replace(hour=19, minute=0, second=0, microsecond=0)  # Default 7 PM
        
        self.logger.info(f"Optimizing venue order for {len(venues)} venues starting at {start_time.strftime('%H:%M')}")
        
        # Step 1: Sort venues by logical day/night flow and time appropriateness
        venues_with_scores = []
        for venue in venues:
            priority_score = self.get_venue_priority_score(venue, start_time)
            venues_with_scores.append((venue, priority_score))
        
        # Sort by priority score (lower = earlier in day)
        venues_with_scores.sort(key=lambda x: x[1])
        logical_order = [venue for venue, score in venues_with_scores]
        
        # Log the logical ordering
        for i, (venue, score) in enumerate(venues_with_scores):
            venue_type = venue.get("venue_type", "unknown")
            venue_name = venue.get("name", "Unknown")
            self.logger.info(f"  {i+1}. {venue_name} ({venue_type}) - Priority Score: {score:.2f}")
        
        # Step 2: Apply travel time optimization while preserving logical flow
        # Only swap adjacent venues if it significantly reduces travel time
        optimized = self.apply_travel_optimization(logical_order)
        
        self.logger.info(f"✅ Optimized venue order: {' → '.join([v.get('venue_type', 'unknown') for v in optimized])}")
        return optimized
    
    def apply_travel_optimization(self, venues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply travel time optimization while preserving logical venue type flow
        Only swap adjacent venues if travel time savings are significant
        """
        if len(venues) <= 2:
            return venues
        
        optimized = venues.copy()
        improved = True
        
        # Multiple passes to find optimal adjacent swaps
        while improved:
            improved = False
            
            for i in range(len(optimized) - 1):
                current_order = optimized[i:i+2]
                swapped_order = [optimized[i+1], optimized[i]]
                
                # Calculate travel time for both orders
                current_travel = self.calculate_total_travel_time(current_order)
                swapped_travel = self.calculate_total_travel_time(swapped_order)
                
                # Only swap if travel time improvement is significant (>0.5 km saved)
                travel_savings_km = current_travel - swapped_travel
                
                # Also check if swapping doesn't violate logical flow too much
                type_conflict_penalty = self.calculate_type_conflict_penalty(
                    optimized[i], optimized[i+1]
                )
                
                # Swap if travel savings outweigh type conflict penalty
                if travel_savings_km > 0.5 and travel_savings_km > type_conflict_penalty:
                    optimized[i], optimized[i+1] = optimized[i+1], optimized[i]
                    improved = True
                    self.logger.info(f"🔄 Swapped {optimized[i+1].get('venue_type')} and {optimized[i].get('venue_type')} to save {travel_savings_km:.1f}km travel")
        
        return optimized
    
    def calculate_total_travel_time(self, venues: List[Dict[str, Any]]) -> float:
        """Calculate total travel distance for a sequence of venues"""
        if len(venues) <= 1:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(venues) - 1):
            lat1 = venues[i]["location"]["latitude"]
            lon1 = venues[i]["location"]["longitude"]
            lat2 = venues[i+1]["location"]["latitude"]
            lon2 = venues[i+1]["location"]["longitude"]
            
            distance = self.calculate_distance(lat1, lon1, lat2, lon2)
            total_distance += distance
        
        return total_distance
    
    def calculate_type_conflict_penalty(self, venue1: Dict[str, Any], venue2: Dict[str, Any]) -> float:
        """
        Calculate penalty for swapping two venues based on type priority conflict
        Higher penalty = less desirable to swap
        """
        type1 = venue1.get("venue_type", "other").lower()
        type2 = venue2.get("venue_type", "other").lower()
        
        priority1 = self.VENUE_TYPE_PRIORITIES.get(type1, 5)
        priority2 = self.VENUE_TYPE_PRIORITIES.get(type2, 5)
        
        # If swapping would put a later-day venue before an earlier-day venue,
        # apply penalty proportional to the priority difference
        if priority2 < priority1:  # venue2 should come before venue1
            return abs(priority1 - priority2) * 0.3  # Penalty in "km equivalent"
        
        return 0.0  # No penalty if order is logical
    
    def get_plan_summary(self, timed_venues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of the plan timing
        """
        if not timed_venues:
            return {}
        
        total_venue_time = sum(venue.get("duration_minutes", 0) for venue in timed_venues)
        total_travel_time = sum(venue.get("travel_time_from_previous", 0) for venue in timed_venues)
        total_buffer_time = (len(timed_venues) - 1) * self.TRANSITION_BUFFER
        
        start_time = timed_venues[0].get("start_time")
        end_time = timed_venues[-1].get("end_time")
        
        total_distance = sum(venue.get("travel_distance_km", 0.0) for venue in timed_venues)
        
        return {
            "plan_start_time": start_time,
            "plan_end_time": end_time,
            "total_duration_minutes": total_venue_time + total_travel_time + total_buffer_time,
            "total_venue_time_minutes": total_venue_time,
            "total_travel_time_minutes": total_travel_time,
            "total_buffer_time_minutes": total_buffer_time,
            "total_distance_km": round(total_distance, 2),
            "number_of_venues": len(timed_venues)
        }

# Global instance
time_calculator = TimeCalculator()
