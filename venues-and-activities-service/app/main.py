from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="Venues Service",
    description="A comprehensive service for managing venues with advanced search and filtering capabilities",
    version="1.0.0"
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

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Venues Service",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }
