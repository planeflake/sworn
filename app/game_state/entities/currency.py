from dataclasses import dataclass, field, KW_ONLY
from uuid import UUID
from datetime import datetime, UTC
from typing import Optional, Dict, Any

from app.game_state.entities.base import BaseEntity

@dataclass(kw_only=True)
class CurrencyEntity(BaseEntity):
    """
    Represents a form of currency used in a world or region.
    """

    _: KW_ONLY

    world_id: UUID
    theme_id: UUID
    faction_id: Optional[UUID] = None

    code: str = "GC"
    exchange_rate: float = 1.0
    precision: int = 2
    symbol: str = "¤"
    symbol_position: str = "prefix"
    active: bool = True

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert CurrencyEntity to a dictionary with safe serialization."""
        # Manually create dictionary instead of using asdict to avoid inheritance issues
        data = {
            "id": str(self.entity_id),
            "name": self.name,
            "world_id": str(self.world_id),
            "theme_id": str(self.theme_id),
            "faction_id": str(self.faction_id) if self.faction_id else None,
            "code": self.code,
            "exchange_rate": self.exchange_rate,
            "precision": self.precision,
            "symbol": self.symbol,
            "symbol_position": self.symbol_position,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        return data

# For backward compatibility
Currency = CurrencyEntity