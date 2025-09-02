"""
Test script for Group Planning Feature
Run this to test the new group planning functionality
"""

import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any

# Configuration
PLANNING_SERVICE_URL = "http://localhost:8001/v1"  # Updated to correct port and prefix
USERS_SERVICE_URL = "http://localhost:8080"     # Adjust port as needed

async def test_group_planning_flow():
    """Test the complete group planning flow"""
    
    async with aiohttp.ClientSession() as session:
        print("🧪 Testing Group Planning Feature")
        print("=" * 50)
        
        # Step 1: Create a test plan request
        print("\n1️⃣ Creating test plan...")
        
        tomorrow = datetime.now() + timedelta(days=1)
        plan_request = {
            "user_id": "test-user-1",
            "venue_types": ["restaurant", "bar"],
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "city": "New York",
                "address": "New York, NY"
            },
            "radius_km": 10.0,
            "date": tomorrow.isoformat(),
            "group_size": 3,  # Testing with 3 people (creator + 2 invites)
            "budget_range": "$$",
            "min_rating": 4.0,
            "use_personalization": False
        }
        
        try:
            async with session.post(
                f"{PLANNING_SERVICE_URL}/plans/create",
                json=plan_request
            ) as response:
                if response.status == 200:
                    plan_data = await response.json()
                    plan_id = plan_data.get("plan_id")
                    print(f"✅ Plan created successfully: {plan_id}")
                    print(f"   Generated {len(plan_data.get('plans', []))} plan options")
                else:
                    print(f"❌ Plan creation failed: {response.status}")
                    print(await response.text())
                    return
        except Exception as e:
            print(f"❌ Error creating plan: {e}")
            return
        
        # Step 2: Test plan confirmation with participants
        print("\n2️⃣ Confirming plan with group participants...")
        
        confirmation_request = {
            "plan_id": plan_id,
            "selected_plan_index": 0,  # Select the first plan
            "participant_emails": [
                "participant1@example.com",
                "participant2@example.com"
            ]
        }
        
        try:
            async with session.post(
                f"{PLANNING_SERVICE_URL}/plans/{plan_id}/confirm",
                json=confirmation_request
            ) as response:
                if response.status == 200:
                    confirmed_data = await response.json()
                    print("✅ Plan confirmed successfully!")
                    print(f"   Total participants: {confirmed_data.get('total_participants')}")
                    print(f"   Participants added: {confirmed_data.get('participants_added')}")
                    
                    # Print participant details
                    confirmed_plan = confirmed_data.get("confirmed_plan", {})
                    participants = confirmed_plan.get("participants", [])
                    print("\n   Participants:")
                    for p in participants:
                        print(f"   - {p.get('name', 'Unknown')} ({p.get('email')}) - {p.get('status')}")
                        
                else:
                    print(f"❌ Plan confirmation failed: {response.status}")
                    print(await response.text())
                    return
        except Exception as e:
            print(f"❌ Error confirming plan: {e}")
            return
        
        # Step 3: Test getting confirmed plan details
        print("\n3️⃣ Retrieving confirmed plan details...")
        
        try:
            async with session.get(
                f"{PLANNING_SERVICE_URL}/plans/{plan_id}/confirmed"
            ) as response:
                if response.status == 200:
                    confirmed_plan = await response.json()
                    print("✅ Confirmed plan retrieved successfully!")
                    print(f"   Plan ID: {confirmed_plan.get('plan_id')}")
                    print(f"   Creator: {confirmed_plan.get('creator_user_id')}")
                    print(f"   Group size: {confirmed_plan.get('group_size')}")
                else:
                    print(f"❌ Failed to get confirmed plan: {response.status}")
        except Exception as e:
            print(f"❌ Error getting confirmed plan: {e}")
        
        # Step 4: Test participant response (simulate user accepting invitation)
        print("\n4️⃣ Testing participant response...")
        
        # Find a pending participant
        participants = confirmed_plan.get("participants", [])
        pending_participant = None
        for p in participants:
            if p.get("status") == "pending":
                pending_participant = p
                break
        
        if pending_participant:
            try:
                async with session.post(
                    f"{PLANNING_SERVICE_URL}/plans/{plan_id}/participants/{pending_participant['user_id']}/respond",
                    json={"status": "confirmed"}
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        print("✅ Participant response recorded successfully!")
                        print(f"   User {pending_participant['user_id']} confirmed participation")
                    else:
                        print(f"❌ Participant response failed: {response.status}")
                        print(await response.text())
            except Exception as e:
                print(f"❌ Error in participant response: {e}")
        else:
            print("ℹ️  No pending participants found to test response")
        
        # Step 5: Test email validation
        print("\n5️⃣ Testing email validation...")
        
        invalid_confirmation = {
            "plan_id": plan_id,
            "selected_plan_index": 0,
            "participant_emails": [
                "invalid-email",  # This should fail validation
                "valid@example.com"
            ]
        }
        
        try:
            async with session.post(
                f"{PLANNING_SERVICE_URL}/plans/{plan_id}/confirm",
                json=invalid_confirmation
            ) as response:
                if response.status == 422:  # Validation error expected
                    print("✅ Email validation working correctly (rejected invalid email)")
                else:
                    print(f"⚠️  Expected validation error, got: {response.status}")
        except Exception as e:
            print(f"ℹ️  Email validation test: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Group Planning Feature Test Complete!")
        print("\nNext steps:")
        print("- Test with real user emails in your system")
        print("- Integrate with frontend UI")
        print("- Test outing history display")
        print("- Add email notifications (future enhancement)")

async def test_users_service_email_lookup():
    """Test the new email lookup functionality in users service"""
    print("\n🔍 Testing Users Service Email Lookup...")
    
    async with aiohttp.ClientSession() as session:
        # Test email lookup
        test_email = "test@example.com"
        
        try:
            async with session.get(
                f"{USERS_SERVICE_URL}/users/by-email?email={test_email}"
            ) as response:
                if response.status == 200:
                    user_data = await response.json()
                    print(f"✅ Email lookup working: Found user {user_data.get('username')}")
                elif response.status == 404:
                    print(f"ℹ️  Email lookup working: User with email {test_email} not found (as expected)")
                else:
                    print(f"❌ Unexpected response: {response.status}")
        except Exception as e:
            print(f"❌ Error testing email lookup: {e}")

if __name__ == "__main__":
    print("Starting Group Planning Feature Tests...")
    print("Make sure your services are running:")
    print(f"- Planning Service: {PLANNING_SERVICE_URL}")
    print(f"- Users Service: {USERS_SERVICE_URL}")
    print(f"- Outing Profile Service: http://localhost:5000")
    
    # Run the tests
    asyncio.run(test_users_service_email_lookup())
    asyncio.run(test_group_planning_flow())
