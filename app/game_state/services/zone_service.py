import logging
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from app.game_state.managers.zone_manager import ZoneManager
from app.game_state.repositories.zone_repository import ZoneRepository
from app.api.schemas.zone_api_schema import ZoneBase, ZoneCreatedResponse
from app.game_state.entities.zone import Zone

class ZoneService:
    @staticmethod
    def _entity_to_zone_base(zone_entity: Zone) -> ZoneBase:
        """
        Helper method to convert a Zone entity to a ZoneBase schema.
        
        Args:
            zone_entity: The Zone entity to convert
            
        Returns:
            ZoneBase representation of the entity
        """
        zone_dict = zone_entity.to_dict()
        return ZoneBase(
            id=zone_dict["id"],
            name=zone_dict["name"],
            theme_id=zone_dict["theme_id"],
            world_id=zone_dict["world_id"],
            description=zone_dict.get("description")
        )
    def __init__(self, db: AsyncSession):
        """
        Initialize the ZoneService with a database session.
        
        Args:
            db: The database session to use for database operations.
        """
        self.db = db
        # Create an instance of ZoneManager rather than using the class
        self.manager = ZoneManager(db=db)
        self.repository = ZoneRepository(db=db)

    async def create_zone(self, zone_data: ZoneBase) -> ZoneCreatedResponse:
        """
        Create a new zone with the provided data.
        
        Args:
            zone_data: Pydantic model containing zone data from the API
                       (id, name, theme_id, world_id)
        
        Returns:
            ZoneCreatedResponse: Response with the created zone and a success message
        """
        logging.info(f"Creating zone with data {zone_data}")
        
        try:
            # 1. Extract the ID if provided, or it will be generated
            zone_id = zone_data.id  # This can be None, and that's okay
            
            # 2. Extract other fields to pass as keyword arguments
            zone_kwargs = {
                "name": zone_data.name,           # Required field from BaseEntity
                "world_id": zone_data.world_id,   # Required specific to Zone
                "theme_id": zone_data.theme_id,   # Required specific to Zone
            }
            
            # Add optional fields if they exist in the schema
            if hasattr(zone_data, 'description') and zone_data.description is not None:
                zone_kwargs["description"] = zone_data.description
                
            if hasattr(zone_data, 'status') and zone_data.status is not None:
                zone_kwargs["status"] = zone_data.status
            
            # 3. Create transient zone using the manager's static create method
            transient_zone = ZoneManager.create(
                entity_class=Zone,
                entity_id=zone_id,
                **zone_kwargs
            )
            
            # 4. Save the transient zone to the database using the repository
            persistent_zone = await self.repository.save(transient_zone)
            
            # 5. Convert entity to ZoneBase for API response
            zone_base = self._entity_to_zone_base(persistent_zone)
            
            # 6. Create and return the response
            return ZoneCreatedResponse(
                zone=zone_base,  # ZoneCreatedResponse now expects a ZoneBase object
                message="Zone created successfully"
            )
            
        except Exception as e:
            logging.error(f"Error creating zone: {e}", exc_info=True)
            raise
    
    async def get_zone_by_id(self, zone_id: UUID) -> Optional[ZoneBase]:
        """
        Get a zone by its ID.
        
        Args:
            zone_id: UUID of the zone to retrieve
            
        Returns:
            ZoneBase schema or None if not found
        """
        try:
            zone_entity = await self.repository.find_by_id(zone_id)
            if zone_entity:
                # Convert entity to ZoneBase
                return self._entity_to_zone_base(zone_entity)
            return None
        except Exception as e:
            logging.error(f"Error retrieving zone {zone_id}: {e}", exc_info=True)
            return None
    
    async def get_zones_by_world(self, world_id: UUID) -> List[ZoneBase]:
        """
        Get all zones in a specific world.
        
        Args:
            world_id: UUID of the world
            
        Returns:
            List of ZoneBase objects
        """
        try:
            # Use the manager's method to find zones by world
            zone_entities = await self.manager.find_zones_by_world(world_id)
            
            # Convert each zone entity to a ZoneBase
            result = []
            for zone in zone_entities:
                zone_base = self._entity_to_zone_base(zone)
                result.append(zone_base)
                
            return result
        except Exception as e:
            logging.error(f"Error retrieving zones for world {world_id}: {e}", exc_info=True)
            return []