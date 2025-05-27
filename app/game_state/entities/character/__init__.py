"""Character entities module.

This module contains entities related to characters, 
including their stats, equipment, and items.
"""

from app.game_state.entities.character.character import CharacterEntity
from app.game_state.entities.character.character_pydantic import CharacterEntityPydantic
from app.game_state.entities.character.stat import StatEntity
from app.game_state.entities.character.stat_pydantic import StatEntityPydantic
from app.game_state.entities.character.equipment import EquipmentEntity
from app.game_state.entities.character.equipment_pydantic import EquipmentEntityPydantic
from app.game_state.entities.character.item import ItemEntity, Item
from app.game_state.entities.character.item_pydantic import ItemEntityPydantic

# Convenience aliases
Character = CharacterEntity
Stat = StatEntity
Equipment = EquipmentEntity