# --- START - app/game_state/services/resource_service.py ---

import logging
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import dataclasses # To convert entity to dict for API model if needed

# Import API Model (for return types), Domain Entity, Manager, Repository, Enums
from app.game_state.models.resource import ResourceApiModel
from app.game_state.entities.resource import ResourceEntity
from app.game_state.managers.resource_manager import ResourceManager
from app.game_state.repositories.resource_repository import ResourceRepository
from app.game_state.enums.shared import RarityEnum, StatusEnum
# Import specific exceptions if defined (e.g., ResourceNotFoundError)
# from app.game_state.exceptions import ResourceNotFoundError

class ResourceService:
    """
    Service layer for orchestrating Resource-related operations.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ResourceRepository(db=self.db)
        # No manager instance needed if using static methods

    async def get_resource_by_id(self, resource_id: UUID) -> Optional[ResourceApiModel]:
        """
        Retrieves a specific resource type by its ID.

        Args:
            resource_id: The UUID of the resource type.

        Returns:
            The ResourceApiModel if found, otherwise None.
        """
        logging.debug(f"Service: Getting resource by ID: {resource_id}")
        resource_entity = await self.repository.find_by_id(resource_id) # Use PK name expected by repo
        if resource_entity is None:
            return None

        # Convert domain entity to API model
        return ResourceApiModel.model_validate(resource_entity)

    async def get_resource_by_name(self, name: str) -> Optional[ResourceApiModel]:
        """
        Retrieves a specific resource type by its unique name.

        Args:
            name: The unique name of the resource type.

        Returns:
            The ResourceApiModel if found, otherwise None.
        """
        logging.debug(f"Service: Getting resource by name: {name}")
        resource_entity = await self.repository.find_by_name(name)
        if resource_entity is None:
            return None
        return ResourceApiModel.model_validate(resource_entity)

    async def get_all_resources(self, skip: int = 0, limit: int = 100) -> List[ResourceApiModel]:
        """
        Retrieves a list of all defined resource types.

        Args:
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A list of ResourceApiModel objects.
        """
        logging.debug(f"Service: Getting all resources (skip={skip}, limit={limit})")
        resource_entities = await self.repository.list_all(skip=skip, limit=limit)
        # Convert list of domain entities to list of API models
        return [ResourceApiModel.model_validate(entity) for entity in resource_entities]

    async def create_resource_type(
        self,
        resource_id: UUID,
        name: str,
        description: Optional[str],
        stack_size: int,
        rarity: RarityEnum,
        status: StatusEnum = StatusEnum.ACTIVE, # Default status if not provided
        theme_id: UUID = None # Optional theme ID for the resource type
    ) -> ResourceApiModel:
        """
        Defines (creates) a new resource type in the system.

        Args:
            resource_id: The specific UUID to assign to this resource type.
            name: The name of the resource type.
            description: Optional description.
            stack_size: Default maximum stack size.
            rarity: Rarity level.
            status: Initial status (defaults to ACTIVE).
            theme_id: Optional theme ID for the resource type.

        Returns:
            The created ResourceApiModel.

        Raises:
            ValueError: If input data is invalid per domain rules.
            Exception: If a database error occurs (e.g., name conflict).
        """
        logging.info(f"Service: Defining new resource type: id={resource_id}, name='{name}'")
        logging.info(f"Service: Resource type details: description='{description}', stack_size={stack_size}, rarity={rarity}, status={status}, theme_id={theme_id}")

        # 1. Use Manager to create and validate the transient domain entity
        try:
            transient_resource_entity = ResourceManager.create_resource_entity(
                resource_id=resource_id,
                name=name,
                description=description,
                stack_size=stack_size,
                rarity=rarity,
                status=status,
                theme_id=theme_id
            )
        except ValueError as ve:
             logging.error(f"Domain validation failed for resource '{name}': {ve}")
             raise # Re-raise validation errors

        logging.info(f"Service: Transient resource entity created: {transient_resource_entity}")

        # --- Optional: Check if resource with this ID or name already exists ---
        existing_by_name = await self.repository.find_by_name(transient_resource_entity.name)
        if existing_by_name:
             raise ValueError(f"Resource type with name '{transient_resource_entity.name}' already exists.")
        # --------------------------------------------------------------------

        # 2. Use Repository to save the validated entity
        try:
            persistent_resource_entity = await self.repository.save(transient_resource_entity)
            logging.info(f"Service: Resource type '{persistent_resource_entity.name}' saved successfully.")
        except Exception as e:
             # Catch potential IntegrityErrors from DB (e.g., unique constraint fail if check above had race condition)
             logging.error(f"Database error saving resource '{name}': {e}", exc_info=True)
             raise Exception(f"Failed to save resource type '{name}' to database.") from e


        # 3. Convert persistent entity to API model for response
        return ResourceApiModel.model_validate(persistent_resource_entity)

    async def delete_resource_type(self, resource_id: UUID) -> bool:
        """
        Deletes a resource type definition.
        (Consider implications - should it just be marked inactive?)

        Args:
            resource_id: The ID of the resource type to delete.

        Returns:
            True if deleted, False if not found.
        """
        logging.warning(f"Service: Attempting to delete resource type ID: {resource_id}")
        # Add domain logic checks via Manager if needed (e.g., can't delete if in use?)
        # can_delete = ResourceManager.can_delete_resource(resource_id) # Example check
        # if not can_delete:
        #     raise ValueError("Resource type cannot be deleted (e.g., currently in use).")

        deleted = await self.repository.delete(resource_id)
        if deleted:
            logging.info(f"Service: Resource type ID {resource_id} deleted.")
        else:
            logging.warning(f"Service: Resource type ID {resource_id} not found for deletion.")
        return deleted

    # Add methods for updating resource types if needed...
    # async def update_resource_description(self, resource_id: UUID, new_description: str) -> ResourceApiModel: ...

# --- END - app/game_state/services/resource_service.py ---