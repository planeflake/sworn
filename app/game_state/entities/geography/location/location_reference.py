"""
Location reference entity for referring to locations with type information.
"""
from uuid import UUID
from pydantic import BaseModel
from typing import Optional

class LocationReference(BaseModel):
    """
    Reference to a location with type information.
    Used for parent-child relationships between locations.
    """
    location_id: UUID
    location_type_id: UUID
    location_type_code: Optional[str] = None  # For convenience
    
    def __str__(self) -> str:
        """String representation of the reference."""
        if self.location_type_code:
            return f"{self.location_type_code}:{self.location_id}"
        return f"{self.location_type_id}:{self.location_id}"