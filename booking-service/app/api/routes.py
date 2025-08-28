from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

router = APIRouter()

@router.get("/")
def home():
    return {"message": "Booking Service Running"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Booking Service",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
