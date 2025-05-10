
from app.game_state.models.character import CharacterApiModel
from app.game_state.entities.character import CharacterEntity
from typing import Optional
from uuid import UUID,uuid4
from app.game_state.enums.shared import RarityEnum, StatusEnum
from app.game_state.enums.character import CharacterTypeEnum
from app.game_state.entities.resource import ResourceEntity
import logging


class CharacterManager:
    def __init__(self):
        self.characters = []

    async def check_name_exists_in_world(self, name:str, world_id:int):
        # This method should check if a character with the given name exists in the world.
        # For now, we will just return False to indicate that the name does not exist.
        return False

    @staticmethod
    def create_character_entity(
        name: str,
        description: Optional[str] = None,
        world_id: UUID = None,
        character_type: CharacterTypeEnum = None,
    ) -> CharacterEntity:
        """
        Creates a new transient (in-memory) CharacterEntity.
        Applies initial validation or default logic if any.

        Args:
            character_id: The unique ID for this resource type.
            name: The required name for the resource.
            description: Optional description.
            stack_size: Maximum stack size.
            status: Initial status.
            theme_id: Optional theme ID.

        Returns:
            A new CharacterEntity instance.

        Raises:
            ValueError: If validation fails (e.g., invalid name).
        """
        logging.info(f"Creating transient CharacterEntity: id={id}, name='{name}, description='{description}', world_id={world_id}, character_type={character_type}")

        # --- Domain Validation Example ---
        # Add more validation based on game rules...

        # Create the entity using keyword arguments for clarity
        # after the required positional resource_id
        character_entity = CharacterEntity(
            entity_id=uuid4(),  # Generate a new UUID for the entity
            name=name,
            description=description,
            world_id=world_id,
            character_type=character_type,
            #status=status,
            # created_at/updated_at are typically handled by persistence layer
        )
        logging.debug(f"Transient ResourceEntity created: {character_entity}")
        return character_entity

    def add_character(self, character):
        self.characters.append(character)

    def remove_character(self, character):
        self.characters.remove(character)

    def get_characters(self):
        return self.characters

    def find_character_by_name(self, name):
        for character in self.characters:
            if character.name == name:
                return character
        return None

    def update_character(self, character):
        for i, c in enumerate(self.characters):
            if c.name == character.name:
                self.characters[i] = character
                break