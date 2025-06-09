"""Character entities module.

This module contains entities related to characters, 
including their stats, equipment, and items.
"""

# Primary Pydantic entities (RECOMMENDED)
from app.game_state.entities.character.character_pydantic import CharacterEntityPydantic
from app.game_state.entities.character.stat_pydantic import StatEntityPydantic
from app.game_state.entities.character.equipment_pydantic import EquipmentEntityPydantic
from app.game_state.entities.character.item_pydantic import ItemEntityPydantic

# Legacy dataclass entities (for backward compatibility)
try:
    from app.game_state.entities.character.character import CharacterEntity
    from app.game_state.entities.character.stat import StatEntity
    from app.game_state.entities.character.equipment import EquipmentEntity
    from app.game_state.entities.character.item import ItemEntity, Item
except ImportError:
    # Graceful degradation if legacy entities are removed
    CharacterEntity = CharacterEntityPydantic
    StatEntity = StatEntityPydantic
    EquipmentEntity = EquipmentEntityPydantic
    ItemEntity = ItemEntityPydantic
    Item = ItemEntityPydantic

# Convenience aliases pointing to Pydantic entities (RECOMMENDED)
Character = CharacterEntityPydantic
Stat = StatEntityPydantic
Equipment = EquipmentEntityPydantic