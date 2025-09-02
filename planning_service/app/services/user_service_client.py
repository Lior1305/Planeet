"""
User Service Client for Planning Service
Handles all communication with the users-service
"""

import logging
from typing import Dict, Any, Optional
import aiohttp
from app.core.config import USERS_SERVICE_URL

logger = logging.getLogger(__name__)

class UserServiceClient:
    """Client for communicating with the users-service"""
    
    def __init__(self):
        self.base_url = USERS_SERVICE_URL
        self.timeout = aiohttp.ClientTimeout(total=10)
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by email address
        
        Args:
            email: User's email address
            
        Returns:
            User data dictionary or None if not found
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.base_url}/users/by-email"
                params = {"email": email}
                
                logger.info(f"Fetching user by email: {email}")
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        logger.info(f"Successfully found user: {user_data.get('username', 'Unknown')}")
                        return user_data
                    elif response.status == 404:
                        logger.warning(f"User not found with email: {email}")
                        return None
                    else:
                        logger.error(f"Unexpected response status {response.status} for email {email}")
                        return None
                        
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching user by email {email}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching user by email {email}: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Get user information by user ID
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User data dictionary (returns default values if not found)
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.base_url}/users/{user_id}"
                
                logger.info(f"Fetching user by ID: {user_id}")
                async with session.get(url) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        logger.info(f"Successfully found user: {user_data.get('username', 'Unknown')}")
                        return user_data
                    elif response.status == 404:
                        logger.warning(f"User not found with ID: {user_id}")
                        return self._get_default_user_data()
                    else:
                        logger.error(f"Unexpected response status {response.status} for user ID {user_id}")
                        return self._get_default_user_data()
                        
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching user by ID {user_id}: {e}")
            return self._get_default_user_data()
        except Exception as e:
            logger.error(f"Unexpected error fetching user by ID {user_id}: {e}")
            return self._get_default_user_data()
    
    async def verify_user_exists(self, user_id: str) -> bool:
        """
        Verify if a user exists by ID
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            True if user exists, False otherwise
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.base_url}/users/{user_id}"
                
                async with session.get(url) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Error verifying user existence {user_id}: {e}")
            return False
    
    def _get_default_user_data(self) -> Dict[str, Any]:
        """Return default user data when user is not found"""
        return {
            "username": "Unknown",
            "email": "unknown@email.com",
            "id": "unknown"
        }
    
    async def health_check(self) -> bool:
        """
        Check if the users service is healthy
        
        Returns:
            True if service is responding, False otherwise
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.base_url}/health"
                
                async with session.get(url) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Users service health check failed: {e}")
            return False


# Global client instance
user_service_client = UserServiceClient()
