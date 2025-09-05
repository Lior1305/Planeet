"""
Client service for Planning Service to communicate with Outing-Profile-Service
"""

import httpx
from typing import Optional, Dict, Any
import logging
from app.core.config import OUTING_PROFILE_SERVICE_URL

logger = logging.getLogger(__name__)

class OutingProfileClient:
    """Client for communicating with the Outing-Profile-Service"""
    
    def __init__(self, outing_profile_service_url: str = None):
        self.outing_profile_service_url = outing_profile_service_url or OUTING_PROFILE_SERVICE_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user outing preferences from Outing-Profile-Service
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            User preferences if found, None otherwise
        """
        try:
            response = await self.client.get(
                f"{self.outing_profile_service_url}/profiles?user_id={user_id}"
            )
            
            if response.status_code == 200:
                preferences = response.json()
                logger.info(f"Retrieved preferences for user {user_id}")
                return preferences
            elif response.status_code == 404:
                logger.info(f"No preferences found for user {user_id}")
                return None
            else:
                logger.error(f"Error fetching preferences for user {user_id}: {response.status_code}")
                return None
                
        except httpx.RequestError as e:
            logger.error(f"Request error when fetching preferences for user {user_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error when fetching preferences for user {user_id}: {e}")
            return None
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user outing profile from Outing-Profile-Service
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            User profile if found, None otherwise
        """
        try:
            response = await self.client.get(
                f"{self.outing_profile_service_url}/profiles?user_id={user_id}"
            )
            
            if response.status_code == 200:
                profile = response.json()
                logger.info(f"Retrieved profile for user {user_id}")
                return profile
            elif response.status_code == 404:
                logger.info(f"No profile found for user {user_id}")
                return None
            else:
                logger.error(f"Error fetching profile for user {user_id}: {response.status_code}")
                return None
                
        except httpx.RequestError as e:
            logger.error(f"Request error when fetching profile for user {user_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error when fetching profile for user {user_id}: {e}")
            return None
    
    async def create_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Create or update user preferences in Outing-Profile-Service
        
        Args:
            user_id: The user's unique identifier
            preferences: User preferences data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.post(
                f"{self.outing_profile_service_url}/preferences/{user_id}",
                json=preferences
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Preferences created/updated for user {user_id}")
                return True
            else:
                logger.error(f"Failed to create preferences for user {user_id}: {response.status_code}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Request error when creating preferences for user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when creating preferences for user {user_id}: {e}")
            return False
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update existing user preferences in Outing-Profile-Service
        
        Args:
            user_id: The user's unique identifier
            preferences: Updated preferences data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.put(
                f"{self.outing_profile_service_url}/preferences/{user_id}",
                json=preferences
            )
            
            if response.status_code == 200:
                logger.info(f"Preferences updated for user {user_id}")
                return True
            else:
                logger.error(f"Failed to update preferences for user {user_id}: {response.status_code}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Request error when updating preferences for user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when updating preferences for user {user_id}: {e}")
            return False
    
    async def delete_user_preferences(self, user_id: str) -> bool:
        """
        Delete user preferences from Outing-Profile-Service
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.delete(
                f"{self.outing_profile_service_url}/preferences/{user_id}"
            )
            
            if response.status_code == 200:
                logger.info(f"Preferences deleted for user {user_id}")
                return True
            else:
                logger.error(f"Failed to delete preferences for user {user_id}: {response.status_code}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Request error when deleting preferences for user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when deleting preferences for user {user_id}: {e}")
            return False
    
    async def get_user_venue_ratings(self, user_id: str) -> Dict[str, float]:
        """
        Get user's venue rating history from Outing-Profile-Service
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            Dictionary mapping venue_id to average rating (e.g., {"venue_id": 4.5})
        """
        try:
            response = await self.client.get(
                f"{self.outing_profile_service_url}/outing-history?user_id={user_id}"
            )
            
            if response.status_code == 200:
                data = response.json()
                past_outings = data.get("past_outings", [])
                
                # Extract venue ratings from all past outings
                venue_ratings = {}
                venue_rating_counts = {}
                
                for outing in past_outings:
                    ratings = outing.get("venue_ratings", [])
                    for rating_entry in ratings:
                        venue_id = rating_entry.get("venue_id")
                        rating = rating_entry.get("rating")
                        
                        if venue_id and rating:
                            if venue_id not in venue_ratings:
                                venue_ratings[venue_id] = 0
                                venue_rating_counts[venue_id] = 0
                            
                            venue_ratings[venue_id] += rating
                            venue_rating_counts[venue_id] += 1
                
                # Calculate average ratings
                avg_ratings = {}
                for venue_id, total_rating in venue_ratings.items():
                    avg_ratings[venue_id] = total_rating / venue_rating_counts[venue_id]
                
                logger.info(f"Retrieved {len(avg_ratings)} venue ratings for user {user_id}")
                return avg_ratings
                
            elif response.status_code == 404:
                logger.info(f"No rating history found for user {user_id}")
                return {}
            else:
                logger.error(f"Error fetching ratings for user {user_id}: {response.status_code}")
                return {}
                
        except httpx.RequestError as e:
            logger.error(f"Request error when fetching ratings for user {user_id}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error when fetching ratings for user {user_id}: {e}")
            return {}
    
    async def add_outing_history(self, outing_data: Dict[str, Any]) -> bool:
        """
        Add an outing to user's history in Outing-Profile-Service
        
        Args:
            outing_data: Dictionary containing outing information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.post(
                f"{self.outing_profile_service_url}/outing-history",
                json=outing_data
            )
            
            if response.status_code == 201:
                logger.info(f"Outing history added for user {outing_data.get('user_id')}")
                return True
            else:
                logger.error(f"Failed to add outing history: {response.status_code} - {response.text}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Request error when adding outing history: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when adding outing history: {e}")
            return False
    
    async def update_outing_status(self, plan_id: str, user_id: str, status: str) -> bool:
        """
        Update outing status in user's history
        
        Args:
            plan_id: The plan identifier
            user_id: The user identifier
            status: New status ('planned', 'completed', 'cancelled')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.put(
                f"{self.outing_profile_service_url}/outing-history/{plan_id}",
                json={"user_id": user_id, "status": status}
            )
            
            if response.status_code == 200:
                logger.info(f"Outing status updated for plan {plan_id}, user {user_id}")
                return True
            else:
                logger.error(f"Failed to update outing status: {response.status_code} - {response.text}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Request error when updating outing status: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when updating outing status: {e}")
            return False
    
    async def update_outing_confirmation(self, plan_id: str, user_id: str, confirmed: bool = True) -> bool:
        """
        Update outing confirmation status in user's history
        
        Args:
            plan_id: The plan identifier
            user_id: The user identifier
            confirmed: Whether the user confirmed the outing (True/False)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.put(
                f"{self.outing_profile_service_url}/outing-history/{plan_id}/confirm",
                json={"user_id": user_id, "confirmed": confirmed}
            )
            
            if response.status_code == 200:
                status_text = "confirmed" if confirmed else "unconfirmed"
                logger.info(f"Outing {status_text} for plan {plan_id}, user {user_id}")
                return True
            else:
                logger.error(f"Failed to update outing confirmation: {response.status_code} - {response.text}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Request error when updating outing confirmation: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when updating outing confirmation: {e}")
            return False
    
    async def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific plan by ID from outing history
        
        Args:
            plan_id: The plan identifier
            
        Returns:
            Plan data if found, None otherwise
        """
        try:
            response = await self.client.get(
                f"{self.outing_profile_service_url}/plans/{plan_id}"
            )
            
            if response.status_code == 200:
                plan_data = response.json()
                logger.info(f"Retrieved plan: {plan_id}")
                return plan_data
            elif response.status_code == 404:
                logger.info(f"Plan not found: {plan_id}")
                return None
            else:
                logger.error(f"Error retrieving plan {plan_id}: {response.status_code}")
                return None
                
        except httpx.RequestError as e:
            logger.error(f"Request error when retrieving plan {plan_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error when retrieving plan {plan_id}: {e}")
            return None
    
    async def get_user_plans(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get all plans for a specific user from outing history
        
        Args:
            user_id: The user identifier
            
        Returns:
            User plans data if found, None otherwise
        """
        try:
            response = await self.client.get(
                f"{self.outing_profile_service_url}/plans?user_id={user_id}"
            )
            
            if response.status_code == 200:
                plans_data = response.json()
                logger.info(f"Retrieved {len(plans_data.get('plans', []))} plans for user {user_id}")
                return plans_data
            else:
                logger.error(f"Error retrieving plans for user {user_id}: {response.status_code}")
                return None
                
        except httpx.RequestError as e:
            logger.error(f"Request error when retrieving plans for user {user_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error when retrieving plans for user {user_id}: {e}")
            return None
    
    async def add_participants_to_plan(self, plan_id: str, participants: list) -> bool:
        """
        Add participants to an existing plan
        
        Args:
            plan_id: The plan identifier
            participants: List of participant data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.post(
                f"{self.outing_profile_service_url}/plans/{plan_id}/participants",
                json={"participants": participants}
            )
            
            if response.status_code == 200:
                logger.info(f"Added {len(participants)} participants to plan {plan_id}")
                return True
            else:
                logger.error(f"Failed to add participants to plan {plan_id}: {response.status_code} - {response.text}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Request error when adding participants to plan {plan_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when adding participants to plan {plan_id}: {e}")
            return False
    
    async def update_creator_plan_participants(self, plan_id: str, creator_user_id: str, new_participants: list) -> bool:
        """
        Update the creator's plan with new participants
        
        Args:
            plan_id: The plan identifier
            creator_user_id: The creator's user ID
            new_participants: List of new participants to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.put(
                f"{self.outing_profile_service_url}/plans/{plan_id}/creator-participants",
                json={
                    "creator_user_id": creator_user_id,
                    "new_participants": new_participants
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Updated creator's plan {plan_id} with {len(new_participants)} new participants")
                return True
            else:
                logger.error(f"Failed to update creator's plan {plan_id}: {response.status_code} - {response.text}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Request error when updating creator's plan {plan_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when updating creator's plan {plan_id}: {e}")
            return False

    async def respond_to_plan_invitation(self, plan_id: str, user_id: str, status: str) -> bool:
        """
        Allow participants to respond to plan invitation
        
        Args:
            plan_id: The plan identifier
            user_id: The user identifier
            status: Response status ('confirmed' or 'declined')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.put(
                f"{self.outing_profile_service_url}/plans/{plan_id}/participants/{user_id}/respond",
                json={"status": status}
            )
            
            if response.status_code == 200:
                logger.info(f"User {user_id} {status} invitation for plan {plan_id}")
                return True
            else:
                logger.error(f"Failed to respond to invitation: {response.status_code} - {response.text}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Request error when responding to invitation: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when responding to invitation: {e}")
            return False

    async def cancel_plan_for_everyone(self, plan_id: str, creator_user_id: str) -> bool:
        """
        Cancel a plan for all participants (creator only)
        
        Args:
            plan_id: The plan identifier
            creator_user_id: The creator's user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.post(
                f"{self.outing_profile_service_url}/plans/{plan_id}/cancel",
                json={
                    "creator_user_id": creator_user_id
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Plan {plan_id} cancelled for all participants")
                return True
            else:
                logger.error(f"Failed to cancel plan for everyone: {response.status_code}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Request error when cancelling plan for everyone: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when cancelling plan for everyone: {e}")
            return False

    async def delete_plan_for_everyone(self, plan_id: str, creator_user_id: str) -> bool:
        """
        Delete a plan for all participants (creator only)
        
        Args:
            plan_id: The plan identifier
            creator_user_id: The creator's user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.post(
                f"{self.outing_profile_service_url}/plans/{plan_id}/delete",
                json={
                    "creator_user_id": creator_user_id
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Plan {plan_id} deleted for all participants")
                return True
            else:
                logger.error(f"Failed to delete plan for everyone: {response.status_code}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Request error when deleting plan for everyone: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when deleting plan for everyone: {e}")
            return False

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global instance
outing_profile_client = OutingProfileClient() 