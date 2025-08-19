from fastapi import FastAPI
from app.api.routes import router as v1_router

app = FastAPI(title="Planning Service")

app.include_router(v1_router, prefix="/v1")