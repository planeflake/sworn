# Entities Module

This module contains all the domain entities used in the game state. Each entity is a representation of a game concept and should be treated as an immutable data structure.

## Module Structure

The entities module is organized into the following submodules:

- **core/**: Base entities and fundamental types
  - `base.py` - The base dataclass entity
  - `base_pydantic.py` - The base pydantic entity
  - `theme.py` - Theme entity
  - `pydantic_bridge.py` - Utilities for converting between dataclass and pydantic entities

- **world/**: World-level entities
  - `world.py` - World entity

- **geography/**: Geographical entities
  - `zone.py` - Zone entity
  - `biome.py` - Biome entity
  - `settlement.py` - Settlement entity

- **character/**: Character-related entities
  - `character.py` - Character entity
  - `stat.py` - Stat entity
  - `equipment.py` - Equipment entity
  - `item.py` - Item entity

- **building/**: Building-related entities
  - `building.py` - Building entity
  - `building_blueprint.py` - Building blueprint entity
  - `building_instance.py` - Building instance entity
  - `building_upgrade_blueprint.py` - Building upgrade blueprint entity

- **skill/**: Skill and profession entities
  - `skill.py` - Skill entity
  - `skill_definition.py` - Skill definition entity
  - `profession_definition.py` - Profession definition entity

- **resource/**: Resource-related entities
  - `resource.py` - Resource entity
  - `resource_blueprint.py` - Resource blueprint entity
  - `resource_node.py` - Resource node entity

- **economy/**: Economy-related entities
  - `currency.py` - Currency entity

## Importing Entities

You can import entities in two ways:

1. From the top-level module (recommended for most cases):

```python
from app.game_state.entities import (
    WorldEntity,
    CharacterEntity,
    BuildingEntity,
    # etc.
)
```

2. From specific submodules (useful for more focused imports):

```python
from app.game_state.entities.character import CharacterEntity, StatEntity
from app.game_state.entities.building import BuildingBlueprintEntity
```

## Dataclass vs. Pydantic Entities

Each entity is available in two formats:

1. Dataclass-based entities (original)
2. Pydantic-based entities (new)

Pydantic entities provide better validation and schema generation. They are named with the same class name as the dataclass entities but with a `_pydantic.py` suffix in the filename.

You can convert between the two formats using the functions in `pydantic_bridge.py`:

```python
from app.game_state.entities import dataclass_to_pydantic, pydantic_to_dataclass
from app.game_state.entities import WorldEntity, WorldEntityPydantic

# Convert from dataclass to pydantic
world_dataclass = WorldEntity(name="My World")
world_pydantic = dataclass_to_pydantic(world_dataclass, WorldEntityPydantic)

# Convert from pydantic to dataclass
world_dataclass_again = pydantic_to_dataclass(world_pydantic, WorldEntity)
```