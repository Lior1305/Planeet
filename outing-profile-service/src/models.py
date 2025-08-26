from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class Profile:
    """Profile data model with outing history included"""
    user_id: str
    name: str
    outing_history: Optional[List[Dict[str, Any]]] = None
    id: Optional[str] = None
    
    def to_dict(self):
        """Convert profile to dictionary"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "outing_history": self.outing_history or []
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create profile from dictionary"""
        return cls(
            user_id=data.get("user_id"),
            name=data.get("name"),
            outing_history=data.get("outing_history", [])
        ) 