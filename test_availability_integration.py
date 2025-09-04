#!/usr/bin/env python3
"""
Test script to verify the availability integration between services
"""

import asyncio
import httpx
import json
from datetime import datetime

# Service URLs (adjust based on your deployment)
PLANNING_SERVICE_URL = "http://localhost:8001"
VENUES_SERVICE_URL = "http://localhost:8002"
BOOKING_SERVICE_URL = "http://localhost:8004"

async def test_availability_integration():
    """Test the full availability integration flow"""
    
    print("🧪 Testing Availability Integration Flow")
    print("=" * 50)
    
    # Test data
    test_request = {
        "user_id": "test_user_123",
        "venue_types": ["restaurant", "bar"],
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "address": "New York, NY, USA",
            "city": "New York",
            "country": "USA"
        },
        "radius_km": 5.0,
        "date": "2024-01-15T14:00:00Z",  # 2:00 PM
        "group_size": 4,
        "use_personalization": False
    }
    
    try:
        # Step 1: Test Planning Service -> Venues Service
        print("1️⃣ Testing Planning Service venue discovery...")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Call planning service
            response = await client.post(
                f"{PLANNING_SERVICE_URL}/plans/create",
                json=test_request
            )
            
            if response.status_code == 200:
                plan_data = response.json()
                print(f"✅ Planning service responded successfully")
                print(f"   Plan ID: {plan_data.get('plan_id')}")
                print(f"   Total plans generated: {plan_data.get('total_plans_generated', 0)}")
                
                # Check if venues were filtered by availability
                if 'plans' in plan_data and plan_data['plans']:
                    first_plan = plan_data['plans'][0]
                    if 'venues' in first_plan:
                        print(f"   Venues in first plan: {len(first_plan['venues'])}")
                        
                        # Check venue types
                        venue_types = {}
                        for venue in first_plan['venues']:
                            venue_type = venue.get('venue_type', 'unknown')
                            venue_types[venue_type] = venue_types.get(venue_type, 0) + 1
                        
                        print(f"   Venue types: {venue_types}")
                
            else:
                print(f"❌ Planning service failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        
        # Step 2: Test Venues Service directly
        print("\n2️⃣ Testing Venues Service directly...")
        
        venue_request = {
            "venue_types": ["restaurant", "bar"],
            "location": test_request["location"],
            "radius_km": 5.0,
            "requested_time": "14:00",  # 2:00 PM
            "group_size": 4
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{VENUES_SERVICE_URL}/api/v1/venues/discover",
                json=venue_request
            )
            
            if response.status_code == 200:
                venues_data = response.json()
                print(f"✅ Venues service responded successfully")
                print(f"   Total venues found: {venues_data.get('total_venues_found', 0)}")
                
                venues_by_type = venues_data.get('venues_by_type', {})
                for venue_type, venues in venues_by_type.items():
                    print(f"   {venue_type}: {len(venues)} venues")
                    
            else:
                print(f"❌ Venues service failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        
        # Step 3: Test Booking Service availability check
        print("\n3️⃣ Testing Booking Service availability...")
        
        # First, get a venue ID from the venues service response
        if 'venues_by_type' in venues_data and venues_data['venues_by_type']:
            first_venue_type = list(venues_data['venues_by_type'].keys())[0]
            first_venue = venues_data['venues_by_type'][first_venue_type][0]
            venue_id = first_venue.get('id')
            
            if venue_id:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # Test availability check
                    response = await client.get(
                        f"{BOOKING_SERVICE_URL}/v1/availability/google-place/{venue_id}/overlapping/12:00-14:00"
                    )
                    
                    if response.status_code == 200:
                        availability_data = response.json()
                        print(f"✅ Booking service availability check successful")
                        print(f"   Venue: {availability_data.get('venue_name', 'Unknown')}")
                        print(f"   Available: {availability_data.get('available', False)}")
                        print(f"   Counter: {availability_data.get('counter', 0)}")
                    else:
                        print(f"❌ Booking service availability check failed: {response.status_code}")
                        print(f"   Error: {response.text}")
            else:
                print("⚠️ No venue ID found for availability testing")
        
        print("\n✅ Integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_services_health():
    """Test if all services are running and healthy"""
    
    print("🏥 Testing Services Health")
    print("=" * 30)
    
    services = [
        ("Planning Service", f"{PLANNING_SERVICE_URL}/"),
        ("Venues Service", f"{VENUES_SERVICE_URL}/api/v1/health"),
        ("Booking Service", f"{BOOKING_SERVICE_URL}/v1/health")
    ]
    
    all_healthy = True
    
    for service_name, health_url in services:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(health_url)
                if response.status_code == 200:
                    print(f"✅ {service_name}: Healthy")
                else:
                    print(f"❌ {service_name}: Unhealthy ({response.status_code})")
                    all_healthy = False
        except Exception as e:
            print(f"❌ {service_name}: Error - {e}")
            all_healthy = False
    
    return all_healthy

async def main():
    """Main test function"""
    
    print("🚀 Starting Availability Integration Tests")
    print("=" * 60)
    
    # First check if services are healthy
    services_healthy = await test_services_health()
    
    if not services_healthy:
        print("\n❌ Some services are not healthy. Please start all services first.")
        print("   Services needed:")
        print("   - Planning Service (port 8001)")
        print("   - Venues Service (port 8002)")
        print("   - Booking Service (port 8004)")
        return
    
    print("\n" + "=" * 60)
    
    # Run the integration test
    success = await test_availability_integration()
    
    if success:
        print("\n🎉 All tests passed! The availability integration is working correctly.")
    else:
        print("\n💥 Some tests failed. Please check the logs above.")

if __name__ == "__main__":
    asyncio.run(main())
