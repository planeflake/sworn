# --- START - app/game_state/services/resource_service.py ---

import logging
from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.services.core.base_service import BaseService
from app.game_state.repositories.resource_repository import ResourceRepository
from app.game_state.entities.resource.resource_pydantic import ResourceEntityPydantic

# Import API schemas
from app.api.schemas.resource import ResourceRead, ResourceCreate, ResourceUpdate

class ResourceService(BaseService[ResourceEntityPydantic, ResourceCreate, ResourceRead]):
    """
    Service layer for orchestrating Resource-related operations.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(
            db=db,
            repository=ResourceRepository(db),
            entity_class=ResourceEntityPydantic,
            response_class=ResourceRead
        )

    # get_by_id is inherited from BaseService via find_by_id

    async def get_resource_by_name(self, name: str) -> Optional[ResourceRead]:
        """
        Retrieves a specific resource type by its unique name.

        Args:
            name: The unique name of the resource type.

        Returns:
            The ResourceRead schema if found, otherwise None.
        """
        logging.debug(f"[ResourceService] Getting resource by name: {name}")
        resource_entity = await self.repository.find_by_name(name)
        if resource_entity is None:
            return None
        return ResourceRead.model_validate(resource_entity.model_dump())

    # get_all is inherited from BaseService via find_all

    async def create_resource(self, resource_data: ResourceCreate) -> ResourceRead:
        """
        Create a new resource with resource-specific validation and processing.
        """
        # Use BaseService to create entity with validation
        entity_dict = resource_data.model_dump(exclude_unset=True)
        
        # Validation phase using BaseService validation
        await self._validate_creation(entity_dict, ResourceCreate)
        
        # Pre-creation processing for resource-specific logic
        await self._pre_create_processing(entity_dict, resource_data)
        
        # Generate ID if not provided
        if 'id' not in entity_dict or entity_dict['id'] is None:
            from uuid import uuid4
            entity_dict['id'] = uuid4()
        
        # Convert to entity and create
        entity = ResourceEntityPydantic.model_validate(entity_dict)
        created_entity = await self.repository.create(entity)
        
        # Post-creation processing
        await self._post_create_processing(created_entity, resource_data)
        
        # Build response
        response = await self._build_response(created_entity)
        
        self.logger.info(f"Successfully created ResourceEntityPydantic {created_entity.id}")
        return response
        
    async def _pre_create_processing(self, entity_dict: Dict[str, Any], original_data: ResourceCreate):
        """Resource-specific pre-creation processing"""
        # Use ResourceManager for additional domain validation if needed
        try:
            # Validate resource-specific business rules
            if entity_dict.get('stack_size', 0) <= 0:
                raise ValueError("Stack size must be greater than 0")
                
            # Check for name uniqueness
            if entity_dict.get('name'):
                existing = await self.repository.find_by_name(entity_dict['name'])
                if existing:
                    raise ValueError(f"Resource with name '{entity_dict['name']}' already exists")
                    
        except Exception as e:
            self.logger.error(f"Resource pre-creation validation failed: {e}")
            raise
            
    async def _post_create_processing(self, created_entity: ResourceEntityPydantic, original_data: ResourceCreate):
        """Resource-specific post-creation processing"""
        self.logger.info(f"Resource {created_entity.name} created successfully with ID {created_entity.id}")
        
    # Keep the old method name for backward compatibility
    async def create_resource_type(self, resource_data: ResourceCreate) -> ResourceRead:
        """Backward compatibility method"""
        return await self.create_resource(resource_data)

    # update is inherited from BaseService
    
    # Keep the old method name for backward compatibility
    async def update_resource_type(self, resource_id: UUID, resource_data: ResourceUpdate) -> Optional[ResourceRead]:
        """Backward compatibility method"""
        update_data = resource_data.model_dump(exclude_unset=True)
        return await self.update_entity(resource_id, update_data)

    # delete is inherited from BaseService
    
    # Keep the old method name for backward compatibility  
    async def delete_resource_type(self, resource_id: UUID) -> bool:
        """Backward compatibility method"""
        return await self.delete_entity(resource_id)

# --- END - app/game_state/services/resource_service.py ---