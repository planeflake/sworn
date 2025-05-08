
import logging

class CharacterService:
    def __init__(self, character_repository):
        self.character_repository = character_repository

    async def create(self, character_data):
        logging.info(f"Creating character with data: {character_data}")
        return await self.character_repository.create(character_data)

    async def delete(self, character_id):
        return await self.character_repository.delete(character_id)