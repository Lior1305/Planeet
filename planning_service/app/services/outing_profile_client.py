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
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global instance
outing_profile_client = OutingProfileClient() 