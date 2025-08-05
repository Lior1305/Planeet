from pydantic import BaseModel
from typing import List, Optional

class OutingPreferences(BaseModel):
    city: str
    date: str
    time_of_day: str
    group_size: int
    venue_type: str
    special_requests: Optional[List[str]] = []

class OutingProfile(BaseModel):
    user_id: str
    name: str
    history: Optional[List[dict]] = []
