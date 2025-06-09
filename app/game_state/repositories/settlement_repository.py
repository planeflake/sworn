# START OF FILE settlement_repository.py

from .base_repository import BaseRepository
# Use aliases for clarity
from app.game_state.entities.geography.settlement_pydantic import SettlementEntityPydantic
from app.db.models.settlement import Settlement as SettlementModel
from app.db.async_session import AsyncSession
from typing import List, Optional, Dict, Any
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
import logging

class SettlementRepository(BaseRepository[SettlementEntityPydantic, SettlementModel, UUID]):
    """
    Repository specifically for Settlement entities.
    """
    def __init__(self, db: AsyncSession):
        # Pass both the DB model class AND the domain entity class to the base repository
        super().__init__(db=db, model_cls=SettlementModel, entity_cls=SettlementEntityPydantic)
        logging.info(f"SettlementRepository initialized with model {SettlementModel.__name__} and entity {SettlementEntityPydantic.__name__}")
        
    async def find_by_id(self, entity_id: UUID) -> Optional[SettlementEntityPydantic]:
        """
        Override find_by_id to use eager loading for building_instances relationship
        to avoid the "greenlet_spawn has not been called" error.
        """
        logging.debug(f"[FindByID] Looking for {self.model_cls.__name__} with ID: {entity_id}")
        
        # Use selectinload to eagerly load the building_instances relationship
        stmt = select(self.model_cls).where(self.model_cls.entity_id == entity_id).options(
            selectinload(self.model_cls.building_instances)
        )
        
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        
        if db_obj:
            logging.debug(f"[FindByID] Found object in session/DB. Converting to entity.")
            return await self._convert_to_entity(db_obj)
        else:
            logging.debug(f"[FindByID] Object not found for ID: {entity_id}")
            return None
            
    async def _entity_to_model_dict(self, entity: SettlementEntityPydantic, is_new: bool = False) -> dict:
        """Special handling for settlement entity conversion to model dict"""
        # Debug resources before conversion
        logging.debug(f"[SettlementRepository] Resources in entity before conversion: {entity.resources}")
        logging.debug(f"[SettlementRepository] Resource keys types: {[(k, type(k)) for k in entity.resources.keys()]}")
        
        model_dict = await super()._entity_to_model_dict(entity, is_new)
        
        # Debug resources after conversion
        logging.debug(f"[SettlementRepository] Resources in model_dict after conversion: {model_dict.get('resources')}")
        
        # Remove the building_instances field which is just for entity use
        # and not a direct mapped column
        model_dict.pop('building_instances', None)
        
        # Ensure resources has string keys
        if 'resources' in model_dict and model_dict['resources'] is not None:
            resources = model_dict['resources']
            if resources and isinstance(resources, dict):
                # Convert any None keys to 'None' string to prevent database issues
                if None in resources:
                    quantity = resources.pop(None)
                    logging.warning(f"[SettlementRepository] Found None key in resources with quantity {quantity}. Converting to 'None' string.")
                    resources['None'] = quantity
            
        return model_dict

    async def find_by_world(self, world_id: UUID) -> List[SettlementEntityPydantic]:
        """Find all settlements in a specific world."""
        logging.debug(f"[SettlementRepository] Finding settlements for world: {world_id}")
        # Use eager loading for building_instances to avoid lazy loading issues
        stmt = select(self.model_cls).where(self.model_cls.world_id == world_id).options(
            selectinload(self.model_cls.building_instances)
        )
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        settlements = [await self._convert_to_entity(db_obj) for db_obj in db_objs]
        logging.debug(f"[SettlementRepository] Found {len(settlements)} settlements for world: {world_id}")
        return settlements

    async def rename(self, settlement_id: UUID, new_name: str) -> Optional[SettlementEntityPydantic]:
        """Rename a settlement."""
        logging.debug(f"[SettlementRepository] Renaming settlement {settlement_id} to '{new_name}'")
        stmt = (
            select(SettlementModel)
            .where(SettlementModel.entity_id == settlement_id)
            .options(selectinload(SettlementModel.building_instances))
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            db_obj.name = new_name
            await self.db.commit()
            updated_entity = await self._convert_to_entity(db_obj)
            logging.debug(f"[SettlementRepository] Successfully renamed settlement {settlement_id}")
            return updated_entity
        else:
            logging.warning(f"[SettlementRepository] Settlement {settlement_id} not found for rename")
            return None

    async def set_leader(self, settlement_id: UUID, leader_id: UUID) -> Optional[SettlementEntityPydantic]:
        """Set the leader of a settlement."""
        logging.debug(f"[SettlementRepository] Setting leader {leader_id} for settlement {settlement_id}")
        stmt = (
            select(self.model_cls)
            .where(self.model_cls.entity_id == settlement_id)
            .options(selectinload(self.model_cls.building_instances))
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            db_obj.leader_id = leader_id
            await self.db.commit()
            updated_entity = await self._convert_to_entity(db_obj)
            logging.debug(f"[SettlementRepository] Successfully set leader for settlement {settlement_id}")
            return updated_entity
        else:
            logging.warning(f"[SettlementRepository] Settlement {settlement_id} not found for setting leader")
            return None

    async def construct_building(self, settlement_id: UUID, building_id: str) -> Optional[SettlementEntityPydantic]:
        """Add a building to a settlement."""
        # Implementation depends on how buildings are stored (JSONB array, relation table, etc.)
        # This is a placeholder implementation
        pass

    async def demolish_building(self, settlement_id: UUID, building_id: str) -> Optional[SettlementEntityPydantic]:
        """Remove a building from a settlement."""
        # Implementation depends on how buildings are stored (JSONB array, relation table, etc.)
        # This is a placeholder implementation
        pass

    async def add_resource(self, settlement_id: UUID, resource_id: UUID, quantity: int = 1) -> Optional[SettlementEntityPydantic]:
        """
        Add a specific quantity of a resource to a settlement.
        
        Args:
            settlement_id: UUID of the settlement to modify
            resource_id: UUID of the resource to add
            quantity: Amount of the resource to add (default: 1)
            
        Returns:
            Updated settlement entity if successful, None if settlement not found
        """
        logging.debug(f"[SettlementRepository] Adding {quantity} of resource {resource_id} to settlement {settlement_id}")
        
        stmt = (
            select(self.model_cls)
            .where(self.model_cls.entity_id == settlement_id)
            .options(selectinload(self.model_cls.building_instances))
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        
        if db_obj:
            # Convert UUID to string for JSONB storage
            resource_id_str = str(resource_id)
            
            # Initialize resources dict if it's None
            if db_obj.resources is None:
                db_obj.resources = {}
                
            # Get current amount or default to 0
            current_amount = db_obj.resources.get(resource_id_str, 0)
            
            # Update the resource quantity
            db_obj.resources[resource_id_str] = current_amount + quantity
            
            await self.db.commit()
            updated_entity = await self._convert_to_entity(db_obj)
            logging.debug(f"[SettlementRepository] Successfully added resource to settlement {settlement_id}")
            return updated_entity
        else:
            logging.warning(f"[SettlementRepository] Settlement {settlement_id} not found for adding resource")
            return None
            
    async def remove_resource(self, settlement_id: UUID, resource_id: UUID, quantity: int = 1) -> Optional[SettlementEntityPydantic]:
        """
        Remove a specific quantity of a resource from a settlement.
        
        Args:
            settlement_id: UUID of the settlement to modify
            resource_id: UUID of the resource to remove
            quantity: Amount of the resource to remove (default: 1)
            
        Returns:
            Updated settlement entity if successful, None if settlement not found or not enough resources
        """
        logging.debug(f"[SettlementRepository] Removing {quantity} of resource {resource_id} from settlement {settlement_id}")
        
        stmt = (
            select(self.model_cls)
            .where(self.model_cls.entity_id == settlement_id)
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        
        if db_obj:
            # Convert UUID to string for JSONB storage
            resource_id_str = str(resource_id)
            
            # Check if resources dict exists and has enough of the resource
            if db_obj.resources is None or resource_id_str not in db_obj.resources:
                logging.warning(f"[SettlementRepository] Resource {resource_id} not found in settlement {settlement_id}")
                return None
                
            current_amount = db_obj.resources.get(resource_id_str, 0)
            
            if current_amount < quantity:
                logging.warning(f"[SettlementRepository] Not enough of resource {resource_id} in settlement {settlement_id}")
                return None
                
            # Update the resource quantity
            new_amount = current_amount - quantity
            if new_amount > 0:
                db_obj.resources[resource_id_str] = new_amount
            else:
                # Remove the key entirely if quantity reaches zero
                del db_obj.resources[resource_id_str]
            
            await self.db.commit()
            updated_entity = await self._convert_to_entity(db_obj)
            logging.debug(f"[SettlementRepository] Successfully removed resource from settlement {settlement_id}")
            return updated_entity
        else:
            logging.warning(f"[SettlementRepository] Settlement {settlement_id} not found for removing resource")
            return None
            
    async def get_resource_quantity(self, settlement_id: UUID, resource_id: UUID) -> Optional[int]:
        """
        Get the quantity of a specific resource in a settlement.
        
        Args:
            settlement_id: UUID of the settlement
            resource_id: UUID of the resource to check
            
        Returns:
            Quantity of the resource if found, None if settlement not found
        """
        logging.debug(f"[SettlementRepository] Getting quantity of resource {resource_id} in settlement {settlement_id}")
        
        stmt = select(self.model_cls).where(self.model_cls.entity_id == settlement_id)
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        
        if db_obj:
            resource_id_str = str(resource_id)
            if db_obj.resources is None:
                return 0
            return db_obj.resources.get(resource_id_str, 0)
        else:
            logging.warning(f"[SettlementRepository] Settlement {settlement_id} not found for getting resource quantity")
            return None
            
    async def has_resources(self, settlement_id: UUID, required_resources: Dict[UUID, int]) -> bool:
        """
        Check if a settlement has all the required resources.
        
        Args:
            settlement_id: UUID of the settlement
            required_resources: Dictionary mapping resource UUIDs to required quantities
            
        Returns:
            True if all required resources are available, False otherwise
        """
        logging.debug(f"[SettlementRepository] Checking if settlement {settlement_id} has required resources")
        
        stmt = select(self.model_cls).where(self.model_cls.entity_id == settlement_id)
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        
        if not db_obj:
            logging.warning(f"[SettlementRepository] Settlement {settlement_id} not found when checking resources")
            return False
            
        if db_obj.resources is None:
            # No resources available but requirements exist
            if required_resources:
                return False
            return True
            
        # Check each required resource
        for resource_id, required_quantity in required_resources.items():
            resource_id_str = str(resource_id)
            available = db_obj.resources.get(resource_id_str, 0)
            
            if available < required_quantity:
                logging.debug(f"[SettlementRepository] Settlement {settlement_id} lacks required amount of resource {resource_id}")
                return False
                
        return True
        
    async def apply_resource_costs(self, settlement_id: UUID, costs: Dict[UUID, int]) -> Optional[SettlementEntityPydantic]:
        """
        Apply a set of resource costs to a settlement. This is an atomic operation -
        either all costs are applied or none are.
        
        Args:
            settlement_id: UUID of the settlement
            costs: Dictionary mapping resource UUIDs to costs
            
        Returns:
            Updated settlement entity if successful, None if settlement not found or not enough resources
        """
        logging.debug(f"[SettlementRepository] Applying resource costs to settlement {settlement_id}")
        
        # First check if the settlement has enough resources
        has_enough = await self.has_resources(settlement_id, costs)
        if not has_enough:
            logging.warning(f"[SettlementRepository] Settlement {settlement_id} doesn't have enough resources")
            return None
            
        # Then apply all costs atomically
        stmt = (
            select(self.model_cls)
            .where(self.model_cls.entity_id == settlement_id)
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        
        if not db_obj:
            logging.warning(f"[SettlementRepository] Settlement {settlement_id} not found when applying costs")
            return None
            
        # Apply all costs
        for resource_id, cost in costs.items():
            resource_id_str = str(resource_id)
            current_amount = db_obj.resources.get(resource_id_str, 0)
            new_amount = current_amount - cost
            
            if new_amount > 0:
                db_obj.resources[resource_id_str] = new_amount
            else:
                # Remove the key entirely if quantity reaches zero
                del db_obj.resources[resource_id_str]
                
        await self.db.commit()
        updated_entity = await self._convert_to_entity(db_obj)
        logging.debug(f"[SettlementRepository] Successfully applied resource costs to settlement {settlement_id}")
        return updated_entity

# END OF FILE settlement_repository.py