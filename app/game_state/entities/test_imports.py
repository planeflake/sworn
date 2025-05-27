#!/usr/bin/env python3
"""
Test script to verify that the new import structure is working correctly.
"""

print("Testing entity imports...")

# Test top-level imports
try:
    from app.game_state.entities import (
        BaseEntity, BaseEntityPydantic,
        ThemeEntity, ThemeEntityPydantic,
        WorldEntity, WorldEntityPydantic,
        BiomeEntity, BiomeEntityPydantic,
        ZoneEntity, ZonePydantic,
        CharacterEntity, CharacterEntityPydantic,
        BuildingEntity, BuildingEntityPydantic,
        ResourceEntity, ResourceEntityPydantic,
        SkillEntity, SkillEntityPydantic,
        dataclass_to_pydantic, pydantic_to_dataclass
    )
    print("✅ Top-level imports successful")
except ImportError as e:
    print(f"❌ Top-level imports failed: {e}")

# Test core module imports
try:
    from app.game_state.entities.core import (
        BaseEntity, BaseEntityPydantic,
        ThemeEntity, ThemeEntityPydantic,
        dataclass_to_pydantic, pydantic_to_dataclass
    )
    print("✅ Core module imports successful")
except ImportError as e:
    print(f"❌ Core module imports failed: {e}")

# Test world module imports
try:
    from app.game_state.entities.world import (
        WorldEntity, WorldEntityPydantic, World
    )
    print("✅ World module imports successful")
except ImportError as e:
    print(f"❌ World module imports failed: {e}")

# Test geography module imports
try:
    from app.game_state.entities.geography import (
        BiomeEntity, BiomeEntityPydantic,
        ZoneEntity, ZonePydantic,
        SettlementEntity, SettlementEntityPydantic
    )
    print("✅ Geography module imports successful")
except ImportError as e:
    print(f"❌ Geography module imports failed: {e}")

# Test character module imports
try:
    from app.game_state.entities.character import (
        CharacterEntity, CharacterEntityPydantic,
        StatEntity, StatEntityPydantic,
        EquipmentEntity, EquipmentEntityPydantic,
        ItemEntity, ItemEntityPydantic
    )
    print("✅ Character module imports successful")
except ImportError as e:
    print(f"❌ Character module imports failed: {e}")

# Test building module imports
try:
    from app.game_state.entities.building import (
        BuildingEntity, BuildingEntityPydantic,
        BuildingBlueprintEntity, BuildingBlueprintPydantic,
        BuildingInstanceEntity, BuildingInstanceEntityPydantic,
        BuildingUpgradeBlueprintEntity, BuildingUpgradeBlueprintEntityPydantic
    )
    print("✅ Building module imports successful")
except ImportError as e:
    print(f"❌ Building module imports failed: {e}")

# Test skill module imports
try:
    from app.game_state.entities.skill import (
        SkillEntity, SkillEntityPydantic,
        SkillDefinitionEntity, SkillDefinitionEntityPydantic,
        ProfessionDefinitionEntity, ProfessionDefinitionEntityPydantic
    )
    print("✅ Skill module imports successful")
except ImportError as e:
    print(f"❌ Skill module imports failed: {e}")

# Test resource module imports
try:
    from app.game_state.entities.resource import (
        ResourceEntity, ResourceEntityPydantic,
        ResourceBlueprint, ResourceNode
    )
    print("✅ Resource module imports successful")
except ImportError as e:
    print(f"❌ Resource module imports failed: {e}")

# Test economy module imports
try:
    from app.game_state.entities.economy import (
        CurrencyEntity, CurrencyEntityPydantic
    )
    print("✅ Economy module imports successful")
except ImportError as e:
    print(f"❌ Economy module imports failed: {e}")

print("Import tests completed!")