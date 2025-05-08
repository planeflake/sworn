# START OF FILE app/game_state/entities/base.py

from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Any # For type hinting

@dataclass
class BaseEntity:
    """
    Base class for all domain entities in the game state.
    Provides common fields like entity_id and name.
    """
    # Use UUID for entity_id, provide a default factory
    entity_id: UUID = field(default_factory=uuid4)

    # Provide a default name
    name: str = "Unnamed Entity"

    # __post_init__ can be used for validation or complex initialization
    # def __post_init__(self):
    #     if not self.name:
    #         raise ValueError("Entity name cannot be empty")

    def __repr__(self) -> str:
        # Use the correct attribute name 'entity_id'
        return f"{self.__class__.__name__}(entity_id={self.entity_id!r}, name={self.name!r})"

    def __str__(self) -> str:
        return f"{self.name} ({self.entity_id})"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the domain entity to a basic dictionary.
        NOTE: dataclasses.asdict is often more comprehensive.
        """
        # Use the correct attribute name 'entity_id'
        return {
            'entity_id': str(self.entity_id), # Convert UUID to string for simple dicts
            'name': self.name,
            # Add other base fields if any
        }

# END OF FILE app/game_state/entities/base.py