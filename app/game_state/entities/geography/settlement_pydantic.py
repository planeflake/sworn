from pydantic import Field, ConfigDict
from uuid import UUID
from typing import Optional, List, Any, Dict

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class SettlementEntityPydantic(BaseEntityPydantic):
    """
    Represents a Settlement in the game (Domain Entity).
    Inherits entity_id and name as fields from BaseEntityPydantic.
    """
    # --- Fields with defaults ---
    world_id: Optional[UUID] = None
    leader_id: Optional[UUID] = None
    description: Optional[str] = None
    # Buildings are stored as a list of strings (IDs) - this matches the repository structure
    buildings: List[str] = Field(default_factory=list)
    building_instances: List[Any] = Field(default_factory=list) 
    # Resources mapped as Dict[resource_uuid_str, quantity]
    resources: Dict[str, int] = Field(default_factory=dict)
    population: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SettlementEntity to a dictionary with safe serialization."""
        # Get base entity fields
        data = super().to_dict()
        
        # Convert UUID keys to strings in resources dictionary
        string_resources = {str(k): v for k, v in self.resources.items()} if self.resources else {}
        
        # Add settlement-specific fields
        settlement_data = {
            "id": str(self.entity_id),
            "name": self.name,
            "world_id": str(self.world_id) if self.world_id else None,
            "leader_id": str(self.leader_id) if self.leader_id else None,
            "description": self.description,
            "buildings": self.buildings,
            "resources": string_resources,
            "population": self.population,
        }
        
        data.update(settlement_data)
        return data
    
    def add_resource(self, resource_id: UUID, quantity: int = 1) -> None:
        """
        Add a specific quantity of a resource to the settlement.
        
        Args:
            resource_id: UUID of the resource to add
            quantity: Amount to add (default: 1)
        """
        resource_id_str = str(resource_id)
        current_amount = self.resources.get(resource_id_str, 0)
        self.resources[resource_id_str] = current_amount + quantity
    
    def remove_resource(self, resource_id: UUID, quantity: int = 1) -> bool:
        """
        Remove a specific quantity of a resource from the settlement.
        
        Args:
            resource_id: UUID of the resource to remove
            quantity: Amount to remove (default: 1)
            
        Returns:
            True if resource was successfully removed, False if not enough resources
        """
        resource_id_str = str(resource_id)
        current_amount = self.resources.get(resource_id_str, 0)
        
        if current_amount < quantity:
            return False
            
        new_amount = current_amount - quantity
        if new_amount > 0:
            self.resources[resource_id_str] = new_amount
        else:
            # Remove the key entirely if quantity reaches zero
            del self.resources[resource_id_str]
            
        return True
    
    def get_resource_quantity(self, resource_id: UUID) -> int:
        """
        Get the quantity of a specific resource.
        
        Args:
            resource_id: UUID of the resource to check
            
        Returns:
            Quantity of the resource (0 if not present)
        """
        return self.resources.get(str(resource_id), 0)
    
    def has_resources(self, required_resources: Dict[UUID, int]) -> bool:
        """
        Check if the settlement has all the required resources.
        
        Args:
            required_resources: Dictionary mapping resource UUIDs to required quantities
            
        Returns:
            True if all required resources are available, False otherwise
        """
        for resource_id, required_quantity in required_resources.items():
            available = self.get_resource_quantity(resource_id)
            if available < required_quantity:
                return False
        return True
    
    def get_missing_resources(self, required_resources: Dict[UUID, int]) -> Dict[UUID, int]:
        """
        Calculate which resources are missing to meet requirements.
        
        Args:
            required_resources: Dictionary mapping resource UUIDs to required quantities
            
        Returns:
            Dictionary of missing resources and their quantities
        """
        missing = {}
        for resource_id, required_quantity in required_resources.items():
            available = self.get_resource_quantity(resource_id)
            if available < required_quantity:
                missing[resource_id] = required_quantity - available
        return missing
    
    def apply_resource_costs(self, costs: Dict[UUID, int]) -> bool:
        """
        Apply a set of resource costs to the settlement.
        
        Args:
            costs: Dictionary mapping resource UUIDs to costs
            
        Returns:
            True if costs were successfully applied, False if not enough resources
        """
        # First check if we have enough resources
        if not self.has_resources(costs):
            return False
            
        # Then remove all required resources
        for resource_id, cost in costs.items():
            self.remove_resource(resource_id, cost)
            
        return True
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Riverdale",
                "world_id": "550e8400-e29b-41d4-a716-446655440000",
                "leader_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "description": "A peaceful village by the river",
                "buildings": ["building1", "building2"],
                "resources": {
                    "550e8400-e29b-41d4-a716-446655440001": 100,
                    "550e8400-e29b-41d4-a716-446655440002": 50
                },
                "population": 150
            }
        }
    )

# For backward compatibility
Settlement = SettlementEntityPydantic