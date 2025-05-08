# START OF FILE app/game_state/services/settlement_service.py

from app.game_state.models.settlement import SettlementEntity # Pydantic Model
# from app.game_state.entities.settlement import Settlement as SettlementDomainEntity # Optional for type hinting
from app.game_state.repositories.settlement_repository import SettlementRepository # Import Repository
from app.game_state.managers.settlement_manager import SettlementManager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import ValidationError
from uuid import UUID
import dataclasses
import json # Import json for parsing
import logging # Import logging

class SettlementService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # Instantiate repository here
        self.repository = SettlementRepository(db=self.db)

    async def create(self, name: str, description: Optional[str], world_id: UUID) -> SettlementEntity: # Return Pydantic model
        """Creates a settlement using the manager, saves it via the repository, and returns a Pydantic model."""

        # 1. Call the manager to create the transient domain entity
        transient_settlement = SettlementManager.create(
            name=name,
            description=description,
            world_id=world_id
        )

        # 2. Call the repository to save the entity
        persistent_settlement = await self.repository.save(transient_settlement)

        if persistent_settlement is None:
             raise ValueError("Failed to save settlement entity.")

        # 3. Convert the persistent domain entity (dataclass) to dict
        try:
            settlement_data = dataclasses.asdict(persistent_settlement)

            if 'resources' in settlement_data:
                res_value = settlement_data['resources']
                if isinstance(res_value, str):
                    try:
                        # Attempt to parse string representation of list/dict
                        parsed_res = json.loads(res_value)
                        if isinstance(parsed_res, list):
                             settlement_data['resources'] = parsed_res
                        else:
                             # Handle case where JSON is valid but not a list (e.g., "{}")
                             logging.warning(f"Parsed 'resources' string but result was not a list ({type(parsed_res)}), defaulting to empty list.")
                             settlement_data['resources'] = []
                    except json.JSONDecodeError:
                        logging.warning(f"Could not JSON decode 'resources' string: {res_value}, defaulting to empty list.")
                        settlement_data['resources'] = [] # Default on error
                elif not isinstance(res_value, list):
                    # Handle cases where it's not a string but also not a list (e.g., None?)
                    logging.warning(f"Field 'resources' is not a list or valid JSON string ({type(res_value)}), defaulting to empty list.")
                    settlement_data['resources'] = []
            else:
                 # Field might be missing if conversion failed earlier
                 logging.warning("Field 'resources' missing from settlement_data, defaulting to empty list.")
                 settlement_data['resources'] = []

            # 4. Validate data using the Pydantic API Model
            if 'entity_id' in settlement_data and hasattr(SettlementEntity, 'id') and 'id' not in settlement_data:
                 settlement_data['id'] = settlement_data.pop('entity_id')

            settlement_api_model = SettlementEntity.model_validate(settlement_data)
            return settlement_api_model # Return the validated Pydantic model

        except (ValidationError, TypeError, ValueError) as e: # Catch specific errors
             logging.error(f"Error converting/validating Settlement domain entity to SettlementEntity model: {e}", exc_info=True)
             logging.error(f"Persistent entity data object: {persistent_settlement}") # Log the object itself
             logging.error(f"Data passed to model_validate: {settlement_data if 'settlement_data' in locals() else 'Not available'}")
             raise ValueError("Failed to convert created settlement to API model.") from e
        except Exception as e: # Catch any other unexpected errors during conversion
             logging.error(f"Unexpected error during final settlement conversion: {e}", exc_info=True)
             raise ValueError("Unexpected error processing settlement data.") from e

    async def delete(self, settlement_id: str) -> bool:
        """Deletes a settlement by its ID."""
        try:
            # Call the repository to delete the settlement
            result = await self.repository.delete(settlement_id=settlement_id)
            return result
        except Exception as e:
            logging.error(f"Error deleting settlement with ID {settlement_id}: {e}", exc_info=True)
            return False

    async def rename(self, settlement_id: str, new_name: str) -> SettlementEntity:
        """Renames a settlement by its ID."""
        try:
            # Call the repository to rename the settlement
            updated_settlement = await self.repository.rename(settlement_id=settlement_id, new_name=new_name)
            return updated_settlement
        except Exception as e:
            logging.error(f"Error renaming settlement with ID {settlement_id}: {e}", exc_info=True)
            raise

    async def set_leader(self, settlement_id: str, leader_id: str) -> SettlementEntity:
        """"Sets the leader of a settlement by its ID."""
        try:
            # Call the repository to set the leader
            updated_settlement = await self.repository.set_leader(settlement_id=settlement_id, leader_id=leader_id)
            return updated_settlement
        except Exception as e:
            logging.error(f"Error setting leader for settlement with ID {settlement_id}: {e}", exc_info=True)
            raise

    async def construct_building(self, settlement_id: str, building_id: str) -> SettlementEntity:
        """Constructs a building in a settlement by its ID."""
        try:
            # Call the repository to construct the building
            updated_settlement = await self.repository.construct_building(settlement_id=settlement_id, building_id=building_id)
            return updated_settlement
        except Exception as e:
            logging.error(f"Error constructing building in settlement with ID {settlement_id}: {e}", exc_info=True)
            raise

    async def demolish_building(self, settlement_id: str, building_id: str) -> SettlementEntity:
        """Demolishes a building in a settlement by its ID."""
        try:
            # Call the repository to demolish the building
            updated_settlement = await self.repository.demolish_building(settlement_id=settlement_id, building_id=building_id)
            return updated_settlement
        except Exception as e:
            logging.error(f"Error demolishing building in settlement with ID {settlement_id}: {e}", exc_info=True)
            raise
        
    async def add_resource(self, settlement_id: str, resource_id: str) -> SettlementEntity:
        """Adds a resource to a settlement by its ID."""
        try:
            # Call the repository to add the resource
            updated_settlement = await self.repository.add_resource(settlement_id=settlement_id, resource_id=resource_id)
            return updated_settlement
        except Exception as e:
            logging.error(f"Error adding resource to settlement with ID {settlement_id}: {e}", exc_info=True)
            raise

    async def expand_settlement(self, settlement_id: str) -> SettlementEntity:
        """Expands a settlement by its ID."""
        pass