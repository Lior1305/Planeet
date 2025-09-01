"""
Time calculation service for venue plans
Calculates start/end times, durations, and travel times between venues
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import math
import logging

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
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
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
    
    def optimize_venue_order(self, venues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Optimize the order of venues to minimize total travel time
        Simple nearest-neighbor approach
        """
        if len(venues) <= 2:
            return venues
        
        optimized = [venues[0]]  # Start with first venue
        remaining = venues[1:].copy()
        
        while remaining:
            current_venue = optimized[-1]
            current_lat = current_venue["location"]["latitude"]
            current_lon = current_venue["location"]["longitude"]
            
            # Find nearest remaining venue
            min_distance = float('inf')
            nearest_venue = None
            nearest_index = -1
            
            for i, venue in enumerate(remaining):
                venue_lat = venue["location"]["latitude"]
                venue_lon = venue["location"]["longitude"]
                
                distance = self.calculate_distance(current_lat, current_lon, venue_lat, venue_lon)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_venue = venue
                    nearest_index = i
            
            if nearest_venue:
                optimized.append(nearest_venue)
                remaining.pop(nearest_index)
        
        self.logger.info(f"Optimized venue order to minimize travel time")
        return optimized
    
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
