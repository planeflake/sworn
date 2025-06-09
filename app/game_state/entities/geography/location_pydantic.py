"""
Location Pydantic entity representing a location in the game world.
"""

from pydantic import Field, ConfigDict
from uuid import UUID
from typing import Optional, Dict, Any, List

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic
from app.game_state.entities.geography.location.location_reference import LocationReference
from app.game_state.entities.geography.location_type_pydantic import LocationTypeEntityPydantic
from app.game_state.ai.base.action_interface import ActionCapable, PossibleAction
from app.game_state.ai.base.game_context import GameContext

class LocationEntityPydantic(BaseEntityPydantic, ActionCapable):
    """
    Pydantic entity representing a location in the game world.
    Each location has a type that defines its properties and behavior.
    """
    
    # Location type
    location_type_id: UUID = Field(..., description="UUID of the location type")
    location_type: Optional[LocationTypeEntityPydantic] = Field(None, description="Full type entity when populated")
    
    # Foreign key references
    world_id: Optional[UUID] = Field(None, description="UUID of the world this location belongs to")
    theme_id: Optional[UUID] = Field(None, description="UUID of the theme for this location")
    biome_id: Optional[UUID] = Field(None, description="UUID of the biome for this location")
    
    # Parent reference
    parent: Optional[LocationReference] = Field(None, description="Reference to parent location")
    parent_id: Optional[UUID] = Field(None, description="UUID of the parent location")
    
    # Leader and Traits
    leader_id: Optional[UUID] = Field(None, description="UUID of the character leading this location")
    entity_traits: List[str] = Field(default_factory=list, description="Traits inherent to this location")
    leader_traits: List[str] = Field(default_factory=list, description="Traits of the leader making decisions")
    
    # Common attributes
    description: Optional[str] = Field(None, description="Description of this location")
    coordinates: Dict[str, float] = Field(default_factory=dict, description="Coordinate system for this location")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Custom attributes specific to this location")
    is_active: bool = Field(True, description="Whether this location is currently active")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entity_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Sol System",
                "location_type_id": "456e7890-e89b-12d3-a456-426614174001",
                "parent": {
                    "location_id": "789abcde-e89b-12d3-a456-426614174002",
                    "location_type_id": "012fghij-e89b-12d3-a456-426614174003",
                    "location_type_code": "galaxy"
                },
                "description": "The solar system containing Earth and other planets",
                "coordinates": {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                },
                "attributes": {
                    "star_type": "G-type main-sequence",
                    "hazard_level": 2,
                    "inhabited": True
                },
                "is_active": True
            }
        }
    )
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Safely get an attribute value."""
        return self.attributes.get(key, default)
    
    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute value."""
        self.attributes[key] = value
        
    def has_attribute(self, key: str) -> bool:
        """Check if an attribute exists."""
        return key in self.attributes
    
    def get_coordinate(self, axis: str, default: float = 0.0) -> float:
        """Get a coordinate value for a specific axis."""
        return self.coordinates.get(axis, default)
    
    def set_coordinate(self, axis: str, value: float) -> None:
        """Set a coordinate value for a specific axis."""
        self.coordinates[axis] = value
    
    def get_parent_id(self) -> Optional[UUID]:
        """Get the parent location ID if it exists."""
        return self.parent.location_id if self.parent else None
    
    def get_parent_type_id(self) -> Optional[UUID]:
        """Get the parent location type ID if it exists."""
        return self.parent.location_type_id if self.parent else None
    
    def is_child_of(self, parent_id: UUID) -> bool:
        """Check if this location is a child of the specified parent."""
        return self.parent is not None and self.parent.location_id == parent_id

    def get_world_id(self) -> Optional[UUID]:
        """Get the world ID if this location is in a world."""
        return self.world_id if self.world_id else None

    def get_theme_id(self) -> Optional[UUID]:
        """Get the theme ID if this location is in a theme."""
        return self.theme_id if self.theme_id else None

    def get_biome_id(self) -> Optional[UUID]:
        """Get the biome ID if this location is in a biome."""
        return self.biome_id if self.biome_id else None

    # Trait-related properties
    @property
    def all_traits(self) -> List[str]:
        """Combined entity and leader traits for decision-making."""
        return self.entity_traits + self.leader_traits
    
    def has_trait(self, trait: str) -> bool:
        """Check if this location or its leader has a specific trait."""
        return trait in self.all_traits
    
    @property  
    def has_leader(self) -> bool:
        """Check if this location has a leader assigned."""
        return self.leader_id is not None
    
    # ActionCapable implementation
    async def get_possible_actions(self, context: GameContext) -> List[PossibleAction]:
        """
        Get all possible actions this location can perform.
        This includes construction, resource management, diplomacy, etc.
        """
        actions = []
        
        try:
            # Import here to avoid circular imports
            from app.game_state.actions.settlement.building_actions import ConstructBuildingAction
            
            # Get all construction actions available to this location
            construction_actions = await ConstructBuildingAction.get_all_available_constructions(
                settlement_id=self.entity_id,  # Using entity_id as settlement_id for now
                context=context
            )
            actions.extend(construction_actions)
            
            # TODO: Add other action types here as they're implemented:
            # - Resource management actions
            # - Trade actions  
            # - Diplomatic actions
            # - Military actions
            
        except ImportError:
            # Action classes not available yet - return empty list
            pass
        except Exception as e:
            # Log error but don't crash
            print(f"Error getting actions for location {self.entity_id}: {e}")
        
        return actions