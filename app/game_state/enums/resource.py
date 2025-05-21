# app/game_state/enums/resource_owner_type.py

from enum import Enum

class ResourceOwnerType(str, Enum):
    CHARACTER = "character"         # Players and NPCs
    SETTLEMENT = "settlement"       # Towns, outposts
    ZONE = "zone"                   # Regional (e.g., forest, swamp)
    AREA = "area"                   # Room, glade, cave
    WORLD = "world"                 # Global/system pool
    BUILDING = "building"           # Lootable or functional buildings
    FACTION = "faction"             # Shared stash for guilds, groups
    CREATURE = "creature"           # Monsters (e.g., dragons)
    ANIMAL = "animal"               # Non-humanoid animals (e.g., goats, wolves)
    CONTAINER = "container"         # Chests, barrels, crates
    QUEST = "quest"                 # Rewards, quest-banked resources
    VEHICLE = "vehicle"             # Carts, ships, siege engines
