from dataclasses import dataclass
from typing import Optional

@dataclass
class Profile:
    """Profile data model"""
    user_id: str
    name: str
    id: Optional[str] = None
    
    def to_dict(self):
        """Convert profile to dictionary"""
        return {
            "user_id": self.user_id,
            "name": self.name
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create profile from dictionary"""
        return cls(
            user_id=data.get("user_id"),
            name=data.get("name")
        ) 