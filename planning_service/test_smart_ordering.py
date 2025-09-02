#!/usr/bin/env python3
"""
Test script for the enhanced smart venue ordering system

This script tests the new venue ordering logic that considers:
1. Logical day/night flow (cafes → restaurants → bars)
2. Opening hours validation  
3. Travel time optimization
"""

import asyncio
import json
from datetime import datetime
import httpx

# Test scenarios with different times and venue combinations
TEST_SCENARIOS = [
    {
        "name": "Morning Start (10 AM) - Should prioritize cafe first",
        "request": {
            "user_id": "test-ordering-user",
            "plan_id": "test-morning-ordering",
            "location": {"latitude": 40.7589, "longitude": -73.9851, "city": "New York"},
            "date": "2025-01-20T10:00:00",  # 10 AM start
            "group_size": 2,
            "venue_types": ["cafe", "restaurant", "bar"],
            "max_venues": 3,
            "budget_per_person": 100
        },
        "expected_order": ["cafe", "restaurant", "bar"]
    },
    {
        "name": "Evening Start (7 PM) - Should prioritize restaurant first",
        "request": {
            "user_id": "test-ordering-user", 
            "plan_id": "test-evening-ordering",
            "location": {"latitude": 40.7589, "longitude": -73.9851, "city": "New York"},
            "date": "2025-01-20T19:00:00",  # 7 PM start
            "group_size": 3,
            "venue_types": ["cafe", "restaurant", "bar"],
            "max_venues": 3,
            "budget_per_person": 150
        },
        "expected_order": ["restaurant", "bar", "cafe"]  # Cafe might be last due to evening timing
    },
    {
        "name": "Late Night Start (10 PM) - Should prioritize bar first",
        "request": {
            "user_id": "test-ordering-user",
            "plan_id": "test-night-ordering", 
            "location": {"latitude": 40.7589, "longitude": -73.9851, "city": "New York"},
            "date": "2025-01-20T22:00:00",  # 10 PM start
            "group_size": 2,
            "venue_types": ["bar", "restaurant", "cafe"],
            "max_venues": 3,
            "budget_per_person": 120
        },
        "expected_order": ["bar", "restaurant", "cafe"]  # Only bar appropriate for late night
    },
    {
        "name": "Mixed Cultural Day (2 PM) - Museum should come early",
        "request": {
            "user_id": "test-ordering-user",
            "plan_id": "test-cultural-ordering",
            "location": {"latitude": 40.7589, "longitude": -73.9851, "city": "New York"},
            "date": "2025-01-20T14:00:00",  # 2 PM start
            "group_size": 2,
            "venue_types": ["museum", "restaurant", "bar"],
            "max_venues": 3,
            "budget_per_person": 100
        },
        "expected_order": ["museum", "restaurant", "bar"]
    }
]

PLANNING_SERVICE_URL = "http://localhost:8001/v1"

async def test_venue_ordering():
    """Test the enhanced venue ordering with different scenarios"""
    
    print("🧪 Testing Enhanced Smart Venue Ordering System")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, scenario in enumerate(TEST_SCENARIOS, 1):
            print(f"\n📋 Test {i}: {scenario['name']}")
            print("-" * 50)
            
            try:
                # Create plan
                response = await client.post(
                    f"{PLANNING_SERVICE_URL}/plans/create",
                    json=scenario["request"]
                )
                
                if response.status_code != 200:
                    print(f"❌ Failed to create plan: {response.status_code}")
                    print(f"   Response: {response.text}")
                    continue
                
                result = response.json()
                plans = result.get("plans", [])
                
                if not plans:
                    print("❌ No plans generated")
                    continue
                
                # Analyze the first plan's venue ordering
                plan = plans[0]
                venues = plan.get("suggested_venues", [])
                
                if not venues:
                    print("❌ No venues in plan")
                    continue
                
                # Extract venue types in order
                actual_order = [venue.get("venue_type") for venue in venues]
                expected_order = scenario["expected_order"]
                
                print(f"📅 Start Time: {scenario['request']['date']}")
                print(f"🎯 Expected Order: {' → '.join(expected_order)}")
                print(f"✨ Actual Order:   {' → '.join(actual_order)}")
                
                # Show detailed venue information
                print(f"\n🏢 Venue Details:")
                for j, venue in enumerate(venues, 1):
                    name = venue.get("name", "Unknown")
                    venue_type = venue.get("venue_type", "unknown")
                    start_time = venue.get("start_time", "N/A")
                    end_time = venue.get("end_time", "N/A")
                    rating = venue.get("rating", "N/A")
                    
                    print(f"   {j}. {name} ({venue_type})")
                    print(f"      ⏰ {start_time} - {end_time}")
                    print(f"      ⭐ Rating: {rating}")
                
                # Check if ordering follows logical flow
                logical_score = calculate_logical_score(actual_order, scenario['request']['date'])
                print(f"\n📊 Logical Flow Score: {logical_score:.1f}/10")
                
                if logical_score >= 7.0:
                    print("✅ GOOD: Venue ordering follows logical day/night flow")
                elif logical_score >= 5.0:
                    print("⚠️  OKAY: Venue ordering is acceptable")
                else:
                    print("❌ POOR: Venue ordering needs improvement")
                
            except Exception as e:
                print(f"❌ Error testing scenario: {e}")
    
    print(f"\n🎉 Smart Venue Ordering Test Complete!")
    print("=" * 60)

def calculate_logical_score(venue_order: list, start_time_str: str) -> float:
    """
    Calculate how logical the venue ordering is based on time and venue types
    Returns score from 0-10 (10 = perfect logical flow)
    """
    if not venue_order:
        return 0.0
    
    # Parse start time
    start_time = datetime.fromisoformat(start_time_str)
    start_hour = start_time.hour
    
    # Venue type priorities (lower = earlier in day)
    priorities = {
        "cafe": 1, "museum": 2, "park": 3, "shopping_center": 4,
        "sports_facility": 5, "spa": 6, "restaurant": 7, 
        "theater": 8, "bar": 9, "other": 5
    }
    
    # Time appropriateness scoring
    def get_time_score(venue_type, hour):
        appropriateness = {
            "cafe": {"good": (7, 16), "poor": (20, 6)},
            "museum": {"good": (9, 17), "poor": (18, 9)},
            "restaurant": {"good": (11, 23), "poor": (2, 11)},
            "bar": {"good": (17, 2), "poor": (6, 17)}
        }
        
        if venue_type not in appropriateness:
            return 5.0  # Neutral score
        
        good_range = appropriateness[venue_type]["good"]
        poor_range = appropriateness[venue_type]["poor"]
        
        def in_range(h, start, end):
            if start <= end:
                return start <= h <= end
            else:  # crosses midnight
                return h >= start or h <= end
        
        if in_range(hour, *good_range):
            return 8.0
        elif in_range(hour, *poor_range):
            return 2.0
        else:
            return 5.0
    
    total_score = 0.0
    
    # Score for logical progression (each venue should have higher or equal priority)
    progression_score = 0.0
    for i in range(len(venue_order) - 1):
        current_priority = priorities.get(venue_order[i], 5)
        next_priority = priorities.get(venue_order[i + 1], 5)
        
        if next_priority >= current_priority:
            progression_score += 2.0  # Good progression
        else:
            progression_score -= 1.0  # Poor progression
    
    # Score for time appropriateness of first venue
    first_venue_time_score = get_time_score(venue_order[0], start_hour)
    
    # Combine scores
    max_progression_score = (len(venue_order) - 1) * 2.0 if len(venue_order) > 1 else 2.0
    normalized_progression = max(0, min(6.0, (progression_score / max_progression_score) * 6.0))
    normalized_time_score = (first_venue_time_score / 8.0) * 4.0
    
    total_score = normalized_progression + normalized_time_score
    
    return min(10.0, max(0.0, total_score))

if __name__ == "__main__":
    asyncio.run(test_venue_ordering())
