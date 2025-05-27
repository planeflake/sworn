from pydantic import Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any, Literal

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class CurrencyEntityPydantic(BaseEntityPydantic):
    """
    Represents a form of currency used in a world or region.
    """
    world_id: UUID
    theme_id: UUID
    faction_id: Optional[UUID] = None

    code: str = "GC"
    exchange_rate: float = 1.0
    precision: int = 2
    symbol: str = "¤"
    symbol_position: Literal["prefix", "suffix"] = "prefix"
    active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert CurrencyEntity to a dictionary with safe serialization."""
        # Get base entity fields
        data = super().to_dict()
        
        # Add currency-specific fields
        currency_data = {
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
            "active": self.active
        }
        
        data.update(currency_data)
        return data
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Gold Coin",
                "world_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "theme_id": "550e8400-e29b-41d4-a716-446655440000",
                "code": "GC",
                "exchange_rate": 1.0,
                "precision": 2,
                "symbol": "🪙",
                "symbol_position": "prefix",
                "active": True
            }
        }
    )

# For backward compatibility
Currency = CurrencyEntityPydantic