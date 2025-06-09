from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4
from typing import  Optional, List
from datetime import datetime

class BaseEntityPydantic(BaseModel):
    """
    Base class for all domain entities in the game state.
    Provides common fields like entity_id, name, timestamps, and metadata.
    """
    # Keep defaults to maintain current behavior
    id: UUID = Field(default_factory=uuid4)
    name: str = "Unnamed Entity"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    # Common fields
    tags: List[str] = Field(default_factory=list)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id!r}, name={self.name!r})"

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        extra='ignore'  # Ignore extra attributes from SQLAlchemy models
    )