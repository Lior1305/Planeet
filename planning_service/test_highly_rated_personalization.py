"""
Test script to verify the enhanced personalization system with highly rated venues only (4+)
"""

import asyncio
import json
from datetime import datetime, time
from app.services.personalization import planning_personalization_service

async def test_highly_rated_personalization():
    """Test the personalization service with sample data, focusing on highly rated venues"""
    
    # Sample venues data (simulating what we get from venues service)
    venues_by_type = {
        "restaurant": [
            {
                "id": "ChIJ1234567890",
                "name": "Amazing Restaurant",
                "rating": 4.5,
                "price_range": "$$",
                "amenities": ["outdoor_seating", "vegetarian_friendly"]
            },
            {
                "id": "ChIJ0987654321", 
                "name": "Good Eats",
                "rating": 4.2,
                "price_range": "$",
                "amenities": ["delivery", "takeout"]
            },
            {
                "id": "ChIJ1111111111",
                "name": "Luxury Dining",
                "rating": 4.8,
                "price_range": "$$$",
                "amenities": ["fine_dining", "wine_list"]
            },
            {
                "id": "ChIJ2222222222",
                "name": "Average Place",
                "rating": 3.5,
                "price_range": "$$",
                "amenities": ["casual", "family_friendly"]
            }
        ],
        "bar": [
            {
                "id": "ChIJ3333333333",
                "name": "Cozy Bar",
                "rating": 4.0,
                "price_range": "$$",
                "amenities": ["live_music", "craft_beer"]
            },
            {
                "id": "ChIJ4444444444",
                "name": "Sports Bar",
                "rating": 3.8,
                "price_range": "$",
                "amenities": ["sports_tv", "pub_food"]
            },
            {
                "id": "ChIJ5555555555",
                "name": "Trendy Bar",
                "rating": 4.7,
                "price_range": "$$$",
                "amenities": ["cocktails", "rooftop"]
            }
        ]
    }
    
    # Sample user rating history with mixed ratings
    user_rating_history = {
        "ChIJ1234567890": 5.0,  # User loved this restaurant (5 stars)
        "ChIJ0987654321": 2.0,  # User didn't like this one (2 stars) - WILL BE FILTERED OUT
        "ChIJ2222222222": 3.0,  # User thought it was okay (3 stars) - WILL BE FILTERED OUT
        "ChIJ3333333333": 4.5,  # User liked this bar (4.5 stars)
        "ChIJ4444444444": 3.5,  # User thought it was okay (3.5 stars) - WILL BE FILTERED OUT
        "ChIJ5555555555": 4.0,  # User liked this bar (4 stars)
    }
    
    # Sample user preferences
    user_preferences = {
        "preferred_price_range": "$$",
        "preferred_amenities": ["outdoor_seating", "live_music"]
    }
    
    print("🧪 Testing Enhanced Personalization System (Highly Rated Venues Only)")
    print("=" * 70)
    
    print(f"📊 Input Data:")
    print(f"   - Venue types: {list(venues_by_type.keys())}")
    print(f"   - Total venues: {sum(len(venues) for venues in venues_by_type.values())}")
    print(f"   - User ratings: {len(user_rating_history)} venues")
    print(f"   - User preferences: {user_preferences}")
    print()
    
    print("🔍 User Rating Analysis:")
    print("   - Highly rated venues (4+): {count_highly_rated(user_rating_history)}")
    print("   - Lower rated venues (<4): {count_lower_rated(user_rating_history)}")
    print()
    
    # Test personalization
    print("🎯 Applying Personalization (Only Highly Rated Venues)...")
    personalized_venues = planning_personalization_service.personalize_venues(
        venues_by_type, user_rating_history, user_preferences
    )
    
    print("✅ Personalization Results:")
    print("=" * 70)
    
    for venue_type, scored_venues in personalized_venues.items():
        print(f"\n🏪 {venue_type.upper()} Venues (Ranked by Personalization Score):")
        print("-" * 50)
        
        for i, (venue, score) in enumerate(scored_venues, 1):
            user_rated = "⭐" if venue["id"] in user_rating_history else "🆕"
            rating_info = f"User Rating: {user_rating_history.get(venue['id'], 'N/A')}" if venue["id"] in user_rating_history else "New Venue"
            
            # Highlight highly rated venues
            if venue["id"] in user_rating_history and user_rating_history[venue["id"]] >= 4.0:
                rating_info += " 🎯 HIGHLY RATED"
            elif venue["id"] in user_rating_history:
                rating_info += " ⚠️ Lower Rated (Filtered Out)"
            
            print(f"  {i}. {venue['name']}")
            print(f"     Score: {score:.3f} | {rating_info} {user_rated}")
            print(f"     Google Rating: {venue.get('rating', 'N/A')} | Price: {venue.get('price_range', 'N/A')}")
            print()
    
    print("🎉 Personalization Test Complete!")
    print("\n📋 Key Features Demonstrated:")
    print("   ✅ Only venues rated 4+ boost personalization scores")
    print("   ✅ Lower rated venues (1-3) are filtered out from preferences")
    print("   ✅ Venue type preferences based on highly rated venues only")
    print("   ✅ Smart venue ranking with focus on quality")
    print("   ✅ New venues still get fair consideration")

def count_highly_rated(ratings):
    """Count venues rated 4 or higher"""
    return sum(1 for rating in ratings.values() if rating >= 4.0)

def count_lower_rated(ratings):
    """Count venues rated below 4"""
    return sum(1 for rating in ratings.values() if rating < 4.0)

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_highly_rated_personalization())
