"""
Service for integrating with the Outing-Profile-Service to fetch user preferences
and provide personalized venue recommendations.
"""

import httpx
from typing import Optional, Dict, Any
from app.models.schemas import UserPreferences
import logging

logger = logging.getLogger(__name__)

class OutingProfileIntegration:
    """Service for integrating with the Outing-Profile-Service"""
    
    def __init__(self, outing_profile_service_url: str = "http://localhost:8002"):
        self.outing_profile_service_url = outing_profile_service_url
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """
        Fetch user preferences from the Outing-Profile-Service
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            UserPreferences object if found, None otherwise
        """
        try:
            response = await self.client.get(
                f"{self.outing_profile_service_url}/preferences/{user_id}"
            )
            
            if response.status_code == 200:
                data = response.json()
                return UserPreferences(**data)
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
    
    async def get_user_outing_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch user outing profile from the Outing-Profile-Service
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            Profile data if found, None otherwise
        """
        try:
            response = await self.client.get(
                f"{self.outing_profile_service_url}/profile/{user_id}"
            )
            
            if response.status_code == 200:
                return response.json()
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
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global instance
planning_integration = OutingProfileIntegration() 