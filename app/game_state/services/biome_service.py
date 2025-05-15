# --- START OF FILE app/game_state/services/biome_service.py ---
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, List, Dict, Any
import logging
import dataclasses

# Import Repository, Manager and Domain Entity
from app.game_state.repositories.biome_repository import BiomeRepository
from app.game_state.managers.biome_manager import BiomeManager
from app.game_state.entities.biome import BiomeEntity

# Import API schemas
from app.api.schemas.shared import PaginatedResponse
from app.api.schemas.biome_schema import BiomeRead, BiomeCreate, BiomeUpdate

class BiomeService:
    """
    Service for managing biomes.
    Handles the connection between API routes, domain logic, and data access.
    """
    
    def __init__(self, db: AsyncSession):
        """Initializes the BiomeService with a database session."""
        self.db = db
        self.repository = BiomeRepository(db=self.db)
        self.manager = BiomeManager()
        logging.debug("BiomeService initialized with BiomeRepository and BiomeManager.")
    
    async def _convert_entity_to_read_schema(self, entity: Optional[BiomeEntity]) -> Optional[BiomeRead]:
        """Convert a domain entity to an API read schema."""
        if entity is None:
            return None
            
        try:
            # Use the entity's to_dict method to get a dictionary representation
            entity_dict = entity.to_dict()
            # Validate with BiomeRead model
            return BiomeRead.model_validate(entity_dict)
        except Exception as e:
            logging.error(f"Failed to convert BiomeEntity to Read schema: {e}", exc_info=True)
            raise ValueError("Internal error converting biome data.")
    
    async def get_all_biomes_paginated(self, skip: int, limit: int) -> PaginatedResponse[BiomeRead]:
        """
        Retrieves a paginated list of biomes.
        
        Args:
            skip: Number of items to skip (for pagination)
            limit: Maximum number of items to return
            
        Returns:
            A paginated response with BiomeRead schemas
        """
        # Call the repository's paginated find method
        paginated_repo_result = await self.repository.find_all_paginated(
            skip=skip,
            limit=limit,
            order_by=[self.repository.model_cls.name.asc()]
        )
        
        # Convert domain entities in "items" to read schemas
        read_schema_items = []
        for entity in paginated_repo_result["items"]:
            schema = await self._convert_entity_to_read_schema(entity)
            if schema:
                read_schema_items.append(schema)
        
        # Construct and return the PaginatedResponse Pydantic model
        return PaginatedResponse[BiomeRead](
            items=read_schema_items,
            total=paginated_repo_result["total"],
            limit=paginated_repo_result["limit"],
            skip=paginated_repo_result["skip"],
        )
    
    async def get_biome_by_id(self, biome_uuid: UUID) -> Optional[BiomeRead]:
        """
        Get a biome by UUID and return as API schema.
        
        Args:
            biome_uuid: The UUID of the biome to retrieve
            
        Returns:
            BiomeRead schema or None if not found
        """
        logging.debug(f"[BiomeService] Getting biome by UUID: {biome_uuid}")
        try:
            entity = await self.repository.find_by_id(biome_uuid)
            if entity:
                return await self._convert_entity_to_read_schema(entity)
            else:
                return None
        except Exception as e:
            logging.error(f"[BiomeService] Error getting biome by UUID {biome_uuid}: {e}")
            return None
    
    async def get_biome_by_string_id(self, biome_id: str) -> Optional[BiomeRead]:
        """
        Get a biome by its string identifier and return as API schema.
        
        Args:
            biome_id: String identifier (e.g., "forest")
            
        Returns:
            BiomeRead schema or None if not found
        """
        logging.debug(f"[BiomeService] Getting biome by string ID: {biome_id}")
        try:
            entity = await self.repository.find_by_biome_id(biome_id)
            if entity:
                return await self._convert_entity_to_read_schema(entity)
            else:
                return None
        except Exception as e:
            logging.error(f"[BiomeService] Error getting biome by string ID {biome_id}: {e}")
            return None
    
    async def exists(self, biome_uuid: UUID) -> bool:
        """
        Check if a biome exists by UUID.
        
        Args:
            biome_uuid: The UUID to check
            
        Returns:
            True if the biome exists, False otherwise
        """
        logging.debug(f"[BiomeService] Checking existence for biome UUID: {biome_uuid}")
        try:
            return await self.repository.exists(biome_uuid)
        except Exception as e:
            logging.error(f"[BiomeService] Error checking existence for biome {biome_uuid}: {e}", exc_info=True)
            return False
    
    async def get_biome_entity(self, biome_uuid: UUID) -> Optional[BiomeEntity]:
        """
        Get a biome domain entity by UUID.
        
        Args:
            biome_uuid: The UUID of the biome to retrieve
            
        Returns:
            BiomeEntity instance or None if not found
        """
        logging.debug(f"[BiomeService] Getting biome entity by UUID: {biome_uuid}")
        try:
            return await self.repository.find_by_id(biome_uuid)
        except Exception as e:
            logging.error(f"[BiomeService] Error getting biome entity by UUID {biome_uuid}: {e}", exc_info=True)
            return None
    
    async def create_biome(self, biome_data: BiomeCreate) -> Optional[BiomeRead]:
        """
        Creates a new biome from API data.
        
        Args:
            biome_data: BiomeCreate schema with the biome data
            
        Returns:
            BiomeRead schema for the created biome or raises an error
        """
        logging.info(f"[BiomeService] Creating biome with string ID: '{biome_data.biome_id}'")
        
        # Check if biome_id already exists
        existing_biome = await self.repository.find_by_biome_id(biome_data.biome_id)
        if existing_biome:
            logging.warning(f"[BiomeService] Biome with ID '{biome_data.biome_id}' already exists (UUID: {existing_biome.entity_id}).")
            raise ValueError(f"Biome with ID '{biome_data.biome_id}' already exists.")
        
        # Create transient entity using manager
        try:
            # Convert Pydantic model to dict for unpacking
            create_data_dict = biome_data.model_dump(exclude={"id"})
            
            # Use manager to create entity
            entity_id = biome_data.id if hasattr(biome_data, "id") and biome_data.id else None
            biome_entity = self.manager.create_transient_biome(
                entity_id=entity_id,
                **create_data_dict
            )
            
            logging.debug(f"[BiomeService] Created transient biome entity: {biome_entity}")
        except Exception as e:
            logging.error(f"[BiomeService] Error creating transient biome entity: {e}", exc_info=True)
            raise ValueError(f"Could not create biome: {e}")
        
        # Save using repository
        try:
            saved_entity = await self.repository.save(biome_entity)
            logging.info(f"[BiomeService] Biome '{saved_entity.name}' created successfully with UUID: {saved_entity.entity_id}")
            
            # Convert to API schema
            return await self._convert_entity_to_read_schema(saved_entity)
        except Exception as e:
            logging.exception(f"[BiomeService] Error saving new biome '{biome_data.name}': {e}")
            raise
    
    async def update_biome(self, biome_uuid: UUID, update_data: BiomeUpdate) -> Optional[BiomeRead]:
        """
        Updates an existing biome.
        
        Args:
            biome_uuid: UUID of the biome to update
            update_data: BiomeUpdate schema with fields to update
            
        Returns:
            Updated BiomeRead schema or None if biome not found
        """
        logging.info(f"[BiomeService] Updating biome with UUID: {biome_uuid}")
        
        # Get existing biome
        existing_biome = await self.repository.find_by_id(biome_uuid)
        if not existing_biome:
            logging.warning(f"[BiomeService] Biome with UUID {biome_uuid} not found for update.")
            return None
        
        # Get non-None update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            logging.info(f"[BiomeService] No fields to update for biome {biome_uuid}")
            return await self._convert_entity_to_read_schema(existing_biome)
        
        # Apply updates to entity
        for field, value in update_dict.items():
            if hasattr(existing_biome, field):
                setattr(existing_biome, field, value)
        
        # Save updated entity
        try:
            updated_entity = await self.repository.save(existing_biome)
            logging.info(f"[BiomeService] Biome {biome_uuid} updated successfully")
            return await self._convert_entity_to_read_schema(updated_entity)
        except Exception as e:
            logging.error(f"[BiomeService] Error updating biome {biome_uuid}: {e}", exc_info=True)
            raise
    
    async def delete_biome(self, biome_uuid: UUID) -> bool:
        """
        Deletes a biome by UUID.
        
        Args:
            biome_uuid: UUID of the biome to delete
            
        Returns:
            True if the biome was deleted, False otherwise
        """
        logging.info(f"[BiomeService] Deleting biome with UUID: {biome_uuid}")
        
        # Check if biome exists
        if not await self.repository.exists(biome_uuid):
            logging.warning(f"[BiomeService] Biome with UUID {biome_uuid} not found for deletion.")
            return False
        
        # Delete using repository
        try:
            result = await self.repository.delete(biome_uuid)
            if result:
                logging.info(f"[BiomeService] Biome {biome_uuid} deleted successfully")
            else:
                logging.warning(f"[BiomeService] Failed to delete biome {biome_uuid}")
            return result
        except Exception as e:
            logging.error(f"[BiomeService] Error deleting biome {biome_uuid}: {e}", exc_info=True)
            return False
    
    async def get_biomes_by_danger_level(self, danger_level: int) -> List[BiomeRead]:
        """
        Gets all biomes with a specific danger level.
        
        Args:
            danger_level: The danger level to filter by (1-5)
            
        Returns:
            List of biomes matching the danger level
        """
        logging.debug(f"[BiomeService] Getting biomes with danger level: {danger_level}")
        try:
            # Use repository to find biomes
            entities = await self.repository.find_by_danger_level(danger_level)
            
            # Convert to API schemas
            read_schemas = []
            for entity in entities:
                schema = await self._convert_entity_to_read_schema(entity)
                if schema:
                    read_schemas.append(schema)
            
            return read_schemas
        except Exception as e:
            logging.error(f"[BiomeService] Error getting biomes by danger level {danger_level}: {e}", exc_info=True)
            return []
    
    async def get_biomes_by_movement_range(self, min_modifier: float, max_modifier: float) -> List[BiomeRead]:
        """
        Gets biomes within a specific movement modifier range.
        
        Args:
            min_modifier: Minimum movement modifier
            max_modifier: Maximum movement modifier
            
        Returns:
            List of biomes within the movement modifier range
        """
        logging.debug(f"[BiomeService] Getting biomes with movement modifier between {min_modifier} and {max_modifier}")
        try:
            # Use repository to find biomes
            entities = await self.repository.find_by_movement_modifier(min_modifier, max_modifier)
            
            # Convert to API schemas
            read_schemas = []
            for entity in entities:
                schema = await self._convert_entity_to_read_schema(entity)
                if schema:
                    read_schemas.append(schema)
            
            return read_schemas
        except Exception as e:
            logging.error(f"[BiomeService] Error getting biomes by movement range: {e}", exc_info=True)
            return []

# --- END OF FILE app/game_state/services/biome_service.py ---