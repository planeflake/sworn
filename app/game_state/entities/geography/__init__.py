"""Geography entities module.

This module contains entities related to geographical features
like zones, biomes, and settlements.
"""

from app.game_state.entities.geography.zone import Zone, ZoneEntity
from app.game_state.entities.geography.zone_pydantic import ZonePydantic
from app.game_state.entities.geography.biome import BiomeEntity
from app.game_state.entities.geography.biome_pydantic import BiomeEntityPydantic
from app.game_state.entities.geography.settlement import SettlementEntity
from app.game_state.entities.geography.settlement_pydantic import SettlementEntityPydantic

# Convenience aliases
Biome = BiomeEntity
Settlement = SettlementEntity