# app/game_state/ai/simple_game_context.py

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession


class SimpleGameContext(BaseModel):
    """
    Simplified game context focused just on settlement decisions.
    Can be expanded later as we add more entity types.
    """
    
    # Basic context
    current_time: datetime = Field(default_factory=datetime.now)
    location_id: UUID = Field(..., description="ID of the location making decisions")
    
    # Settlement-specific data
    has_leader: bool = Field(False, description="Whether this location has a leader")
    leader_id: Optional[UUID] = Field(None, description="Leader's UUID if one exists")
    leader_traits: List[str] = Field(default_factory=list, description="Leader's decision-making traits")
    location_traits: List[str] = Field(default_factory=list, description="Location's inherent traits")
    
    # Settlement resources and population
    population: int = Field(0, description="Current population")
    resources: Dict[str, int] = Field(default_factory=dict, description="Available resources")
    buildings: List[str] = Field(default_factory=list, description="Existing buildings")
    
    # Available options
    available_technologies: List[str] = Field(
        default_factory=lambda: ["basic_construction"], 
        description="Technologies available for construction"
    )
    nearby_resource_types: List[str] = Field(
        default_factory=list, 
        description="Resource types available nearby"
    )
    
    # Simple modifiers
    threat_level: float = Field(0.0, ge=0.0, le=1.0, description="Local threat level")
    prosperity: float = Field(0.5, ge=0.0, le=1.0, description="Economic prosperity")
    
    model_config = {"arbitrary_types_allowed": True}
    
    @classmethod
    async def for_settlement(
        cls, 
        db: AsyncSession, 
        location_entity,
        scope: str = "local"
    ) -> 'SimpleGameContext':
        """
        Build simple context for a settlement location.
        
        Args:
            db: Database session (for future expansion)
            location_entity: LocationEntityPydantic with settlement data
            scope: Context scope (for future use)
            
        Returns:
            SimpleGameContext with settlement data
        """
        
        # Extract basic settlement info from location entity
        context = cls(
            location_id=location_entity.entity_id,
            has_leader=location_entity.has_leader,
            leader_id=location_entity.leader_id,
            leader_traits=location_entity.leader_traits,
            location_traits=location_entity.entity_traits
        )
        
        # Extract settlement data from location attributes
        context.population = location_entity.get_attribute("population", 50)
        context.resources = location_entity.get_attribute("resources", {
            "wood": 100,
            "stone": 50,
            "food": 75
        })
        context.buildings = location_entity.get_attribute("buildings", [])
        
        # Set available technologies based on location
        technologies = ["basic_construction"]
        if location_entity.get_attribute("has_agriculture", True):
            technologies.append("agriculture")
        if location_entity.get_attribute("has_metalworking", False):
            technologies.append("metalworking")
        context.available_technologies = technologies
        
        # Try to get nearby resources (optional)
        try:
            resource_nodes = await cls._get_nearby_resources(db, location_entity.entity_id)
            context.nearby_resource_types = resource_nodes
        except Exception:
            # Default resources for testing
            context.nearby_resource_types = ["wood", "stone"]
        
        # Simple threat and prosperity (can be expanded later)
        context.threat_level = location_entity.get_attribute("threat_level", 0.1)
        context.prosperity = location_entity.get_attribute("prosperity", 0.5)
        
        return context
    
    @staticmethod
    async def _get_nearby_resources(db: AsyncSession, location_id: UUID) -> List[str]:
        """Get list of nearby resource types (simplified)."""
        try:
            # Try to use resource node service if available
            from app.game_state.services.resource.resource_node_service import ResourceNodeService
            resource_service = ResourceNodeService(db)
            nodes = await resource_service.get_nodes_by_location(location_id)
            
            # Extract resource type names
            resource_types = []
            for node in nodes:
                if hasattr(node, 'resource_links'):
                    for link in node.resource_links:
                        if hasattr(link, 'resource_name'):
                            resource_types.append(link.resource_name)
            
            return list(set(resource_types))
        except:
            # Fallback to default resources
            return ["wood", "stone"]
    
    @property
    def all_traits(self) -> List[str]:
        """Combined location and leader traits."""
        return self.location_traits + self.leader_traits
    
    def has_trait(self, trait: str) -> bool:
        """Check if location or leader has a trait."""
        return trait in self.all_traits
    
    def has_resource(self, resource: str, amount: int = 1) -> bool:
        """Check if settlement has enough of a resource."""
        return self.resources.get(resource, 0) >= amount
    
    def has_technology(self, tech: str) -> bool:
        """Check if a technology is available."""
        return tech in self.available_technologies
    
    def has_building(self, building_type: str) -> bool:
        """Check if settlement already has a building type."""
        return building_type in self.buildings