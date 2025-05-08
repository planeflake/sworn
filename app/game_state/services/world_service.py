# --- START OF FILE app/game_state/services/world_service.py ---
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
import dataclasses

# Domain Entity and API Model for World
from app.game_state.entities.world import World as WorldDomainEntity
from app.game_state.models.world import WorldEntity as WorldApiModel

# Repositories and other Services
from app.game_state.repositories.world_repository import WorldRepository
from app.game_state.services.theme_service import ThemeService # Import ThemeService
from app.game_state.managers.world_manager import WorldManager

# Import base exception for more specific error handling if desired
# from sqlalchemy.exc import IntegrityError, NoResultFound

class WorldService:
    """Service for world operations - orchestrates between repository and managers"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = WorldRepository(db=self.db, entity_cls=WorldDomainEntity)
        # Instantiate ThemeService for internal use
        self._theme_service = ThemeService(db=self.db)
        logging.info("WorldService initialized with WorldRepository and ThemeService.")

    @staticmethod
    def _convert_domain_to_api(domain_entity: Optional[WorldDomainEntity]) -> Optional[WorldApiModel]:
        """Converts World Domain Entity (dataclass) to API Model (Pydantic)."""
        if domain_entity is None:
            return None
        try:
            entity_dict = dataclasses.asdict(domain_entity)

            # --- Field Name Mapping & Defaults ---
            # Ensure required API fields exist, potentially mapping from domain fields
            # Example: If domain uses 'day' and API uses 'game_day'
            if 'game_day' not in entity_dict and 'day' in entity_dict:
                 entity_dict['game_day'] = entity_dict.get('day', 0)
            # Ensure default values if domain entity might lack optional API fields
            if 'game_day' not in entity_dict: entity_dict['game_day'] = 0 # Default if missing

            # Ensure theme_id is included if present
            if hasattr(domain_entity, 'theme_id'):
                entity_dict['theme_id'] = domain_entity.theme_id

            # Ensure ID is included if present
            if hasattr(domain_entity, 'id'):
                entity_dict['id'] = domain_entity.id


            # Use Pydantic V1 `parse_obj` or V2 `model_validate`
            # return WorldApiModel.model_validate(entity_dict) # Pydantic V2
            return WorldApiModel.parse_obj(entity_dict) # Pydantic V1

        except Exception as e:
             logging.error(f"Error converting World Domain Entity to API Model: {e}. Data: {entity_dict if 'entity_dict' in locals() else 'N/A'}", exc_info=True)
             return None # Or raise a specific conversion error

    @staticmethod
    def _convert_api_to_domain(api_model: Optional[WorldApiModel]) -> Optional[WorldDomainEntity]:
        """Converts World API Model (Pydantic) to Domain Entity (dataclass)."""
        if api_model is None:
            return None
        try:
            # Pydantic V1 `dict` or V2 `model_dump`
            # api_dict = api_model.model_dump(exclude_unset=True) # Pydantic V2
            api_dict = api_model.dict(exclude_unset=True) # Pydantic V1

            # --- Field Name Mapping ---
            # Example: If domain uses 'day' and API uses 'game_day'
            if 'game_day' in api_dict and 'day' not in api_dict:
                 api_dict['day'] = api_dict.pop('game_day')

            # Instantiate domain entity (dataclass)
            return WorldDomainEntity(**api_dict)
        except TypeError as e:
             logging.error(f"Error converting World API Model to Domain Entity: {e}. Data: {api_dict if 'api_dict' in locals() else 'N/A'}", exc_info=True)
             domain_fields = {f.name for f in dataclasses.fields(WorldDomainEntity)}
             api_keys = set(api_dict.keys() if 'api_dict' in locals() else [])
             missing = domain_fields - api_keys
             extra = api_keys - domain_fields
             logging.error(f"Domain fields: {domain_fields}, API keys: {api_keys}")
             logging.error(f"Missing in API dict for Domain init: {missing}, Extra in API dict: {extra}")
             return None # Or raise

    async def get_world(self, world_id: UUID) -> Optional[WorldApiModel]:
        """Get a specific world by ID, returned as API Model."""
        logging.debug(f"WorldService: Getting world {world_id}")
        domain_entity = await self.repository.find_by_id(world_id)
        return self._convert_domain_to_api(domain_entity)

    async def get_all_worlds(self, skip: int = 0, limit: int = 100) -> List[WorldApiModel]:
        """Get all worlds, returned as API Models."""
        logging.info(f"[WorldService] get_all_worlds called (skip={skip}, limit={limit})")
        domain_entities = await self.repository.find_all(skip=skip, limit=limit)
        api_models = [self._convert_domain_to_api(de) for de in domain_entities]
        return [am for am in api_models if am is not None]

    async def create_world(self, name: str, theme_id: UUID) -> WorldApiModel:
        """
        Create a new world. Checks for theme existence. Returns API Model.
        Raises ValueError if theme not found or creation fails.
        """
        logging.info(f"[WorldService] Attempting to create world '{name}' with Theme ID: {theme_id}")

        # *** Perform Theme Existence Check ***
        theme_exists = await self._theme_service.exists(theme_id)
        if not theme_exists:
             error_msg = f"Theme ID not found: {theme_id}. Cannot create world."
             logging.warning(error_msg)
             raise ValueError(error_msg) # Raise specific error for route

        # Call WorldManager to create the DOMAIN entity
        # Ensure the domain entity has a field for theme_id, maybe Optional initially
        world_domain_entity = await WorldManager.create_world(name=name)

        logging.info(f"[WorldService] Value of world_domain_entity after creation: {world_domain_entity}")
        if world_domain_entity is None:
            logging.error("[WorldService] CRITICAL: WorldManager.create_world returned None!")

        # Set theme_id on the domain entity
        # Check if the attribute exists before setting
        if hasattr(world_domain_entity, 'theme_id'):
             world_domain_entity.theme_id = theme_id
        else:
             # This indicates a mismatch between the domain entity definition and requirements
             logging.error("CRITICAL: Domain entity WorldDomainEntity missing 'theme_id' attribute.")
             # Raise an internal server error type exception as this is a code setup issue
             raise AttributeError("Domain entity configuration error: World entity is missing 'theme_id'.")

        logging.debug(f"Domain entity prepared: {world_domain_entity}")

        # Save the DOMAIN entity using the repository
        try:
            saved_domain_entity = await self.repository.save(world_domain_entity)
            logging.info(f"World '{saved_domain_entity.name}' created and saved with ID: {saved_domain_entity.id}")
        except Exception as e:
            # Catch potential IntegrityErrors etc. from the DB save
            logging.exception(f"Error saving world entity for name '{name}', theme '{theme_id}'")
            # Raise a generic error or a specific DB error if needed
            raise ValueError(f"Database error creating world: {e}") from e

        # Convert the saved DOMAIN entity to API Model before returning
        api_model = self._convert_domain_to_api(saved_domain_entity)
        if api_model is None:
             # This indicates a problem converting the saved data back
             logging.error(f"Failed to convert saved world entity (ID: {saved_domain_entity.id}) back to API model.")
             raise ValueError("Internal error: Failed to process saved world data.")
        return api_model

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
            # Access the attribute on the domain entity ('game_day' or 'day')
            return getattr(domain_entity, 'game_day', getattr(domain_entity, 'day', 0)) # Default to 0 if missing
        return None

    async def advance_game_day(self, world_id: UUID) -> Optional[WorldApiModel]:
        """Advance world day by one. Returns updated API Model or None if world not found."""
        logging.info(f"[WorldService] advance_day called for world {world_id}")
        world_domain_entity = await self.repository.find_by_id(world_id)

        if not world_domain_entity:
            logging.warning(f"World {world_id} not found for advancing day.")
            return None # Explicitly return None if world doesn't exist

        logging.info(f"Advancing world {getattr(world_domain_entity, 'name', world_id)} by one day")

        # Call WorldManager with the DOMAIN entity
        updated_domain_entity = await WorldManager.increment_day(world_domain_entity)

        # Save updated DOMAIN entity
        try:
            saved_domain_entity = await self.repository.save(updated_domain_entity)
            logging.info(f"WorldService.advance_day finished for {world_id}. New day: {getattr(saved_domain_entity, 'game_day', None)}")
        except Exception as e:
             logging.exception(f"Error saving world {world_id} after advancing day.")
             # Decide how to handle save errors - return None? Raise?
             return None # Indicate failure

        # Convert the saved DOMAIN entity to API Model
        api_model = self._convert_domain_to_api(saved_domain_entity)
        if api_model is None:
             logging.error(f"Failed to convert updated world entity (ID: {world_id}) back to API model.")
             # This is an internal issue post-save
             return None # Indicate failure
        return api_model

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

    async def assign_theme_to_world(self, world_id: UUID, theme_id: UUID) -> Optional[WorldApiModel]:
        """Assign a theme to a world. Checks theme/world existence. Returns updated API Model."""
        logging.info(f"[WorldService] Assigning theme {theme_id} to world {world_id}")

        # *** Check if Theme Exists ***
        theme_exists = await self._theme_service.exists(theme_id)
        if not theme_exists:
            error_msg = f"Theme ID not found: {theme_id}. Cannot assign to world."
            logging.warning(error_msg)
            raise ValueError(error_msg) # Raise error for route handler

        # Fetch the World DOMAIN entity
        world_domain_entity = await self.repository.find_by_id(world_id)
        if not world_domain_entity:
            error_msg = f"World {world_id} not found. Cannot assign theme."
            logging.warning(error_msg)
            raise ValueError(error_msg) # Raise error for route handler

        # Modify and save
        saved_domain_entity = None
        try:
            if hasattr(world_domain_entity, 'theme_id'):
                # Check if update is needed
                if world_domain_entity.theme_id == theme_id:
                     logging.info(f"Theme {theme_id} is already assigned to world {world_id}. No change needed.")
                     saved_domain_entity = world_domain_entity # Use current entity for return
                else:
                     world_domain_entity.theme_id = theme_id
                     saved_domain_entity = await self.repository.save(world_domain_entity)
                     logging.info(f"Successfully assigned and saved theme {theme_id} to world {world_id}.")
            else:
                 logging.error("CRITICAL: Domain entity WorldDomainEntity missing 'theme_id' attribute.")
                 raise AttributeError("Domain entity configuration error: World entity missing 'theme_id'.")

            # Convert potentially updated DOMAIN entity to API Model
            api_model = self._convert_domain_to_api(saved_domain_entity)
            if api_model is None:
                 logging.error(f"Failed to convert world entity (ID: {world_id}) to API model after theme assignment.")
                 raise ValueError("Internal error: Failed to process world data after theme assignment.")
            return api_model

        except AttributeError as ae: # Catch config errors
             logging.exception(f"Configuration error assigning theme: {ae}")
             raise # Re-raise config errors
        except Exception as e: # Catch other errors (like DB save issues)
            logging.exception(f"Error assigning theme {theme_id} to world {world_id}: {e}")
            raise ValueError(f"Database error assigning theme: {e}") from e


# --- END OF FILE app/game_state/services/world_service.py ---