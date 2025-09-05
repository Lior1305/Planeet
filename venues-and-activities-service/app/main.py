from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.api.routes import router
from app.services.cleanup_service import cleanup_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Starting Venues Service...")
    try:
        await cleanup_service.start_cleanup()
        logger.info("Cleanup service started successfully")
    except Exception as e:
        logger.error(f"Failed to start cleanup service: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Venues Service...")
    try:
        await cleanup_service.stop_cleanup()
        logger.info("Cleanup service stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping cleanup service: {e}")

app = FastAPI(
    title="Venues Service",
    description="A comprehensive service for managing venues with advanced search and filtering capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(router)

# Also include the same router with /api/v1 prefix for compatibility with planning service
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Venues Service",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.post("/cleanup/manual")
async def manual_cleanup():
    """Manually trigger venues cleanup"""
    try:
        await cleanup_service.manual_cleanup()
        return {"message": "Manual cleanup completed successfully"}
    except Exception as e:
        logger.error(f"Manual cleanup failed: {e}")
        return {"error": f"Manual cleanup failed: {str(e)}"}

@app.get("/cleanup/status")
async def cleanup_status():
    """Get cleanup service status"""
    return {
        "is_running": cleanup_service.is_running,
        "cleanup_interval_minutes": cleanup_service.cleanup_interval_minutes
    }
