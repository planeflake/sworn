# app/game_state/services/location/location_service.py

"""
Location service with create functionality and location-specific business logic.
"""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.services.core.base_service import BaseService
from app.game_state.repositories.location.location_repository import LocationRepository
from app.game_state.entities.geography.location_pydantic import LocationEntityPydantic
from app.api.schemas.location.location_schema import LocationCreate, LocationResponse
from app.game_state.services.geography.location_sub_type_service import LocationSubTypeService

class LocationService(BaseService[LocationEntityPydantic, LocationCreate, LocationResponse]):
    """
    Location service handling location creation with business logic.
    
    Features:
    - Location subtype integration
    - Theme auto-population from subtype
    - Location-specific validation
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(
            db=db,
            repository=LocationRepository(db),
            entity_class=LocationEntityPydantic,
            response_class=LocationResponse
        )
        
        # Additional services for location-specific logic
        self.subtype_service = LocationSubTypeService(db)
    
    # ==============================================================================
    # PUBLIC API
    # ==============================================================================
    
    async def create_location(self, location_data: dict) -> LocationResponse:
        """
        Create a new location with location-specific validation and processing.
        """
        from app.api.schemas.location.location_schema import LocationCreate
        
        # Use BaseService to create entity, but customize response building
        entity_dict = location_data
        
        # Validation phase
        await self._validate_creation(entity_dict, LocationCreate)
        
        # Pre-creation processing
        location_schema = LocationCreate.model_validate(entity_dict)
        await self._pre_create_processing(entity_dict, location_schema)
        
        # Generate ID if not provided
        if 'id' not in entity_dict or entity_dict['id'] is None:
            from uuid import uuid4
            entity_dict['id'] = uuid4()
        
        # Convert to entity and create
        entity = LocationEntityPydantic.model_validate(entity_dict)
        created_entity = await self.repository.create(entity)
        
        # Post-creation processing
        await self._post_create_processing(created_entity, location_schema)
        
        # Use custom response building to populate Reference objects
        response = await self._build_response(created_entity)
        
        self.logger.info(f"Successfully created LocationEntityPydantic {created_entity.id}")
        return response
    
    # ==============================================================================
    # OVERRIDE HOOK METHODS FOR LOCATION-SPECIFIC LOGIC
    # ==============================================================================
    
    async def _validate_creation(self, entity_dict: Dict[str, Any], validation_schema=None):
        """Location-specific validation"""
        # Base FK validation handles all foreign key validation automatically
        await super()._validate_creation(entity_dict, validation_schema)
    
    async def _pre_create_processing(self, entity_dict: Dict[str, Any], original_data: LocationCreate):
        """Location-specific pre-creation processing"""
        # Handle location subtype processing
        if entity_dict.get("location_sub_type_id"):
            await self._process_location_subtype(entity_dict)
        
        # Set default coordinates if not provided
        if not entity_dict.get("coordinates"):
            entity_dict["coordinates"] = {}
    
    async def _post_create_processing(self, created_entity: LocationEntityPydantic, original_data: LocationCreate):
        """Location-specific post-creation processing"""
        self.logger.info(f"Location {created_entity.name} created successfully with ID {created_entity.id}")
        
        # Future: Initialize default resources, create travel connections, etc.
        # await self._initialize_default_resources(created_entity)

    async def _build_response(self, entity: LocationEntityPydantic) -> LocationResponse:
        """Build LocationResponse with populated Reference objects."""
        from app.api.schemas.location.location_schema import Reference
        from app.db.models.theme import ThemeDB
        from app.db.models.world import World  
        from app.db.models.biome import Biome
        from app.db.models.location_type import LocationType
        from sqlalchemy import select
        
        # Start with base entity data
        response_data = entity.model_dump()
        
        # Populate location_type Reference
        if entity.location_type_id:
            stmt = select(LocationType).where(LocationType.id == entity.location_type_id)
            result = await self.db.execute(stmt)
            location_type = result.scalar_one_or_none()
            if location_type:
                response_data["location_type"] = Reference(
                    id=location_type.id,
                    name=location_type.name,
                    code=location_type.code
                )
        
        # Populate theme Reference  
        if entity.theme_id:
            stmt = select(ThemeDB).where(ThemeDB.id == entity.theme_id)
            result = await self.db.execute(stmt)
            theme = result.scalar_one_or_none()
            if theme:
                response_data["theme"] = Reference(
                    id=theme.id,
                    name=theme.name
                )
        
        # Populate world Reference
        if entity.world_id:
            stmt = select(World).where(World.id == entity.world_id) 
            result = await self.db.execute(stmt)
            world = result.scalar_one_or_none()
            if world:
                response_data["world"] = Reference(
                    id=world.id,
                    name=world.name
                )
        
        # Populate biome Reference
        if entity.biome_id:
            stmt = select(Biome).where(Biome.id == entity.biome_id)
            result = await self.db.execute(stmt) 
            biome = result.scalar_one_or_none()
            if biome:
                response_data["biome"] = Reference(
                    id=biome.id,
                    name=biome.name
                )
        
        return LocationResponse.model_validate(response_data)
    
    # ==============================================================================
    # LOCATION-SPECIFIC BUSINESS LOGIC
    # ==============================================================================
    
    async def _process_location_subtype(self, entity_dict: Dict[str, Any]):
        """
        Process location subtype and auto-populate related fields.
        This is where the magic happens for subtype integration.
        """
        subtype_id = entity_dict.get("location_sub_type_id")
        if not subtype_id:
            return
        
        # Get subtype details
        subtype = await self.subtype_service.get_subtype_by_id(subtype_id)
        if not subtype:
            raise ValueError(f"Location subtype not found: {subtype_id}")
        
        # Auto-populate theme from subtype if not provided
        if not entity_dict.get("theme_id"):
            entity_dict["theme_id"] = subtype.theme_id
            self.logger.info(f"Auto-populated theme_id {subtype.theme_id} from subtype {subtype.name}")
        
        # Map the field name correctly for database storage
        entity_dict["sub_type_id"] = entity_dict.pop("location_sub_type_id")
        
        self.logger.info(f"Processed location subtype: {subtype.name}")


# ==============================================================================
# USAGE EXAMPLE WITH ENHANCED SCHEMA VALIDATION
# ==============================================================================

"""
# Enhanced schema with proper validation decorators:

from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, Dict, Any, List
from uuid import UUID

class LocationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    location_type_id: UUID
    location_sub_type_id: Optional[UUID] = None
    theme_id: Optional[UUID] = None
    world_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None
    coordinates: Optional[Dict[str, Any]] = None
    attributes: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = True
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip()
    
    @field_validator('attributes')
    @classmethod
    def validate_attributes(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if v is None:
            return {}
        
        # Validate population if present
        if 'population' in v:
            pop = v['population']
            if not isinstance(pop, int) or pop < 0:
                raise ValueError('Population must be a non-negative integer')
        
        return v
    
    @model_validator(mode='after')
    def validate_location_logic(self):
        # Business rule: if subtype is provided, location_type_id is required
        if self.location_sub_type_id and not self.location_type_id:
            raise ValueError('location_type_id is required when location_sub_type_id is provided')
        
        return self

# Usage in API:
@router.post("/locations/", response_model=LocationResponse)
async def create_location(
    location_data: LocationCreate,  # ✅ Validation happens here automatically
    db: AsyncSession = Depends(get_db_session)
):
    service = LocationService(db)
    try:
        return await service.create_location(location_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
"""