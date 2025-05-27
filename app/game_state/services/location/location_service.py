"""
Service for locations.
"""
from uuid import UUID, uuid4
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.entities.geography.location import LocationEntity, LocationReference
from app.game_state.repositories.location.location_repository import LocationRepository
from app.game_state.services.location.location_type_service import LocationTypeService

class LocationService:
    """Service for working with locations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db
        self.repository = LocationRepository(db)
        self.type_service = LocationTypeService(db)
    
    async def get_location(self, location_id: UUID) -> Optional[LocationEntity]:
        """Get a location by ID."""
        return await self.repository.get_by_id(location_id)
    
    async def get_locations_by_type_id(self, type_id: UUID, limit: int = 100, offset: int = 0) -> List[LocationEntity]:
        """Get locations by type ID."""
        return await self.repository.get_by_type(type_id, limit, offset)
    
    async def get_locations_by_type_code(self, type_code: str, limit: int = 100, offset: int = 0) -> List[LocationEntity]:
        """Get locations by type code."""
        return await self.repository.get_by_type_code(type_code, limit, offset)
    
    async def get_children(
        self,
        parent_id: UUID,
        child_type_id: Optional[UUID] = None
    ) -> List[LocationEntity]:
        """Get child locations of a parent."""
        return await self.repository.get_children(parent_id, child_type_id)
    
    async def create_location(self, location_data: Dict[str, Any]) -> LocationEntity:
        """Create a new location from API data."""
        # Get the location type
        type_id = location_data.get("location_type_id")
        if not type_id:
            type_code = location_data.get("location_type_code")
            if type_code:
                type_entity = await self.type_service.get_type_by_code(type_code)
                if type_entity:
                    type_id = type_entity.entity_id
                else:
                    raise ValueError(f"Location type with code '{type_code}' not found")
            else:
                raise ValueError("Either location_type_id or location_type_code must be provided")
        
        # Handle parent reference
        parent = None
        if location_data.get("parent_id"):
            parent_type_id = location_data.get("parent_type_id")
            if not parent_type_id:
                parent_type_code = location_data.get("parent_type_code")
                if parent_type_code:
                    parent_type = await self.type_service.get_type_by_code(parent_type_code)
                    if parent_type:
                        parent_type_id = parent_type.entity_id
                    else:
                        raise ValueError(f"Parent type with code '{parent_type_code}' not found")
                else:
                    raise ValueError("For parent reference, both parent_id and either parent_type_id or parent_type_code must be provided")
            
            # Create parent reference
            parent = LocationReference(
                location_id=UUID(location_data["parent_id"]),
                location_type_id=UUID(parent_type_id),
                location_type_code=location_data.get("parent_type_code")
            )
            
            # Validate containment rules
            valid = await self.type_service.validate_containment(
                UUID(parent_type_id), UUID(type_id)
            )
            if not valid:
                type_entity = await self.type_service.get_type(UUID(type_id))
                parent_type_entity = await self.type_service.get_type(UUID(parent_type_id))
                raise ValueError(
                    f"Invalid parent-child relationship: {parent_type_entity.name} ({parent_type_entity.code}) "
                    f"cannot contain {type_entity.name} ({type_entity.code})"
                )
        
        # Create location entity
        location = LocationEntity(
            entity_id=uuid4(),
            name=location_data["name"],
            location_type_id=UUID(type_id),
            parent=parent,
            description=location_data.get("description"),
            coordinates=location_data.get("coordinates", {}),
            attributes=location_data.get("attributes", {}),
            tags=location_data.get("tags", []),
            is_active=location_data.get("is_active", True)
        )
        
        # Save to database
        return await self.repository.create(location)
    
    async def update_location(self, location_id: UUID, location_data: Dict[str, Any]) -> Optional[LocationEntity]:
        """Update an existing location."""
        # Get existing location
        existing = await self.repository.get_by_id(location_id)
        if not existing:
            return None
        
        # Handle type change if requested
        if "location_type_id" in location_data or "location_type_code" in location_data:
            new_type_id = None
            if "location_type_id" in location_data:
                new_type_id = UUID(location_data["location_type_id"])
            elif "location_type_code" in location_data:
                type_entity = await self.type_service.get_type_by_code(location_data["location_type_code"])
                if type_entity:
                    new_type_id = type_entity.entity_id
                else:
                    raise ValueError(f"Location type with code '{location_data['location_type_code']}' not found")
            
            if new_type_id and new_type_id != existing.location_type_id:
                # If parent exists, validate containment rules
                if existing.parent:
                    valid = await self.type_service.validate_containment(
                        existing.parent.location_type_id, new_type_id
                    )
                    if not valid:
                        parent_type = await self.type_service.get_type(existing.parent.location_type_id)
                        new_type = await self.type_service.get_type(new_type_id)
                        raise ValueError(
                            f"Invalid parent-child relationship: {parent_type.name} ({parent_type.code}) "
                            f"cannot contain {new_type.name} ({new_type.code})"
                        )
                
                existing.location_type_id = new_type_id
                existing.location_type = await self.type_service.get_type(new_type_id)
        
        # Handle parent change if requested
        if "parent_id" in location_data:
            if location_data["parent_id"] is None:
                # Remove parent
                existing.parent = None
            else:
                parent_type_id = None
                if "parent_type_id" in location_data:
                    parent_type_id = UUID(location_data["parent_type_id"])
                elif "parent_type_code" in location_data:
                    parent_type = await self.type_service.get_type_by_code(location_data["parent_type_code"])
                    if parent_type:
                        parent_type_id = parent_type.entity_id
                    else:
                        raise ValueError(f"Parent type with code '{location_data['parent_type_code']}' not found")
                
                if parent_type_id:
                    # Validate containment rules
                    valid = await self.type_service.validate_containment(
                        parent_type_id, existing.location_type_id
                    )
                    if not valid:
                        parent_type = await self.type_service.get_type(parent_type_id)
                        existing_type = existing.location_type or await self.type_service.get_type(existing.location_type_id)
                        raise ValueError(
                            f"Invalid parent-child relationship: {parent_type.name} ({parent_type.code}) "
                            f"cannot contain {existing_type.name} ({existing_type.code})"
                        )
                    
                    # Set new parent
                    existing.parent = LocationReference(
                        location_id=UUID(location_data["parent_id"]),
                        location_type_id=parent_type_id,
                        location_type_code=location_data.get("parent_type_code")
                    )
        
        # Update other fields
        if "name" in location_data:
            existing.name = location_data["name"]
        
        if "description" in location_data:
            existing.description = location_data["description"]
        
        if "coordinates" in location_data:
            existing.coordinates = location_data["coordinates"]
        
        if "attributes" in location_data:
            if isinstance(location_data["attributes"], dict):
                # Merge attributes
                existing.attributes.update(location_data["attributes"])
            else:
                # Replace attributes
                existing.attributes = location_data["attributes"]
        
        if "tags" in location_data:
            existing.tags = location_data["tags"]
        
        if "is_active" in location_data:
            existing.is_active = location_data["is_active"]
        
        # Save updates
        return await self.repository.update(existing)
    
    async def get_location_with_full_data(self, location_id: UUID) -> Optional[LocationEntity]:
        """Get a location with all related data (buildings, resources, travel connections, etc.)."""
        return await self.repository.get_with_full_data(location_id)