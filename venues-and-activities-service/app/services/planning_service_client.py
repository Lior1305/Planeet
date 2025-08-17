"""
Client service for Venues Service to communicate back to Planning Service
"""

import httpx
from typing import Optional, Dict, Any
from app.models.schemas import Venue
import logging

logger = logging.getLogger(__name__)

class PlanningServiceClient:
    """Client for communicating back to the Planning Service"""
    
    def __init__(self, planning_service_url: str = "http://localhost:8001"):
        self.planning_service_url = planning_service_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def send_plan_response(self, plan_response: Dict[str, Any]) -> bool:
        """
        Send plan response back to Planning Service
        
        Args:
            plan_response: The complete plan response with venue suggestions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.post(
                f"{self.planning_service_url}/v1/plans/response",
                json=plan_response
            )
            
            if response.status_code == 200:
                logger.info(f"Plan response sent successfully for plan {plan_response.get('plan_id')}")
                return True
            else:
                logger.error(f"Failed to send plan response: {response.status_code} - {response.text}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Request error when sending plan response: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when sending plan response: {e}")
            return False
    
    async def update_plan_status(self, plan_id: str, status: str, message: str = None) -> bool:
        """
        Update plan status in Planning Service
        
        Args:
            plan_id: The plan identifier
            status: New status (processing, completed, failed, etc.)
            message: Optional status message
            
        Returns:
            True if successful, False otherwise
        """
        try:
            update_data = {
                "plan_id": plan_id,
                "status": status
            }
            if message:
                update_data["message"] = message
            
            response = await self.client.put(
                f"{self.planning_service_url}/v1/plans/{plan_id}/status",
                json=update_data
            )
            
            if response.status_code == 200:
                logger.info(f"Plan status updated to {status} for plan {plan_id}")
                return True
            else:
                logger.error(f"Failed to update plan status: {response.status_code}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Request error when updating plan status: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when updating plan status: {e}")
            return False
    
    async def notify_plan_completion(self, plan_id: str, venue_count: int) -> bool:
        """
        Notify Planning Service that venue discovery is complete
        
        Args:
            plan_id: The plan identifier
            venue_count: Number of venues found
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notification_data = {
                "plan_id": plan_id,
                "venue_count": venue_count,
                "status": "venues_discovered"
            }
            
            response = await self.client.post(
                f"{self.planning_service_url}/v1/plans/{plan_id}/notify",
                json=notification_data
            )
            
            if response.status_code == 200:
                logger.info(f"Plan completion notified for plan {plan_id}")
                return True
            else:
                logger.error(f"Failed to notify plan completion: {response.status_code}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Request error when notifying plan completion: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when notifying plan completion: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global instance
planning_service_client = PlanningServiceClient() 