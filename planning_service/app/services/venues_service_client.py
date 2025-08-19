"""
Client service for Planning Service to communicate with Venues Service
"""

import httpx
from typing import Optional, Dict, Any
import logging
from app.core.config import VENUES_SERVICE_URL

logger = logging.getLogger(__name__)

class VenuesServiceClient:
    """Client for communicating with the Venues Service"""
    
    def __init__(self, venues_service_url: str = None):
        self.venues_service_url = venues_service_url or VENUES_SERVICE_URL
        self.client = httpx.AsyncClient(timeout=60.0)  # Longer timeout for plan generation
    
    async def generate_venue_plan(self, plan_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Request venue plan generation from Venues Service
        
        Args:
            plan_request: Complete plan request with user requirements
            
        Returns:
            Plan response with venue suggestions if successful, None otherwise
        """
        try:
            response = await self.client.post(
                f"{self.venues_service_url}/api/v1/plans/generate",
                json=plan_request
            )
            
            if response.status_code == 200:
                plan_response = response.json()
                logger.info(f"Venue plan generated successfully for plan {plan_request.get('plan_id')}")
                return plan_response
            else:
                logger.error(f"Failed to generate venue plan: {response.status_code} - {response.text}")
                return None
                
        except httpx.RequestError as e:
            logger.error(f"Request error when generating venue plan: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error when generating venue plan: {e}")
            return None
    
    async def get_venue_details(self, venue_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific venue
        
        Args:
            venue_id: The venue identifier
            
        Returns:
            Venue details if found, None otherwise
        """
        try:
            response = await self.client.get(
                f"{self.venues_service_url}/api/v1/venues/{venue_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.info(f"Venue {venue_id} not found")
                return None
            else:
                logger.error(f"Error fetching venue {venue_id}: {response.status_code}")
                return None
                
        except httpx.RequestError as e:
            logger.error(f"Request error when fetching venue {venue_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error when fetching venue {venue_id}: {e}")
            return None
    
    async def search_venues(self, search_criteria: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Search for venues using the Venues Service search endpoint
        
        Args:
            search_criteria: Search parameters
            
        Returns:
            Search results if successful, None otherwise
        """
        try:
            response = await self.client.post(
                f"{self.venues_service_url}/api/v1/search",
                json=search_criteria
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Venue search failed: {response.status_code} - {response.text}")
                return None
                
        except httpx.RequestError as e:
            logger.error(f"Request error when searching venues: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error when searching venues: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global instance
venues_service_client = VenuesServiceClient() 