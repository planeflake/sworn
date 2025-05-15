import logging
import random
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean
from sqlalchemy.ext.asyncio import AsyncSession


from app.api.schemas.character import CharacterRead, CharacterCreate
from app.game_state.entities.character import CharacterEntity
from app.game_state.managers.character_manager import CharacterManager
from app.game_state.repositories.character_repository import CharacterRepository
from app.game_state.services.world_service import WorldService
import dataclasses 

class CharacterService:
    def __init__(self, db: AsyncSession, world_service: Optional[WorldService] = None): 
        """
        Initializes the CharacterService.

        Args:
            db: The asynchronous SQLAlchemy session.
            world_service: An optional instance of WorldService for dependency injection.
        """
        self.db = db
        self.character_repository = CharacterRepository(db=self.db)
        self._world_service_instance = world_service

    def _get_world_service(self) -> WorldService:
        if self._world_service_instance:
            return self._world_service_instance
        return WorldService(db=self.db) # Create if not provided

    @classmethod
    async def _convert_entity_to_read_schema(cls, entity: Optional[CharacterEntity]) -> Optional[CharacterRead]:
        """Helper to convert domain entity to Pydantic Read schema."""
        if not entity:
            return None
        try:
            # Check if entity is actually a CharacterEntity before processing
            if not isinstance(entity, CharacterEntity):
                logging.error(f"Expected CharacterEntity but got {type(entity)}")
                return None
                
            entity_dict = dataclasses.asdict(entity)
            # Handle potential 'entity_id' vs 'id' mismatch
            if 'entity_id' in entity_dict and 'id' not in entity_dict:
                 entity_dict['id'] = entity_dict.pop('entity_id')
            # Add any other specific transformations needed for CharacterReadSchema
            return CharacterRead.model_validate(entity_dict)
        except Exception as e:
            logging.error(f"Error converting CharacterEntity to CharacterReadSchema: {e}", exc_info=True)
            logging.error(f"Entity data: {entity}")
            raise ValueError("Internal error converting character data.") from e

    async def get_character_by_name(self, name: str) -> Optional[CharacterRead]: 
        """Fetches a character by name and returns its API representation."""
        logging.info(f"Fetching character by name: {name}")

        character_entity = await self.character_repository.get_by_name(name)
        return await self._convert_entity_to_read_schema(character_entity)

    async def get_by_id(self, character_id: UUID) -> Optional[CharacterRead]:
        """Fetches a character by ID and returns its API representation."""
        logging.info(f"Fetching character by ID: {character_id}")
        character_entity = await self.character_repository.find_by_id(character_id)
        return await self._convert_entity_to_read_schema(character_entity)

    async def get_by_player(self,player_id: UUID):
        """
        Fetches all characters belonging to a player.

        arguments: player_id:UUID
        returns: list of characters as CharacterRead objects
        """
        # TODO: Implement once player entity is added.
        pass

    async def create_character(self, character_data: CharacterCreate) -> CharacterRead: 
        """
        Creates a new character.

        Args:
            character_data: Pydantic schema containing character creation data.

        Returns:
            Pydantic schema of the created character.

        Raises:
            ValueError: If validation fails (e.g., world not found, name exists).
        """
        logging.info(f"Attempting to create character with data: {character_data.model_dump_json(indent=2)}")


        # Validate world_id (must be provided by the caller or handled by API default)
        if not character_data.world_id:
            # This logic should ideally be in the API layer or a default in the schema
            # If it must be here, raise a clear error.
            logging.error("world_id is missing in character_data for create_character.")
            raise ValueError("world_id is required to create a character.")

        world_service = self._get_world_service()
        world_exists = await world_service.exists(world_id=character_data.world_id)

        if not world_exists:
            logging.warning(f"World with ID {character_data.world_id} not found.")
            raise ValueError(f"World with ID {character_data.world_id} not found.") # Service raises domain error

        # Name generation for testing should be handled in test setup or API layer default
        if not character_data.name:
             # This is problematic for a service. Name should be required by the schema or defaulted there.
             logging.warning("Character name not provided, using a random test name. This should be for testing only.")
             character_data.name = f"test_Character_{random.randint(1, 1000)}"

        # Check if Character name already exists
        # Note: This check might need to be world-specific if names are unique per world.
        # The current self.get_character_by_name likely searches globally.
        # Consider: existing_character_in_world = await self.character_repository.find_by_name_and_world(name=character_data.name, world_id=character_data.world_id)
        existing_character = await self.character_repository.get_by_name(name=character_data.name)
        if existing_character:
            logging.warning(f"Character name '{character_data.name}' already exists.")
            raise ValueError(f"Character name '{character_data.name}' already exists.")

        # Call CharacterManager (static method) to create the transient domain entity
        # Pass attributes explicitly from character_data
        transient_character_entity = CharacterManager.create_character_entity(
            name=character_data.name,
            character_type=character_data.character_type, # Assuming these are in CharacterCreateSchema
            world_id=character_data.world_id,
            description=character_data.description,
            # Pass other fields from character_data as needed by CharacterManager.create
            # or directly to the CharacterEntity constructor if Manager.create is simple.
        )
        # Ensure all necessary fields for CharacterEntity are passed.
        # If CharacterManager.create doesn't take all CharacterCreateSchema fields,
        # you might need to set them on transient_character_entity after creation.

        try:
            persisted_character_entity = await self.character_repository.save(transient_character_entity)
        except Exception as e: 
            logging.error(f"Database error saving character '{character_data.name}': {e}", exc_info=True)
            raise ValueError(f"Could not save character: {e}") from e

        if persisted_character_entity is None:
            # This case should ideally be covered by an exception from repository.save
            logging.error(f"Character repository failed to save '{character_data.name}' and returned None.")
            raise ValueError("Failed to save character.")

        logging.info(f"Successfully created character: {persisted_character_entity.name} (ID: {persisted_character_entity.entity_id})")
        return await self._convert_entity_to_read_schema(persisted_character_entity)

    async def delete_character(self, character_id: UUID) -> bool:
        """Deletes a character by its ID."""
        logging.info(f"Attempting to delete character with ID: {character_id}")

        deleted = await self.character_repository.delete(character_id)
        if deleted:
            logging.info(f"Successfully deleted character ID: {character_id}")
        else:
            logging.warning(f"Character ID: {character_id} not found for deletion.")
        return deleted

    async def add_resources(self, character_id: UUID, resources: list) -> Boolean:
        """
        Adds resources to a character.

        Args:
            character_id: The ID of the character to update.
            resources: A dictionary of resources to add.

        Returns:
            True if the operation was successful, False otherwise.
        """
        #TODO: implement add_resources to character repository

        logging.info(f"Adding resources to character ID: {character_id}")

        # This method should be implemented in the repository or service layer
        # depending on how you manage resources in your game state.
        success = await self.character_repository.add_resources(character_id, resources)
        if success:
            logging.info(f"Successfully added resources to character ID: {character_id}")
        else:
            logging.warning(f"Failed to add resources to character ID: {character_id}")
        return success