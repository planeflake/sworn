"""
Simple Theme entity model
"""
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class ThemeEntity:
    """ theme state """
    id: UUID = uuid4()
    name: str = "Default World"
    description: str = "Default Description"
    created_at: datetime = None
    updated_at: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {"day": self.name, "description": self.description}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeEntity':
        """Create from dictionary"""
        return cls(name=data.get("name", 0), description=data.get("description", 0))