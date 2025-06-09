"""Economy entities module.

This module contains entities related to the game economy,
including currencies and economic systems.
"""

# Primary Pydantic entities (RECOMMENDED)
from app.game_state.entities.economy.currency_pydantic import CurrencyEntityPydantic

# Legacy dataclass entities (for backward compatibility)
try:
    from app.game_state.entities.economy.currency import CurrencyEntity, Currency
except ImportError:
    # Graceful degradation if legacy entities are removed
    CurrencyEntity = CurrencyEntityPydantic
    Currency = CurrencyEntityPydantic

# Convenience aliases pointing to Pydantic entities (RECOMMENDED)
Currency = CurrencyEntityPydantic