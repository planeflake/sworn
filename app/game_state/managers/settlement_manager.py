# START OF FILE settlement_manager.py
"""
Settlement Manager - Contains domain logic for settlement operations
"""
from app.game_state.entities.settlement import Settlement
from app.game_state.managers.base_manager import BaseManager
from typing import Optional, Dict
from uuid import UUID

class SettlementManager:
    """Manager class for settlement-specific domain logic. Creates transient entities."""

    @staticmethod
    # Remove db: AsyncSession parameter
    def create(population: Optional[int],resources: Optional[Dict[str,int]], world_id: UUID, name: Optional[str] = None, description: Optional[str] = None) -> Settlement:
        """
        Create a new transient (in-memory) settlement entity.

        Args:
            world_id: The ID of the world this settlement belongs to.
            name: Optional name for the settlement.
            description: Optional description for the settlement.
            population: Optional initial population for the settlement.
            resources: Optional initial resources for the settlement.

        Returns:
            A new transient Settlement entity instance.
        """
        # BaseManager creates the basic entity with ID, name etc.
        settlement_entity = BaseManager.create(
            entity_class=Settlement, # Create the domain entity (dataclass)
            name=name,
            world_id=world_id,
            population=population,
            resources=resources
        )
        # Explicitly set description if provided
        if description is not None:
             settlement_entity.description = description

        # Return the transient entity
        return settlement_entity

# END OF FILE settlement_manager.py