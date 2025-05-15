# --- START OF FILE app/game_state/services/world_service.py ---
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional

# Domain Entity
from app.game_state.entities.world import WorldEntity

# API Schemas
from app.api.schemas.world import WorldRead, WorldCreate, WorldUpdate

# Repositories and other Services
from app.game_state.repositories.world_repository import WorldRepository
from app.game_state.services.theme_service import ThemeService
from app.game_state.managers.world_manager import WorldManager

class WorldService:
    """Service for world operations - orchestrates between repository and managers"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = WorldRepository(db=self.db, entity_cls=WorldEntity)
        # Instantiate ThemeService for internal use
        self._theme_service = ThemeService(db=self.db)
        logging.info("WorldService initialized with WorldRepository and ThemeService.")

    @staticmethod
    async def _convert_entity_to_read_schema(entity: Optional[WorldEntity]) -> Optional[WorldRead]:
        """Convert a domain entity to an API read schema."""
        if entity is None:
            return None
            
        try:
            # Use the entity's to_dict method to get a dictionary representation
            entity_dict = entity.to_dict()
            # Validate with WorldRead model
            return WorldRead.model_validate(entity_dict)
        except Exception as e:
            logging.error(f"Failed to convert World entity to Read schema: {e}", exc_info=True)
            raise ValueError("Internal error converting world data.")

    async def get_world(self, world_id: UUID) -> Optional[WorldRead]:
        """Get a specific world by ID, returned as API Schema."""
        logging.debug(f"[WorldService] Getting world {world_id}")
        domain_entity = await self.repository.find_by_id(world_id)
        return await self._convert_entity_to_read_schema(domain_entity)

    async def get_all_worlds(self, skip: int = 0, limit: int = 100) -> List[WorldRead]:
        """Get all worlds, returned as API Schemas."""
        logging.info(f"[WorldService] get_all_worlds called (skip={skip}, limit={limit})")
        domain_entities = await self.repository.find_all(skip=skip, limit=limit)
        
        result = []
        for entity in domain_entities:
            schema = await self._convert_entity_to_read_schema(entity)
            if schema:
                result.append(schema)
        return result

    async def create_world(self, world_data: WorldCreate) -> WorldRead:
        """
        Create a new world. Checks for theme existence. Returns API Schema.
        Raises ValueError if theme not found or creation fails.
        """
        logging.info(f"[WorldService] Attempting to create world '{world_data.name}' with Theme ID: {world_data.theme_id}")

        # *** Perform Theme Existence Check ***
        theme_exists = await self._theme_service.exists(world_data.theme_id)
        if not theme_exists:
            error_msg = f"Theme ID not found: {world_data.theme_id}. Cannot create world."
            logging.warning(error_msg)
            raise ValueError(error_msg)

        # Call WorldManager to create the DOMAIN entity
        world_domain_entity = await WorldManager.create_world(name=world_data.name)

        logging.info(f"[WorldService] Value of world_domain_entity after creation: {world_domain_entity}")
        if world_domain_entity is None:
            logging.error("[WorldService] CRITICAL: WorldManager.create_world returned None!")
            raise ValueError("Failed to create world entity.")

        # Set theme_id and description on the domain entity
        world_domain_entity.theme_id = world_data.theme_id
        if world_data.description:
            world_domain_entity.description = world_data.description

        logging.debug(f"[WorldService] Domain entity prepared: {world_domain_entity}")

        # Save the DOMAIN entity using the repository
        try:
            saved_domain_entity = await self.repository.save(world_domain_entity)
            logging.info(f"World '{saved_domain_entity.name}' created and saved with ID: {saved_domain_entity.id}")
        except Exception as e:
            # Catch potential database errors
            logging.exception(f"Error saving world entity for name '{world_data.name}', theme '{world_data.theme_id}'")
            raise ValueError(f"Database error creating world: {e}") from e

        # Convert the saved DOMAIN entity to API Schema before returning
        api_schema = await self._convert_entity_to_read_schema(saved_domain_entity)
        if api_schema is None:
            # This indicates a problem converting the saved data back
            logging.error(f"Failed to convert saved world entity (ID: {saved_domain_entity.id}) back to API schema.")
            raise ValueError("Internal error: Failed to process saved world data.")
        return api_schema

    async def update_world(self, world_id: UUID, world_data: WorldUpdate) -> Optional[WorldRead]:
        """
        Update an existing world.
        
        Args:
            world_id: The ID of the world to update
            world_data: WorldUpdate schema with fields to update
            
        Returns:
            Updated WorldRead schema or None if world not found
        """
        logging.info(f"[WorldService] Updating world {world_id}")
        
        # Get the existing world
        world_domain_entity = await self.repository.find_by_id(world_id)
        if not world_domain_entity:
            logging.warning(f"[WorldService] World {world_id} not found for update.")
            return None
        
        # If updating theme_id, check if theme exists
        if world_data.theme_id is not None and world_data.theme_id != world_domain_entity.theme_id:
            theme_exists = await self._theme_service.exists(world_data.theme_id)
            if not theme_exists:
                error_msg = f"Theme ID not found: {world_data.theme_id}. Cannot update world."
                logging.warning(error_msg)
                raise ValueError(error_msg)
        
        # Apply updates
        update_dict = world_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(world_domain_entity, key):
                setattr(world_domain_entity, key, value)
                
        # Save the updated entity
        try:
            updated_entity = await self.repository.save(world_domain_entity)
            logging.info(f"[WorldService] World '{updated_entity.name}' updated successfully")
            return await self._convert_entity_to_read_schema(updated_entity)
        except Exception as e:
            logging.error(f"[WorldService] Error updating world {world_id}: {e}", exc_info=True)
            raise ValueError(f"Failed to update world: {e}") from e

    async def delete_world(self, world_id: UUID) -> bool:
        """Delete a world. Returns True if successful, False otherwise."""
        logging.info(f"[WorldService] Deleting world {world_id}")
        try:
            return await self.repository.delete(world_id)
        except Exception as e:
            logging.error(f"Error deleting world {world_id}: {e}", exc_info=True)
            return False

    async def get_day(self, world_id: UUID) -> Optional[int]:
        """Get the current game day for a specific world."""
        domain_entity = await self.repository.find_by_id(world_id)
        if domain_entity:
            return domain_entity.day
        return None

    async def advance_game_day(self, world_id: UUID) -> Optional[WorldRead]:
        """Advance world day by one. Returns updated API Schema or None if world not found."""
        logging.info(f"[WorldService] advance_day called for world {world_id}")
        world_domain_entity = await self.repository.find_by_id(world_id)

        if not world_domain_entity:
            logging.warning(f"World {world_id} not found for advancing day.")
            return None

        logging.info(f"Advancing world {world_domain_entity.name} by one day")

        # Call WorldManager with the DOMAIN entity
        updated_domain_entity = await WorldManager.increment_day(world_domain_entity)

        # Save updated DOMAIN entity
        try:
            saved_domain_entity = await self.repository.save(updated_domain_entity)
            logging.info(f"[WorldService] advance_day finished for {world_id}. New day: {saved_domain_entity.day}")
        except Exception as e:
            logging.exception(f"Error saving world {world_id} after advancing day.")
            return None

        # Convert the saved DOMAIN entity to API Schema
        return await self._convert_entity_to_read_schema(saved_domain_entity)

    async def get_world_name(self, world_id: UUID) -> Optional[str]:
        """Get the name of a specific world."""
        domain_entity = await self.repository.find_by_id(world_id)
        return domain_entity.name if domain_entity else None

    async def exists(self, world_id: UUID) -> bool:
        """Check if a world exists."""
        logging.info(f"[WorldService] exists called for {world_id}")
        try:
            exists_result = await self.repository.exists(world_id)
            logging.info(f"World {world_id} exists check result: {exists_result}")
            return exists_result
        except Exception as e:
            logging.error(f"Error checking existence for world {world_id}: {e}", exc_info=True)
            return False

    async def assign_theme_to_world(self, world_id: UUID, theme_id: UUID) -> Optional[WorldRead]:
        """Assign a theme to a world. Checks theme/world existence. Returns updated API Schema."""
        logging.info(f"[WorldService] Assigning theme {theme_id} to world {world_id}")

        # Check if Theme Exists
        theme_exists = await self._theme_service.exists(theme_id)
        if not theme_exists:
            error_msg = f"Theme ID not found: {theme_id}. Cannot assign to world."
            logging.warning(error_msg)
            raise ValueError(error_msg)

        # Fetch the World DOMAIN entity
        world_domain_entity = await self.repository.find_by_id(world_id)
        if not world_domain_entity:
            error_msg = f"World {world_id} not found. Cannot assign theme."
            logging.warning(error_msg)
            raise ValueError(error_msg)

        # Modify and save
        saved_domain_entity = None
        try:
            # Check if update is needed
            if world_domain_entity.theme_id == theme_id:
                logging.info(f"Theme {theme_id} is already assigned to world {world_id}. No change needed.")
                saved_domain_entity = world_domain_entity  # Use current entity for return
            else:
                world_domain_entity.theme_id = theme_id
                saved_domain_entity = await self.repository.save(world_domain_entity)
                logging.info(f"Successfully assigned and saved theme {theme_id} to world {world_id}.")

            # Convert potentially updated DOMAIN entity to API Schema
            return await self._convert_entity_to_read_schema(saved_domain_entity)

        except Exception as e:
            logging.exception(f"Error assigning theme {theme_id} to world {world_id}: {e}")
            raise ValueError(f"Database error assigning theme: {e}") from e

# --- END OF FILE app/game_state/services/world_service.py ---