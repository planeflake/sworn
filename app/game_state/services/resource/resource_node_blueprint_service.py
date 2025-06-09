# app/game_state/services/resource_node_blueprint_service.py

import logging
from uuid import UUID, uuid4
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.services.core.base_service import BaseService
from app.game_state.repositories.resource_node_blueprint_repository import ResourceNodeBlueprintRepository
from app.game_state.entities.resource.resource_node_pydantic import ResourceNodeEntityPydantic
from app.api.schemas.resource_node_blueprint_schema import (
    ResourceNodeBlueprintCreate, 
    ResourceNodeBlueprintRead, 
    ResourceNodeBlueprintUpdate,
    ResourceLinkCreate
)
from app.game_state.enums.shared import StatusEnum


class ResourceNodeBlueprintService(BaseService[ResourceNodeEntityPydantic, ResourceNodeBlueprintCreate, ResourceNodeBlueprintRead]):
    """
    Service layer for ResourceNodeBlueprint operations.
    Handles blueprint creation, resource link management, and business logic.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(
            db=db,
            repository=ResourceNodeBlueprintRepository(db),
            entity_class=ResourceNodeEntityPydantic,
            response_class=ResourceNodeBlueprintRead
        )

    # ==============================================================================
    # BLUEPRINT CRUD OPERATIONS
    # ==============================================================================

    async def create_blueprint(self, blueprint_data: ResourceNodeBlueprintCreate) -> ResourceNodeBlueprintRead:
        """
        Create a new resource node blueprint with resource links.
        """
        # Use BaseService creation pattern with blueprint-specific validation
        entity_dict = blueprint_data.model_dump(exclude_unset=True)
        
        # Validation phase using BaseService validation
        await self._validate_creation(entity_dict, ResourceNodeBlueprintCreate)
        
        # Pre-creation processing for blueprint-specific logic
        await self._pre_create_processing(entity_dict, blueprint_data)
        
        # Generate ID if not provided
        if 'id' not in entity_dict or entity_dict['id'] is None:
            entity_dict['id'] = uuid4()
        
        # Convert to entity and create
        entity = ResourceNodeEntityPydantic.model_validate(entity_dict)
        created_entity = await self.repository.create(entity)
        
        # Post-creation processing (handle resource links)
        await self._post_create_processing(created_entity, blueprint_data)
        
        # Build response with full details
        response = await self._build_blueprint_response(created_entity)
        
        self.logger.info(f"Successfully created ResourceNodeBlueprint {created_entity.id}")
        return response

    async def find_by_id(self, blueprint_id: UUID) -> Optional[ResourceNodeBlueprintRead]:
        """Override find_by_id to return proper response format."""
        entity = await self.repository.find_by_id(blueprint_id)
        if entity:
            return await self._build_blueprint_response(entity)
        return None

    async def get_blueprint_by_name(self, name: str) -> Optional[ResourceNodeBlueprintRead]:
        """Get blueprint by unique name."""
        entity = await self.repository.find_by_name(name)
        if entity:
            return await self._build_blueprint_response(entity)
        return None

    async def get_blueprints_by_biome(self, biome_type: str, skip: int = 0, limit: int = 100) -> List[ResourceNodeBlueprintRead]:
        """Get blueprints for a specific biome type."""
        entities = await self.repository.find_by_biome_type(biome_type, skip, limit)
        return [await self._build_blueprint_response(entity) for entity in entities]

    async def get_blueprints_by_status(self, status: StatusEnum, skip: int = 0, limit: int = 100) -> List[ResourceNodeBlueprintRead]:
        """Get blueprints by status."""
        entities = await self.repository.find_by_status(status, skip, limit)
        return [await self._build_blueprint_response(entity) for entity in entities]

    async def get_blueprints_by_resource(self, resource_id: UUID, skip: int = 0, limit: int = 100) -> List[ResourceNodeBlueprintRead]:
        """Get blueprints that can yield a specific resource."""
        entities = await self.repository.find_by_resource_id(resource_id, skip, limit)
        return [await self._build_blueprint_response(entity) for entity in entities]

    async def get_blueprints_by_world(self, world_id: UUID, skip: int = 0, limit: int = 100) -> List[ResourceNodeBlueprintRead]:
        """Get blueprints associated with a specific world through theme relationships."""
        entities = await self.repository.find_by_world_id(world_id, skip, limit)
        return [await self._build_blueprint_response(entity) for entity in entities]

    # ==============================================================================
    # RESOURCE LINK MANAGEMENT
    # ==============================================================================

    async def add_resource_to_blueprint(
        self, 
        blueprint_id: UUID, 
        resource_link: ResourceLinkCreate
    ) -> Optional[ResourceNodeBlueprintRead]:
        """Add a resource link to an existing blueprint."""
        try:
            # Validate the resource exists
            await self.validator.validate_entity_exists(
                entity_id=resource_link.resource_id,
                service_name="resource", 
                entity_name="Resource"
            )
            
            # Validate theme if provided
            if resource_link.theme_id:
                await self.validator.validate_entity_exists(
                    entity_id=resource_link.theme_id,
                    service_name="theme", 
                    entity_name="Theme"
                )

            # Add the resource link
            link_data = resource_link.model_dump()
            updated_entity = await self.repository.add_resource_link(
                blueprint_id, 
                resource_link.resource_id, 
                link_data
            )

            if updated_entity:
                self.logger.info(f"Added resource {resource_link.resource_id} to blueprint {blueprint_id}")
                return await self._build_blueprint_response(updated_entity)
            
            return None

        except Exception as e:
            self.logger.error(f"Error adding resource to blueprint {blueprint_id}: {e}")
            raise

    async def remove_resource_from_blueprint(self, blueprint_id: UUID, resource_id: UUID) -> bool:
        """Remove a resource link from a blueprint."""
        try:
            success = await self.repository.remove_resource_link(blueprint_id, resource_id)
            if success:
                self.logger.info(f"Removed resource {resource_id} from blueprint {blueprint_id}")
            return success

        except Exception as e:
            self.logger.error(f"Error removing resource from blueprint {blueprint_id}: {e}")
            raise

    # ==============================================================================
    # OVERRIDE HOOK METHODS FOR BLUEPRINT-SPECIFIC LOGIC
    # ==============================================================================

    async def _validate_creation(self, entity_dict: Dict[str, Any], validation_schema=None):
        """Blueprint-specific validation"""
        # Base FK validation handles all foreign key validation automatically
        await super()._validate_creation(entity_dict, validation_schema)

    async def _pre_create_processing(self, entity_dict: Dict[str, Any], original_data: ResourceNodeBlueprintCreate):
        """Blueprint-specific pre-creation processing"""
        try:
            # Validate business rules
            if entity_dict.get('name'):
                # Check for name uniqueness
                existing = await self.repository.find_by_name(entity_dict['name'])
                if existing:
                    raise ValueError(f"Blueprint with name '{entity_dict['name']}' already exists")

            # Validate resource links if provided
            resource_links = original_data.resource_links or []
            for link in resource_links:
                if link.amount_min > link.amount_max:
                    raise ValueError(f"amount_min ({link.amount_min}) cannot be greater than amount_max ({link.amount_max})")
                
                if not (0.0 <= link.chance <= 1.0):
                    raise ValueError(f"Resource chance must be between 0.0 and 1.0, got {link.chance}")
                
                if not (0.0 <= link.purity <= 1.0):
                    raise ValueError(f"Resource purity must be between 0.0 and 1.0, got {link.purity}")

            # Set default values
            if 'status' not in entity_dict:
                entity_dict['status'] = StatusEnum.PENDING
            
            if 'depleted' not in entity_dict:
                entity_dict['depleted'] = False

            # Process tags
            if 'tags' not in entity_dict:
                entity_dict['tags'] = []

        except Exception as e:
            self.logger.error(f"Blueprint pre-creation validation failed: {e}")
            raise

    async def _post_create_processing(self, created_entity: ResourceNodeEntityPydantic, original_data: ResourceNodeBlueprintCreate):
        """Blueprint-specific post-creation processing"""
        self.logger.info(f"Blueprint {created_entity.name} created successfully with ID {created_entity.id}")
        
        # Handle resource links creation
        if original_data.resource_links:
            for link in original_data.resource_links:
                try:
                    await self.add_resource_to_blueprint(created_entity.id, link)
                except Exception as e:
                    self.logger.warning(f"Failed to add resource link during creation: {e}")
                    # Continue with other links rather than failing completely

    async def _build_blueprint_response(self, entity: ResourceNodeEntityPydantic) -> ResourceNodeBlueprintRead:
        """Build detailed blueprint response with resource statistics."""
        try:
            # Convert entity to base response data
            response_data = entity.model_dump()
            
            # Add blueprint-specific calculations
            total_resources = len(entity.resource_links)
            primary_resources = sum(1 for link in entity.resource_links if link.is_primary)
            secondary_resources = total_resources - primary_resources

            # Build the complete response
            response_data.update({
                'id': entity.id,
                'total_resources': total_resources,
                'primary_resources': primary_resources,
                'secondary_resources': secondary_resources,
                # Map any missing fields
                'biome_type': getattr(entity, 'biome_type', None),
                'metadata': getattr(entity, 'metadata', {}),
            })

            return ResourceNodeBlueprintRead.model_validate(response_data)

        except Exception as e:
            self.logger.error(f"Error building blueprint response: {e}")
            raise

    # ==============================================================================
    # BACKWARD COMPATIBILITY METHODS
    # ==============================================================================

    async def create_resource_node_blueprint(self, blueprint_data: ResourceNodeBlueprintCreate) -> ResourceNodeBlueprintRead:
        """Backward compatibility method"""
        return await self.create_blueprint(blueprint_data)

    async def update_resource_node_blueprint(self, blueprint_id: UUID, update_data: ResourceNodeBlueprintUpdate) -> Optional[ResourceNodeBlueprintRead]:
        """Backward compatibility method"""
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_entity = await self.update_entity(blueprint_id, update_dict)
        if updated_entity:
            return await self._build_blueprint_response(updated_entity)
        return None

    async def delete_resource_node_blueprint(self, blueprint_id: UUID) -> bool:
        """Backward compatibility method"""
        return await self.delete_entity(blueprint_id)