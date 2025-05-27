"""
Service for location types.
"""
from uuid import UUID, uuid4
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.entities.geography.location import LocationTypeEntity
from app.game_state.repositories.location.location_type_repository import LocationTypeRepository

class LocationTypeService:
    """Service for working with location types."""
    
    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db
        self.repository = LocationTypeRepository(db)
    
    async def get_type(self, type_id: UUID) -> Optional[LocationTypeEntity]:
        """Get a location type by ID."""
        return await self.repository.get_by_id(type_id)
    
    async def get_type_by_code(self, code: str) -> Optional[LocationTypeEntity]:
        """Get a location type by code."""
        return await self.repository.get_by_code(code)
    
    async def get_all_types(self, theme: Optional[str] = None) -> List[LocationTypeEntity]:
        """Get all location types, optionally filtered by theme."""
        return await self.repository.get_all(theme)
    
    async def create_type(self, type_data: Dict[str, Any]) -> LocationTypeEntity:
        """Create a new location type."""
        # Ensure code is unique
        code = type_data.get("code")
        existing = await self.repository.get_by_code(code)
        if existing:
            raise ValueError(f"Location type with code '{code}' already exists")
        
        # Create entity
        type_entity = LocationTypeEntity(
            entity_id=uuid4(),
            code=code,
            name=type_data.get("name"),
            description=type_data.get("description"),
            theme=type_data.get("theme"),
            can_contain=type_data.get("can_contain", []),
            required_attributes=type_data.get("required_attributes", []),
            optional_attributes=type_data.get("optional_attributes", []),
            icon_path=type_data.get("icon_path"),
            tags=type_data.get("tags", [])
        )
        
        # Save to database
        return await self.repository.create(type_entity)
    
    async def update_type(self, type_id: UUID, type_data: Dict[str, Any]) -> Optional[LocationTypeEntity]:
        """Update an existing location type."""
        # Get existing type
        existing = await self.repository.get_by_id(type_id)
        if not existing:
            return None
        
        # Check if code is being changed and is unique
        if "code" in type_data and type_data["code"] != existing.code:
            code_check = await self.repository.get_by_code(type_data["code"])
            if code_check:
                raise ValueError(f"Location type with code '{type_data['code']}' already exists")
        
        # Update fields
        for key, value in type_data.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        
        # Save updates
        return await self.repository.update(existing)
    
    async def delete_type(self, type_id: UUID) -> bool:
        """Delete a location type if not in use."""
        return await self.repository.delete(type_id)
    
    async def validate_containment(self, parent_type_id: UUID, child_type_id: UUID) -> bool:
        """Validate that a parent type can contain a child type."""
        parent_type = await self.repository.get_by_id(parent_type_id)
        child_type = await self.repository.get_by_id(child_type_id)
        
        if not parent_type or not child_type:
            return False
        
        return parent_type.can_contain_type(child_type.code)