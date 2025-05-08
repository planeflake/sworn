# START OF FILE app/game_state/entities/settlement.py

from .base import BaseEntity
# Import KW_ONLY and field
from dataclasses import dataclass, field, KW_ONLY
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime

@dataclass
class Settlement(BaseEntity):
    """
    Represents a Settlement in the game (Domain Entity).
    Uses KW_ONLY to separate non-default positional args from others.
    """
    # --- Positional, Non-default fields FIRST ---
    # This will be the only required positional argument
    world_id: UUID

    # --- Positional fields with defaults NEXT ---
    # These can still be positional, but have defaults
    description: Optional[str] = None
    buildings: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # --- Keyword-Only Separator ---
    # All fields defined *after* this MUST be specified by keyword
    # when creating an instance (e.g., Settlement(world_id=..., entity_id=...))
    _: KW_ONLY

    # --- Keyword-Only fields (inherited, re-declared with defaults) ---
    # Marking these as keyword-only ensures they don't interfere
    # with the positional argument order check.
    entity_id: UUID = field(default_factory=uuid4)
    name: str = "Unnamed Entity"

# END OF FILE app/game_state/entities/settlement.py