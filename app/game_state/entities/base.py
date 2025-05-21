from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Any, Optional, Dict, List
from datetime import datetime

@dataclass
class BaseEntity:
    """
    Base class for all domain entities in the game state.
    Provides common fields like entity_id, name, timestamps, and metadata.
    """
    # Keep defaults to maintain current behavior
    entity_id: UUID = field(default_factory=uuid4)
    name: str = "Unnamed Entity"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    # Common metadata fields
    tags: List[str] = field(default_factory=list)
    _metadata: Dict[str, Any] = field(default_factory=dict)

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
            '_metadata': self._metadata,
        }