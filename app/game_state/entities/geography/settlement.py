# settlement.py
from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional, List, Any, Dict
from datetime import datetime
# Import the base entity
from app.game_state.entities.base import BaseEntity

@dataclass
class SettlementEntity(BaseEntity):
    """
    Represents a Settlement in the game (Domain Entity).
    Inherits entity_id and name as fields from BaseEntity.
    """
    # --- Fields with defaults ---
    world_id: UUID = None
    area_id: Optional[UUID] = None  # The area this settlement is located in
    leader_id: Optional[UUID] = None
    description: Optional[str] = None
    # Buildings are stored as a list of strings (IDs) - this matches the repository structure
    buildings: List[str] = field(default_factory=list)
    # We don't directly use the building_instances relationship from the SQLAlchemy model
    # to avoid lazy loading issues in async contexts
    building_instances: List[Any] = field(default_factory=list) 
    # Resources mapped as Dict[resource_uuid_str, quantity]
    resources: Dict[str, int] = field(default_factory=dict)
    population: int = 0
    # created_at and updated_at now come from BaseEntity

    def to_dict(self) -> Dict[str, Any]:
        """Convert SettlementEntity to a dictionary with safe serialization."""
        # Manually create dictionary instead of using asdict to avoid inheritance issues
        
        # Convert UUID keys to strings in resources dictionary
        string_resources = {str(k): v for k, v in self.resources.items()} if self.resources else {}
        
        data = {
            "id": str(self.entity_id),
            "name": self.name,
            "world_id": str(self.world_id) if self.world_id else None,
            "area_id": str(self.area_id) if self.area_id else None,
            "leader_id": str(self.leader_id) if self.leader_id else None,
            "description": self.description,
            "buildings": self.buildings,
            "resources": string_resources,
            "population": self.population,
        }
        
        # Include the base entity fields (including timestamps)
        base_data = super().to_dict()
        data.update(base_data)
        
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

# For backward compatibility
Settlement = SettlementEntity