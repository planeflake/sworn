
from app.game_state.models.character import Character

class CharacterManager:
    def __init__(self):
        self.characters = []

    async def check_name_exists_in_world(self, name:str, world_id:int):
        # This method should check if a character with the given name exists in the world.
        # For now, we will just return False to indicate that the name does not exist.
        return False

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