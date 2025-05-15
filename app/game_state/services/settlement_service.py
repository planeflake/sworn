# START OF FILE app/game_state/services/settlement_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
import logging
import json

# Import domain entity and repository
from app.game_state.entities.settlement import SettlementEntity
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

    @staticmethod
    async def _convert_entity_to_read_schema(entity: Optional[SettlementEntity]) -> Optional[SettlementRead]:
        """Convert a domain entity to an API read schema."""
        if entity is None:
            return None
            
        try:
            # Use the entity's to_dict method to get a dictionary representation
            entity_dict = entity.to_dict()
            # Validate with SettlementRead model
            return SettlementRead.model_validate(entity_dict)
        except Exception as e:
            logging.error(f"Failed to convert Settlement entity to Read schema: {e}", exc_info=True)
            raise ValueError("Internal error converting settlement data.")

    async def create(self, name: str, description: Optional[str], world_id: UUID) -> SettlementRead:
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
            world_id=world_id
        )

        # 2. Call the repository to save the entity
        try:
            persistent_settlement = await self.repository.save(transient_settlement)
            if persistent_settlement is None:
                raise ValueError("Failed to save settlement entity.")
                
            # 3. Convert the domain entity to API schema
            settlement_api_schema = await self._convert_entity_to_read_schema(persistent_settlement)
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
                return await self._convert_entity_to_read_schema(settlement_entity)
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
                return await self._convert_entity_to_read_schema(settlement_entity)
            return None
        except Exception as e:
            logging.error(f"[SettlementService] Error setting leader for settlement with ID {settlement_id}: {e}", exc_info=True)
            raise

    async def construct_building(self, settlement_id: UUID, building_id: str) -> Optional[SettlementRead]:
        """Constructs a building in a settlement by its ID."""
        logging.info(f"[SettlementService] Constructing building {building_id} in settlement {settlement_id}")
        try:
            settlement_entity = await self.repository.construct_building(settlement_id=settlement_id, building_id=building_id)
            if settlement_entity:
                return await self._convert_entity_to_read_schema(settlement_entity)
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
                return await self._convert_entity_to_read_schema(settlement_entity)
            return None
        except Exception as e:
            logging.error(f"[SettlementService] Error demolishing building in settlement with ID {settlement_id}: {e}", exc_info=True)
            raise
        
    async def add_resource(self, settlement_id: UUID, resource_id: str) -> Optional[SettlementRead]:
        """Adds a resource to a settlement by its ID."""
        logging.info(f"[SettlementService] Adding resource {resource_id} to settlement {settlement_id}")
        try:
            settlement_entity = await self.repository.add_resource(settlement_id=settlement_id, resource_id=resource_id)
            if settlement_entity:
                return await self._convert_entity_to_read_schema(settlement_entity)
            return None
        except Exception as e:
            logging.error(f"[SettlementService] Error adding resource to settlement with ID {settlement_id}: {e}", exc_info=True)
            raise

    async def expand_settlement(self, settlement_id: UUID) -> Optional[SettlementRead]:
        """Expands a settlement by its ID."""
        logging.info(f"[SettlementService] Expanding settlement {settlement_id}")
        # Implement expansion logic here
        # This would involve calculating resource growth, building new structures, etc.
        # Placeholder implementation
        return None

    async def get_settlements_by_world(self, world_id: UUID) -> List[SettlementEntity]:
        """Gets a list of settlements in a world."""
        logging.debug(f"[SettlementService] Getting settlements for world {world_id}")
        try:
            return await self.repository.find_by_world(world_id)
        except Exception as e:
            logging.error(f"[SettlementService] Error getting settlements for world {world_id}: {e}", exc_info=True)
            return []
            
    async def get_all_settlements(self) -> List[SettlementEntity]:
        """Gets a list of all settlements."""
        logging.debug("[SettlementService] Getting all settlements")
        try:
            return await self.repository.find_all()
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
            read_schema_items = []
            for entity in paginated_repo_result["items"]:
                schema = await self._convert_entity_to_read_schema(entity)
                if schema:
                    read_schema_items.append(schema)
            
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