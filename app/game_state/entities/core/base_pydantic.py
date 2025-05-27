from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4
from typing import Any, Optional, Dict, List
from datetime import datetime

class BaseEntityPydantic(BaseModel):
    """
    Base class for all domain entities in the game state.
    Provides common fields like entity_id, name, timestamps, and metadata.
    """
    # Keep defaults to maintain current behavior
    entity_id: UUID = Field(default_factory=uuid4)
    name: str = "Unnamed Entity"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    # Common metadata fields
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(entity_id={self.entity_id!r}, name={self.name!r})"

    def __str__(self) -> str:
        return f"{self.name} ({self.entity_id})"

    def to_dict(self) -> dict[str, Any]:
        """Convert entity to a dictionary representation with serialized values."""
        return {
            'entity_id': str(self.entity_id),
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tags': self.tags,
            'metadata': self.metadata  # Using 'metadata' consistently
        }
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )