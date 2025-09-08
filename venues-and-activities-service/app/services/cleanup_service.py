"""
Cleanup service for managing scheduled data deletion from venues collection.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from app.db import get_venues_collection

logger = logging.getLogger(__name__)

class VenuesCleanupService:
    """Service to handle periodic cleanup of venues collection data."""
    
    def __init__(self, cleanup_interval_minutes: int = 20):
        self.cleanup_interval_minutes = cleanup_interval_minutes
        self.cleanup_task: Optional[asyncio.Task] = None
        self.is_running = False
        
    async def start_cleanup(self):
        """Start the periodic cleanup task."""
        if self.is_running:
            logger.warning("Cleanup service is already running")
            return
            
        self.is_running = True
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info(f"Started venues cleanup service - will delete venues data every {self.cleanup_interval_minutes} minutes")
        
    async def stop_cleanup(self):
        """Stop the periodic cleanup task."""
        if not self.is_running:
            logger.warning("Cleanup service is not running")
            return
            
        self.is_running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped venues cleanup service")
        
    async def _cleanup_loop(self):
        """Main cleanup loop that runs every specified interval."""
        while self.is_running:
            try:
                await self._delete_venues_data()
                logger.info(f"Cleanup completed. Next cleanup in {self.cleanup_interval_minutes} minutes")
                
                # Wait for the specified interval
                await asyncio.sleep(self.cleanup_interval_minutes * 60)
                
            except asyncio.CancelledError:
                logger.info("Cleanup service was cancelled")
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                # Wait a bit before retrying to avoid rapid error loops
                await asyncio.sleep(60)
                
    async def _delete_venues_data(self):
        """Delete all data from the venues collection."""
        try:
            venues_collection = get_venues_collection()
            
            # Get count before deletion for logging
            count_before = await asyncio.get_event_loop().run_in_executor(
                None, venues_collection.count_documents, {}
            )
            
            if count_before == 0:
                logger.info("No venues data to delete")
                return
                
            # Delete all documents from venues collection
            result = await asyncio.get_event_loop().run_in_executor(
                None, venues_collection.delete_many, {}
            )
            
            deleted_count = result.deleted_count
            logger.info(f"Successfully deleted {deleted_count} venues from collection at {datetime.now()}")
            
        except Exception as e:
            logger.error(f"Failed to delete venues data: {e}")
            raise
            
    async def manual_cleanup(self):
        """Manually trigger cleanup (useful for testing or immediate cleanup)."""
        logger.info("Manual cleanup triggered")
        await self._delete_venues_data()

# Global cleanup service instance
cleanup_service = VenuesCleanupService(cleanup_interval_minutes=20)
