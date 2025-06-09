from uuid import UUID
from typing import Optional, List
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from .base_manager import BaseManager
from app.game_state.repositories.zone_repository import ZoneRepository
from app.game_state.entities.geography.zone_pydantic import ZonePydantic


class ZoneManager(BaseManager):
    """
    Manager for Zone domain logic.
    
    This class handles business logic related to Zones, using the 
    BaseManager and ZoneRepository for persistence operations.
    """
    def __init__(self, db: AsyncSession):
        """
        Initialize the ZoneManager with a database session.
        
        Args:
            db: AsyncSession for database operations
        """
        self.db = db
        self.repository = ZoneRepository(db=db)
        logging.debug("ZoneManager initialized")
    
    @staticmethod
    def create(entity_class=ZonePydantic, entity_id: Optional[UUID] = None, **kwargs) -> ZonePydantic:
        """
        Create a new ZonePydantic entity with the provided attributes.
        
        This utilizes the BaseManager.create method to instantiate the entity.
        
        Args:
            entity_class: The entity class to create (defaults to ZonePydantic)
            entity_id: Optional UUID for the entity
            **kwargs: Additional attributes to set on the entity
                - name: Required, name of the zone
                - world_id: Required, the world this zone belongs to
                - theme_id: Optional, the primary theme of this zone
                - other fields as defined in the ZonePydantic entity
        
        Returns:
            A new ZonePydantic entity instance (not yet persisted to the database)
        """
        # Delegate to BaseManager.create
        return BaseManager.create(
            entity_class=entity_class,
            entity_id=entity_id,
            **kwargs
        )
    
    async def find_zones_by_world(self, world_id: UUID) -> List[ZonePydantic]:
        """
        Find all zones within a specific world.
        
        Args:
            world_id: The UUID of the world to find zones for
            
        Returns:
            List of ZonePydantic entities in the specified world
        """
        return await self.repository.find_by_world_id(world_id)
    
    async def save_zone(self, zone: ZonePydantic) -> ZonePydantic:
        """
        Persist a zone entity to the database.
        
        Args:
            zone: The ZonePydantic entity to save
            
        Returns:
            The saved ZonePydantic entity with any auto-generated fields populated
        """
        return await self.repository.save(zone)
