from pydantic import BaseModel
from app.models.outing import OutingPreferences

class Plan(BaseModel):
    user_id: str
    plan_description: str
    preferences: OutingPreferences
