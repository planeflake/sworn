# --- START - app/game_state/services/resource_service.py ---

import logging
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

# Import Domain Entity, Manager, Repository, Enums
from app.game_state.entities.resource import ResourceEntity
from app.game_state.managers.resource_manager import ResourceManager
from app.game_state.repositories.resource_repository import ResourceRepository
from app.game_state.enums.shared import RarityEnum, StatusEnum

# Import API schemas
from app.api.schemas.resource import ResourceRead, ResourceCreate, ResourceUpdate

class ResourceService:
    """
    Service layer for orchestrating Resource-related operations.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ResourceRepository(db=self.db)
        # No manager instance needed if using static methods

    @staticmethod
    async def _convert_entity_to_read_schema(entity: Optional[ResourceEntity]) -> Optional[ResourceRead]:
        """Convert a domain entity to an API read schema."""
        if entity is None:
            return None
            
        try:
            # Use the entity's to_dict method to get a dictionary representation
            entity_dict = entity.to_dict()
            # Validate with ResourceRead model
            return ResourceRead.model_validate(entity_dict)
        except Exception as e:
            logging.error(f"Failed to convert ResourceEntity to ResourceRead schema: {e}", exc_info=True)
            raise ValueError("Internal error converting resource data.")

    async def get_resource_by_id(self, resource_id: UUID) -> Optional[ResourceRead]:
        """
        Retrieves a specific resource type by its ID.

        Args:
            resource_id: The UUID of the resource type.

        Returns:
            The ResourceRead schema if found, otherwise None.
        """
        logging.debug(f"[ResourceService] Getting resource by ID: {resource_id}")
        resource_entity = await self.repository.find_by_id(resource_id)
        if resource_entity is None:
            return None

        # Convert domain entity to API schema
        return await self._convert_entity_to_read_schema(resource_entity)

    async def get_resource_by_name(self, name: str) -> Optional[ResourceRead]:
        """
        Retrieves a specific resource type by its unique name.

        Args:
            name: The unique name of the resource type.

        Returns:
            The ResourceRead schema if found, otherwise None.
        """
        logging.debug(f"[ResourceService] Getting resource by name: {name}")
        resource_entity = await self.repository.find_by_name(name)
        if resource_entity is None:
            return None
        return await self._convert_entity_to_read_schema(resource_entity)

    async def get_all_resources(self, skip: int = 0, limit: int = 100) -> List[ResourceRead]:
        """
        Retrieves a list of all defined resource types.

        Args:
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A list of ResourceRead schema objects.
        """
        logging.debug(f"[ResourceService] Getting all resources (skip={skip}, limit={limit})")
        resource_entities = await self.repository.list_all(skip=skip, limit=limit)
        
        # Convert list of domain entities to list of API schemas
        result = []
        for entity in resource_entities:
            schema = await self._convert_entity_to_read_schema(entity)
            if schema:
                result.append(schema)
        return result

    async def create_resource_type(
        self,
        resource_data: ResourceCreate
    ) -> ResourceRead:
        """
        Defines (creates) a new resource type in the system.

        Args:
            resource_data: The ResourceCreate schema with resource data.

        Returns:
            The created ResourceRead schema.

        Raises:
            ValueError: If input data is invalid per domain rules.
            Exception: If a database error occurs (e.g., name conflict).
        """
        logging.info(f"[ResourceService] Defining new resource type: name='{resource_data.name}'")

        # 1. Use Manager to create and validate the transient domain entity
        try:
            transient_resource_entity = ResourceManager.create_resource_entity(
                resource_id=resource_data.id or UUID(),  # Use provided ID or generate new
                name=resource_data.name,
                description=resource_data.description,
                stack_size=resource_data.stack_size,
                rarity=resource_data.rarity,
                status=resource_data.status,
                theme_id=resource_data.theme_id
            )
        except ValueError as ve:
            logging.error(f"[ResourceService] Domain validation failed for resource '{resource_data.name}': {ve}")
            raise  # Re-raise validation errors

        logging.debug(f"[ResourceService] Transient resource entity created: {transient_resource_entity}")

        # Check if resource with this name already exists
        existing_by_name = await self.repository.find_by_name(transient_resource_entity.name)
        if existing_by_name:
            raise ValueError(f"Resource type with name '{transient_resource_entity.name}' already exists.")

        # 2. Use Repository to save the validated entity
        try:
            persistent_resource_entity = await self.repository.save(transient_resource_entity)
            logging.info(f"[ResourceService] Resource type '{persistent_resource_entity.name}' saved successfully.")
        except Exception as e:
            # Catch potential database errors
            logging.error(f"[ResourceService] Database error saving resource '{resource_data.name}': {e}", exc_info=True)
            raise ValueError(f"Failed to save resource type '{resource_data.name}' to database.") from e

        # 3. Convert persistent entity to API schema for response
        return await self._convert_entity_to_read_schema(persistent_resource_entity)

    async def update_resource_type(
        self,
        resource_id: UUID,
        resource_data: ResourceUpdate
    ) -> Optional[ResourceRead]:
        """
        Updates an existing resource type.

        Args:
            resource_id: The ID of the resource to update.
            resource_data: The ResourceUpdate schema with the fields to update.

        Returns:
            The updated ResourceRead schema or None if resource not found.
            
        Raises:
            ValueError: If input data is invalid or if database error occurs.
        """
        logging.info(f"[ResourceService] Updating resource with ID: {resource_id}")
        
        # Get the existing resource
        existing_entity = await self.repository.find_by_id(resource_id)
        if not existing_entity:
            logging.warning(f"[ResourceService] Resource with ID {resource_id} not found for update")
            return None
            
        # Apply updates
        update_dict = resource_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(existing_entity, key):
                setattr(existing_entity, key, value)
                
        # Save the updated entity
        try:
            updated_entity = await self.repository.save(existing_entity)
            logging.info(f"[ResourceService] Resource '{updated_entity.name}' updated successfully")
            return await self._convert_entity_to_read_schema(updated_entity)
        except Exception as e:
            logging.error(f"[ResourceService] Error updating resource {resource_id}: {e}", exc_info=True)
            raise ValueError(f"Failed to update resource: {e}") from e

    async def delete_resource_type(self, resource_id: UUID) -> bool:
        """
        Deletes a resource type definition.

        Args:
            resource_id: The ID of the resource type to delete.

        Returns:
            True if deleted, False if not found.
        """
        logging.warning(f"[ResourceService] Attempting to delete resource type ID: {resource_id}")
        # Add domain logic checks via Manager if needed (e.g., can't delete if in use?)
        # can_delete = ResourceManager.can_delete_resource(resource_id) # Example check
        # if not can_delete:
        #     raise ValueError("Resource type cannot be deleted (e.g., currently in use).")

        deleted = await self.repository.delete(resource_id)
        if deleted:
            logging.info(f"[ResourceService] Resource type ID {resource_id} deleted.")
        else:
            logging.warning(f"[ResourceService] Resource type ID {resource_id} not found for deletion.")
        return deleted

# --- END - app/game_state/services/resource_service.py ---