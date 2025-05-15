"""
Building attribute enums and mapping to character traits.
This module defines the attribute types for buildings and 
how they relate to character traits.
"""
import enum
from typing import Dict, List, Set

class BuildingAttributeType(enum.Enum):
    """
    Defines the attribute types that buildings can have.
    These are used in the _metadata field of BuildingBlueprint.
    """
    DEFENSIVE = "DEFENSIVE"         # Maps to DEFENSIVE trait
    ECONOMIC = "ECONOMIC"           # Maps to ECONOMICAL trait
    EXPANSION = "EXPANSION"         # Maps to EXPANSIVE trait
    CULTURAL = "CULTURAL"           # Maps to CULTURAL trait
    SPIRITUAL = "SPIRITUAL"         # Maps to SPIRITUAL trait
    MILITARY = "MILITARY"           # Maps to AGGRESSIVE/STRATEGIC traits
    RESIDENTIAL = "RESIDENTIAL"     # Housing/population buildings
    PRODUCTION = "PRODUCTION"       # Resource production buildings
    ADMINISTRATIVE = "ADMINISTRATIVE" # Governance buildings
    INFRASTRUCTURE = "INFRASTRUCTURE" # Basic infrastructure

# Mapping from character traits to building attributes
# This defines which building attributes are preferred by different character traits
TRAIT_TO_ATTRIBUTE_MAP: Dict[str, Set[str]] = {
    "DEFENSIVE": {
        BuildingAttributeType.DEFENSIVE.value, 
        BuildingAttributeType.MILITARY.value
    },
    "AGGRESSIVE": {
        BuildingAttributeType.MILITARY.value, 
        BuildingAttributeType.EXPANSION.value
    },
    "SUPPORTIVE": {
        BuildingAttributeType.RESIDENTIAL.value, 
        BuildingAttributeType.INFRASTRUCTURE.value
    },
    "STRATEGIC": {
        BuildingAttributeType.DEFENSIVE.value, 
        BuildingAttributeType.MILITARY.value, 
        BuildingAttributeType.ADMINISTRATIVE.value
    },
    "ECONOMICAL": {
        BuildingAttributeType.ECONOMIC.value, 
        BuildingAttributeType.PRODUCTION.value
    },
    "EXPANSIVE": {
        BuildingAttributeType.EXPANSION.value, 
        BuildingAttributeType.RESIDENTIAL.value
    },
    "CULTURAL": {
        BuildingAttributeType.CULTURAL.value, 
        BuildingAttributeType.SPIRITUAL.value
    },
    "SPIRITUAL": {
        BuildingAttributeType.SPIRITUAL.value, 
        BuildingAttributeType.CULTURAL.value
    }
}

# Define suggested attribute schema for the _metadata field
BUILDING_METADATA_SCHEMA = {
    "attributes": [],                    # List of BuildingAttributeType values
    "category": "",                      # Primary category (e.g., "DEFENSIVE")
    "sub_categories": [],                # Additional categories
    "resource_production": {},           # Resources produced by this building
    "resource_consumption": {},          # Resources consumed by this building
    "population_capacity": 0,            # How many people can live/work here
    "required_tech": [],                 # Technologies required to build/use
    "building_tags": [],                 # Additional tags for filtering/categorization
    "trait_modifiers": {},               # How this building affects character traits
    "unlock_conditions": {},             # Conditions to unlock this building
    "upgrade_paths": []                  # IDs of possible upgrade blueprints
}

def get_attribute_values() -> List[str]:
    """Returns a list of all attribute values as strings."""
    return [attr.value for attr in BuildingAttributeType]

def get_attribute_from_string(attr_str: str) -> BuildingAttributeType:
    """
    Convert a string to a BuildingAttributeType enum.
    Returns None if not found.
    """
    try:
        return BuildingAttributeType(attr_str)
    except ValueError:
        return None

def get_attributes_for_trait(trait: str) -> Set[str]:
    """
    Get the set of building attributes preferred by a given trait.
    """
    return TRAIT_TO_ATTRIBUTE_MAP.get(trait, set())

def calculate_trait_affinity(
    building_attributes: List[str],
    character_trait: str
) -> float:
    """
    Calculate how well a building's attributes align with a character trait.
    Returns a score between 0.0 and 1.0, where higher is better alignment.
    
    Args:
        building_attributes: List of attribute strings from building metadata
        character_trait: Character trait to compare against
    
    Returns:
        Float score between 0.0 and 1.0
    """
    if not building_attributes or not character_trait:
        return 0.0
    
    # Get attributes preferred by this trait
    trait_attributes = get_attributes_for_trait(character_trait)
    if not trait_attributes:
        return 0.0
    
    # Calculate how many of the trait's preferred attributes match
    # the building's attributes
    building_attr_set = set(building_attributes)
    matching_attributes = building_attr_set.intersection(trait_attributes)
    
    # Score is the percentage of trait attributes that are present in building
    return len(matching_attributes) / len(trait_attributes)