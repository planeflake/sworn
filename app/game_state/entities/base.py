from dataclasses import dataclass, field, KW_ONLY
from uuid import UUID, uuid4
from typing import Any

@dataclass
class BaseEntity:
    """
    Base class for all domain entities in the game state.
    Provides common fields like entity_id and name.
    """

    entity_id: UUID = field(default_factory=uuid4)
    name: str = "Unnamed Entity"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(entity_id={self.entity_id!r}, name={self.name!r})"

    def __str__(self) -> str:
        return f"{self.name} ({self.entity_id})"

    def to_dict(self) -> dict[str, Any]:
        return {
            'entity_id': str(self.entity_id),
            'name': self.name,
        }
