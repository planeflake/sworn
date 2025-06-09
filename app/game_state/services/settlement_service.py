# START OF FILE app/game_state/services/settlement_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict
from uuid import UUID
import logging

# Import domain entity and repository
from app.game_state.repositories.settlement_repository import SettlementRepository
from app.game_state.managers.settlement_manager import SettlementManager

# Import API schemas
from app.api.schemas.settlement import SettlementRead
from app.api.schemas.shared import PaginatedResponse

class SettlementService:
    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session."""
        self.db = db
        self.repository = SettlementRepository(db=self.db)
        logging.debug("SettlementService initialized with SettlementRepository.")

    async def create(self, name: str, description: Optional[str], world_id: UUID, population: Optional[int],resources: Optional[dict]) -> SettlementRead:
        """Creates a settlement and returns an API schema."""
        logging.info(f"[SettlementService] Creating settlement with name: '{name}' in world: {world_id}")
        
        # Basic validation
        if not name:
            logging.error("[SettlementService] Settlement name cannot be empty.")
            raise ValueError("Settlement name cannot be empty.")
            
        # 1. Call the manager to create the transient domain entity
        transient_settlement = SettlementManager.create(
            name=name,
            description=description,
            world_id=world_id,
            population=population,
            resources=resources
        )

        # 2. Call the repository to save the entity
        try:
            persistent_settlement = await self.repository.save(transient_settlement)
            if persistent_settlement is None:
                raise ValueError("Failed to save settlement entity.")
                
            # 3. Convert the domain entity to API schema
            settlement_api_schema = SettlementRead.model_validate(persistent_settlement.to_dict())
            logging.info(f"[SettlementService] Settlement '{name}' created successfully with ID: {settlement_api_schema.id}")
            return settlement_api_schema
            
        except Exception as e:
            logging.exception(f"[SettlementService] Error creating settlement '{name}': {e}")
            raise ValueError(f"Failed to create settlement: {str(e)}") from e

    async def delete(self, settlement_id: UUID) -> bool:
        """Deletes a settlement by its ID."""
        logging.info(f"[SettlementService] Deleting settlement with ID: {settlement_id}")
        try:
            result = await self.repository.delete(settlement_id)
            if result:
                logging.info(f"[SettlementService] Settlement {settlement_id} deleted successfully")
            else:
                logging.warning(f"[SettlementService] Settlement {settlement_id} not found for deletion")
            return result
        except Exception as e:
            logging.error(f"[SettlementService] Error deleting settlement with ID {settlement_id}: {e}", exc_info=True)
            return False

    async def rename(self, settlement_id: UUID, new_name: str) -> Optional[SettlementRead]:
        """Renames a settlement by its ID."""
        logging.info(f"[SettlementService] Renaming settlement {settlement_id} to '{new_name}'")
        try:
            settlement_entity = await self.repository.rename(settlement_id=settlement_id, new_name=new_name)
            if settlement_entity:
                return SettlementRead.model_validate(settlement_entity.to_dict())
            return None
        except Exception as e:
            logging.error(f"[SettlementService] Error renaming settlement with ID {settlement_id}: {e}", exc_info=True)
            raise

    async def set_leader(self, settlement_id: UUID, leader_id: UUID) -> Optional[SettlementRead]:
        """Sets the leader of a settlement by its ID."""
        logging.info(f"[SettlementService] Setting leader {leader_id} for settlement {settlement_id}")
        try:
            settlement_entity = await self.repository.set_leader(settlement_id=settlement_id, leader_id=leader_id)
            if settlement_entity:
                return SettlementRead.model_validate(settlement_entity.to_dict())
            return None
        except Exception as e:
            logging.error(f"[SettlementService] Error setting leader for settlement with ID {settlement_id}: {e}", exc_info=True)
            raise

    async def construct_building(self, settlement_id: UUID, building_id: str, building_costs: Optional[Dict[UUID, int]] = None) -> Optional[SettlementRead]:
        """
        Constructs a building in a settlement after checking and deducting required resources.
        
        Args:
            settlement_id: UUID of the settlement
            building_id: ID of the building to construct
            building_costs: Optional dictionary mapping resource UUIDs to costs
            
        Returns:
            Updated settlement API schema if successful, None if settlement not found or not enough resources
        """
        logging.info(f"[SettlementService] Constructing building {building_id} in settlement {settlement_id}")
        try:
            # Check if building has costs and if the settlement can afford them
            if building_costs:
                # Check if settlement can afford the building
                can_afford = await self.can_afford_building(settlement_id, building_costs)
                if not can_afford:
                    logging.warning(f"[SettlementService] Settlement {settlement_id} cannot afford building {building_id}")
                    return None
                    
                # Apply resource costs
                resource_update = await self.apply_resource_costs(settlement_id, building_costs)
                if not resource_update:
                    logging.warning(f"[SettlementService] Failed to apply resource costs for building {building_id} in settlement {settlement_id}")
                    return None
            
            # Construct the building
            settlement_entity = await self.repository.construct_building(settlement_id=settlement_id, building_id=building_id)
            if settlement_entity:
                return SettlementRead.model_validate(settlement_entity.to_dict())
            return None
        except Exception as e:
            logging.error(f"[SettlementService] Error constructing building in settlement with ID {settlement_id}: {e}", exc_info=True)
            raise

    async def demolish_building(self, settlement_id: UUID, building_id: str) -> Optional[SettlementRead]:
        """Demolishes a building in a settlement by its ID."""
        logging.info(f"[SettlementService] Demolishing building {building_id} in settlement {settlement_id}")
        try:
            settlement_entity = await self.repository.demolish_building(settlement_id=settlement_id, building_id=building_id)
            if settlement_entity:
                return SettlementRead.model_validate(settlement_entity.to_dict())
            return None
        except Exception as e:
            logging.error(f"[SettlementService] Error demolishing building in settlement with ID {settlement_id}: {e}", exc_info=True)
            raise
        
    async def add_resource(self, settlement_id: UUID, resource_id: UUID, quantity: int = 1) -> Optional[SettlementRead]:
        """
        Adds a specific quantity of a resource to a settlement.
        
        Args:
            settlement_id: UUID of the settlement to modify
            resource_id: UUID of the resource to add
            quantity: Amount of the resource to add (default: 1)
            
        Returns:
            Updated settlement API schema if successful, None if settlement not found
        """
        logging.info(f"[SettlementService] Adding {quantity} of resource {resource_id} to settlement {settlement_id}")
        try:
            settlement_entity = await self.repository.add_resource(
                settlement_id=settlement_id, 
                resource_id=resource_id,
                quantity=quantity
            )
            if settlement_entity:
                return SettlementRead.model_validate(settlement_entity.to_dict())
            return None
        except Exception as e:
            logging.error(f"[SettlementService] Error adding resource to settlement with ID {settlement_id}: {e}", exc_info=True)
            raise
            
    async def remove_resource(self, settlement_id: UUID, resource_id: UUID, quantity: int = 1) -> Optional[SettlementRead]:
        """
        Removes a specific quantity of a resource from a settlement.
        
        Args:
            settlement_id: UUID of the settlement to modify
            resource_id: UUID of the resource to remove
            quantity: Amount of the resource to remove (default: 1)
            
        Returns:
            Updated settlement API schema if successful, None if settlement not found or not enough resources
        """
        logging.info(f"[SettlementService] Removing {quantity} of resource {resource_id} from settlement {settlement_id}")
        try:
            settlement_entity = await self.repository.remove_resource(
                settlement_id=settlement_id,
                resource_id=resource_id,
                quantity=quantity
            )
            if settlement_entity:
                return SettlementRead.model_validate(settlement_entity.to_dict())
            return None
        except Exception as e:
            logging.error(f"[SettlementService] Error removing resource from settlement with ID {settlement_id}: {e}", exc_info=True)
            raise
            
    async def get_resource_quantity(self, settlement_id: UUID, resource_id: UUID) -> Optional[int]:
        """
        Gets the quantity of a specific resource in a settlement.
        
        Args:
            settlement_id: UUID of the settlement
            resource_id: UUID of the resource to check
            
        Returns:
            Quantity of the resource if found, None if settlement not found
        """
        logging.info(f"[SettlementService] Getting quantity of resource {resource_id} in settlement {settlement_id}")
        try:
            return await self.repository.get_resource_quantity(settlement_id, resource_id)
        except Exception as e:
            logging.error(f"[SettlementService] Error getting resource quantity in settlement with ID {settlement_id}: {e}", exc_info=True)
            raise
            
    async def get_available_resources(self, settlement_id: UUID) -> Optional[Dict[UUID, int]]:
        """
        Gets all resources available in a settlement with their quantities.
        
        Args:
            settlement_id: UUID of the settlement
            
        Returns:
            Dictionary mapping resource UUIDs to quantities if found, None if settlement not found
        """
        logging.info(f"[SettlementService] Getting all available resources in settlement {settlement_id}")
        try:
            # Get the settlement entity
            settlement_entity = await self.repository.find_by_id(settlement_id)
            if not settlement_entity:
                logging.warning(f"[SettlementService] Settlement {settlement_id} not found when getting available resources")
                return None
                
            # Convert string keys in the entity's resources dict to UUIDs
            result = {}
            for resource_id_key, quantity in settlement_entity.resources.items():
                # Use f-string for logging to avoid concatenation issues with different types
                logging.debug(f">>> Resource ID: {resource_id_key} (type: {type(resource_id_key)}) Quantity: {quantity} <<<")
                
                # Convert the key to string first if it's a UUID
                if isinstance(resource_id_key, UUID):
                    resource_id_str = str(resource_id_key)
                else:
                    resource_id_str = resource_id_key
                    
                # Skip 'None' keys
                if resource_id_str == 'None' or not resource_id_str:
                    logging.warning(f"Skipping invalid resource key: {resource_id_str}")
                    continue
                    
                try:
                    # Convert to UUID and add to result
                    result[UUID(resource_id_str)] = quantity
                except (ValueError, TypeError) as e:
                    logging.warning(f"Invalid UUID key '{resource_id_str}': {e}")
                    continue
                
            return result
        except Exception as e:
            logging.error(f"[SettlementService] Error getting available resources in settlement with ID {settlement_id}: {e}", exc_info=True)
            raise
            
    async def has_resources(self, settlement_id: UUID, required_resources: Dict[UUID, int]) -> bool:
        """
        Checks if a settlement has all the required resources.
        
        Args:
            settlement_id: UUID of the settlement
            required_resources: Dictionary mapping resource UUIDs to required quantities
            
        Returns:
            True if all required resources are available, False otherwise
        """
        logging.info(f"[SettlementService] Checking if settlement {settlement_id} has required resources")
        try:
            return await self.repository.has_resources(settlement_id, required_resources)
        except Exception as e:
            logging.error(f"[SettlementService] Error checking resources in settlement with ID {settlement_id}: {e}", exc_info=True)
            return False
            
    async def apply_resource_costs(self, settlement_id: UUID, costs: Dict[UUID, int]) -> Optional[SettlementRead]:
        """
        Applies a set of resource costs to a settlement. This is an atomic operation -
        either all costs are applied or none are.
        
        Args:
            settlement_id: UUID of the settlement
            costs: Dictionary mapping resource UUIDs to costs
            
        Returns:
            Updated settlement API schema if successful, None if settlement not found or not enough resources
        """
        logging.info(f"[SettlementService] Applying resource costs to settlement {settlement_id}")
        try:
            settlement_entity = await self.repository.apply_resource_costs(settlement_id, costs)
            if settlement_entity:
                return SettlementRead.model_validate(settlement_entity.to_dict())
            return None
        except Exception as e:
            logging.error(f"[SettlementService] Error applying resource costs to settlement with ID {settlement_id}: {e}", exc_info=True)
            raise
            
    async def can_afford_building(self, settlement_id: UUID, building_costs: Dict[UUID, int]) -> bool:
        """
        Checks if a settlement can afford to build a structure with the given resource costs.
        
        Args:
            settlement_id: UUID of the settlement
            building_costs: Dictionary mapping resource UUIDs to costs
            
        Returns:
            True if the settlement can afford the building, False otherwise
        """
        logging.info(f"[SettlementService] Checking if settlement {settlement_id} can afford building")
        try:
            return await self.repository.has_resources(settlement_id, building_costs)
        except Exception as e:
            logging.error(f"[SettlementService] Error checking if settlement can afford building: {e}", exc_info=True)
            return False

    @staticmethod
    async def expand_settlement(settlement_id: UUID) -> Optional[SettlementRead]:
        """Expands a settlement by its ID."""
        logging.info(f"[SettlementService] Expanding settlement {settlement_id}")
        # Implement expansion logic here
        # This would involve calculating resource growth, building new structures, etc.
        # Placeholder implementation
        return None

    async def get_settlements_by_world(self, world_id: UUID) -> List[SettlementRead]:
        """Gets a list of settlements in a world."""
        logging.debug(f"[SettlementService] Getting settlements for world {world_id}")
        try:

            settlements = await self.repository.find_by_world(world_id)

            return [SettlementRead.model_validate(settlement.to_dict()) for settlement in settlements]
        except Exception as e:
            logging.error(f"[SettlementService] Error getting settlements for world {world_id}: {e}", exc_info=True)
            return []
            
    async def get_all_settlements(self) -> List[SettlementRead]:
        """Gets a list of all settlements."""
        logging.debug("[SettlementService] Getting all settlements")
        try:
            settlements = await self.repository.find_all()
            return [SettlementRead.model_validate(settlement.to_dict()) for settlement in settlements]
        except Exception as e:
            logging.error(f"[SettlementService] Error getting all settlements: {e}", exc_info=True)
            return []
            
    async def get_all_settlements_paginated(self, skip: int, limit: int) -> PaginatedResponse[SettlementRead]:
        """Gets a paginated list of settlements."""
        logging.debug(f"[SettlementService] Getting paginated settlements (skip={skip}, limit={limit})")
        try:
            paginated_repo_result = await self.repository.find_all_paginated(
                skip=skip,
                limit=limit
            )
            
            # Convert domain entities in "items" to read schemas
            #read_schema_items = []
            #for entity in paginated_repo_result["items"]:
            #    schema = await self._convert_entity_to_read_schema(entity)
            #    if schema:
            #        read_schema_items.append(schema)

            read_schema_items = [SettlementRead.model_validate(entity.to_dict()) for entity in paginated_repo_result["items"]]

            
            # Construct and return the PaginatedResponse Pydantic model
            return PaginatedResponse[SettlementRead](
                items=read_schema_items,
                total=paginated_repo_result["total"],
                limit=paginated_repo_result["limit"],
                skip=paginated_repo_result["skip"],
            )
        except Exception as e:
            logging.error(f"[SettlementService] Error getting paginated settlements: {e}", exc_info=True)
            raise

# END OF FILE app/game_state/services/settlement_service.py