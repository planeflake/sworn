# app/game_state/ai/base/game_context.py

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

class GameContext(BaseModel):
    """
    Provides context information for AI decision-making and action discovery.
    Contains the current state of the game world relevant to entity decisions.
    """
    
    # Basic Context
    current_time: datetime = Field(..., description="Current game time")
    location_id: Optional[UUID] = Field(None, description="Current location context")
    
    # Resource Context - Used by action validation
    resource_scarcity: Dict[str, float] = Field(
        default_factory=dict,
        description="Resource scarcity levels (resource_name -> scarcity_factor)"
    )
    
    # Threat Context - Used by action selection
    threat_level: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Overall threat level in the region"
    )
    
    # Economic Context - Used by action modifiers
    economic_conditions: Dict[str, float] = Field(
        default_factory=dict,
        description="Current economic indicators"
    )
    
    # Technology Context - Used by action validation
    available_technologies: List[str] = Field(
        default_factory=list,
        description="Technologies available to the current entity"
    )
    
    # Settlement Data - Used by action validation
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Settlement-specific data (population, resources, buildings)"
    )
    
    # Internal attributes
    _db: Optional[AsyncSession] = None
    
    def get_resource_scarcity(self, resource_name: str, default: float = 0.0) -> float:
        """Get the scarcity level of a resource."""
        return self.resource_scarcity.get(resource_name, default)
    
    def is_technology_available(self, technology_name: str) -> bool:
        """Check if a technology is available."""
        return technology_name in self.available_technologies
    
    @classmethod
    async def build_context(
        cls, 
        db: AsyncSession, 
        entity: Any,
        scope: str = "local"
    ) -> 'GameContext':
        """
        Build context for location entities.
        """
        from app.game_state.entities.geography.location_pydantic import LocationEntityPydantic
        
        # For now, only support locations
        if not isinstance(entity, LocationEntityPydantic):
            raise ValueError(f"Unsupported entity type: {type(entity).__name__}")
        
        # Create simple context
        context = cls(
            current_time=datetime.now(),
            location_id=entity.entity_id
        )
        context._db = db
        
        # Extract settlement data from location entity
        context.metadata["settlement_population"] = entity.get_attribute("population", 50)
        context.metadata["settlement_resources"] = entity.get_attribute("resources", {
            "wood": 100,
            "stone": 50,
            "food": 75
        })
        context.metadata["settlement_buildings"] = entity.get_attribute("buildings", [])
        context.metadata["nearby_resource_types"] = entity.get_attribute("nearby_resources", ["wood", "stone"])
        
        # Set basic technologies
        context.available_technologies = ["basic_construction", "agriculture"]
        
        # Set basic threat and economic levels
        context.threat_level = 0.1
        context.economic_conditions = {"prosperity": 0.5}
        context.resource_scarcity = {"wood": 0.1, "stone": 0.2}
        
        return context