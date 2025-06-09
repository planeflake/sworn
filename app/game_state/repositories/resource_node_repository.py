# app/game_state/repositories/resource_node_repository.py

import logging
from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.game_state.repositories.base_repository import BaseRepository
from app.db.models.resources.resource_node import ResourceNode
from app.db.models.resources.resource_node_link import ResourceNodeResource
from app.db.models.resources.resource_blueprint import ResourceBlueprint
from app.db.models.location_instance import LocationInstance
from app.db.models.resources.resource_node_blueprint import ResourceNodeBlueprint
from app.game_state.entities.resource.resource_node_pydantic import ResourceNodeEntityPydantic
from app.game_state.enums.shared import StatusEnum
from app.game_state.enums.resource import ResourceNodeVisibilityEnum

logger = logging.getLogger(__name__)


class ResourceNodeRepository(BaseRepository[ResourceNodeEntityPydantic, ResourceNode, UUID]):
    """
    Repository for ResourceNode instance operations with location-centric design.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(
            db=db,
            model_cls=ResourceNode,
            entity_cls=ResourceNodeEntityPydantic
        )

    # ==============================================================================
    # BASIC CRUD OPERATIONS (Enhanced)
    # ==============================================================================

    async def find_by_id(self, node_id: UUID) -> Optional[ResourceNodeEntityPydantic]:
        """Find resource node by ID with full details."""
        try:
            stmt = (
                select(ResourceNode)
                .options(
                    selectinload(ResourceNode.resource_links).selectinload(ResourceNodeResource.resource),
                    selectinload(ResourceNode.location)
                )
                .where(ResourceNode.id == node_id)
            )
            
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                return await self._model_to_entity_with_links(model)
            return None
            
        except Exception as e:
            logger.error(f"Error finding resource node {node_id}: {e}")
            raise

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[ResourceNodeEntityPydantic]:
        """Find all resource nodes with full details."""
        try:
            stmt = (
                select(ResourceNode)
                .options(
                    selectinload(ResourceNode.resource_links).selectinload(ResourceNodeResource.resource),
                    selectinload(ResourceNode.location)
                )
                .offset(skip)
                .limit(limit)
                .order_by(ResourceNode.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            entities = []
            for model in models:
                entity = await self._model_to_entity_with_links(model)
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error finding all resource nodes: {e}")
            raise

    # ==============================================================================
    # LOCATION-CENTRIC QUERIES
    # ==============================================================================

    async def find_by_location_id(self, location_id: UUID, skip: int = 0, limit: int = 100) -> List[ResourceNodeEntityPydantic]:
        """Find all resource nodes in a specific location."""
        try:
            stmt = (
                select(ResourceNode)
                .options(
                    selectinload(ResourceNode.resource_links).selectinload(ResourceNodeResource.resource),
                    selectinload(ResourceNode.location)
                )
                .where(ResourceNode.location_id == location_id)
                .offset(skip)
                .limit(limit)
                .order_by(ResourceNode.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            entities = []
            for model in models:
                entity = await self._model_to_entity_with_links(model)
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error finding resource nodes by location {location_id}: {e}")
            raise

    async def find_by_location_hierarchy(self, parent_location_id: UUID, skip: int = 0, limit: int = 100) -> List[ResourceNodeEntityPydantic]:
        """
        Find resource nodes in a location and all its child locations.
        Useful for continental/regional searches.
        """
        try:
            # First get all child locations (this would need to be implemented based on your location hierarchy)
            # For now, we'll just search the direct location
            return await self.find_by_location_id(parent_location_id, skip, limit)
            
        except Exception as e:
            logger.error(f"Error finding resource nodes by location hierarchy {parent_location_id}: {e}")
            raise

    async def find_by_location_and_status(
        self, 
        location_id: UUID, 
        status: StatusEnum, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ResourceNodeEntityPydantic]:
        """Find resource nodes by location and status."""
        try:
            stmt = (
                select(ResourceNode)
                .options(
                    selectinload(ResourceNode.resource_links).selectinload(ResourceNodeResource.resource),
                    selectinload(ResourceNode.location)
                )
                .where(
                    and_(
                        ResourceNode.location_id == location_id,
                        ResourceNode.status == status
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(ResourceNode.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            entities = []
            for model in models:
                entity = await self._model_to_entity_with_links(model)
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error finding resource nodes by location and status: {e}")
            raise

    async def find_by_location_and_visibility(
        self, 
        location_id: UUID, 
        visibility: ResourceNodeVisibilityEnum, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ResourceNodeEntityPydantic]:
        """Find resource nodes by location and visibility."""
        try:
            stmt = (
                select(ResourceNode)
                .options(
                    selectinload(ResourceNode.resource_links).selectinload(ResourceNodeResource.resource),
                    selectinload(ResourceNode.location)
                )
                .where(
                    and_(
                        ResourceNode.location_id == location_id,
                        ResourceNode.visibility == visibility
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(ResourceNode.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            entities = []
            for model in models:
                entity = await self._model_to_entity_with_links(model)
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error finding resource nodes by location and visibility: {e}")
            raise

    async def find_depleted_in_location(self, location_id: UUID, skip: int = 0, limit: int = 100) -> List[ResourceNodeEntityPydantic]:
        """Find depleted resource nodes in a location."""
        try:
            stmt = (
                select(ResourceNode)
                .options(
                    selectinload(ResourceNode.resource_links).selectinload(ResourceNodeResource.resource),
                    selectinload(ResourceNode.location)
                )
                .where(
                    and_(
                        ResourceNode.location_id == location_id,
                        ResourceNode.depleted == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(ResourceNode.updated_at.desc())
            )
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            entities = []
            for model in models:
                entity = await self._model_to_entity_with_links(model)
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error finding depleted nodes in location {location_id}: {e}")
            raise

    # ==============================================================================
    # RESOURCE-BASED QUERIES
    # ==============================================================================

    async def find_by_resource_id(self, resource_id: UUID, skip: int = 0, limit: int = 100) -> List[ResourceNodeEntityPydantic]:
        """Find resource nodes that can yield a specific resource."""
        try:
            stmt = (
                select(ResourceNode)
                .join(ResourceNodeResource)
                .options(
                    selectinload(ResourceNode.resource_links).selectinload(ResourceNodeResource.resource),
                    selectinload(ResourceNode.location)
                )
                .where(ResourceNodeResource.resource_id == resource_id)
                .offset(skip)
                .limit(limit)
                .order_by(ResourceNode.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            entities = []
            for model in models:
                entity = await self._model_to_entity_with_links(model)
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error finding resource nodes by resource {resource_id}: {e}")
            raise

    async def find_by_blueprint_id(self, blueprint_id: UUID, skip: int = 0, limit: int = 100) -> List[ResourceNodeEntityPydantic]:
        """Find resource nodes created from a specific blueprint."""
        try:
            # Note: This assumes you have a blueprint_id field on ResourceNode
            # If not, you might need to track this relationship differently
            stmt = (
                select(ResourceNode)
                .options(
                    selectinload(ResourceNode.resource_links).selectinload(ResourceNodeResource.resource),
                    selectinload(ResourceNode.location)
                )
                .where(ResourceNode.blueprint_id == blueprint_id)  # This field may need to be added
                .offset(skip)
                .limit(limit)
                .order_by(ResourceNode.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            entities = []
            for model in models:
                entity = await self._model_to_entity_with_links(model)
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error finding resource nodes by blueprint {blueprint_id}: {e}")
            # If blueprint relationship doesn't exist, return empty list
            return []

    # ==============================================================================
    # RESOURCE EXTRACTION TRACKING
    # ==============================================================================

    async def update_extraction_stats(
        self, 
        node_id: UUID, 
        resource_id: UUID, 
        amount_extracted: int
    ) -> Optional[ResourceNodeEntityPydantic]:
        """Update extraction statistics for a resource in a node."""
        try:
            # Find the resource link
            stmt = (
                select(ResourceNodeResource)
                .where(
                    and_(
                        ResourceNodeResource.node_id == node_id,
                        ResourceNodeResource.resource_id == resource_id
                    )
                )
            )
            
            result = await self.db.execute(stmt)
            link = result.scalar_one_or_none()
            
            if not link:
                return None

            # Update extraction statistics
            # Note: These fields would need to be added to the ResourceNodeResource model
            # For now, we'll update metadata
            if not link._metadata:
                link._metadata = {}
            
            link._metadata['times_extracted'] = link._metadata.get('times_extracted', 0) + 1
            link._metadata['total_extracted'] = link._metadata.get('total_extracted', 0) + amount_extracted
            link._metadata['last_extracted_at'] = func.now()

            await self.db.commit()
            await self.db.refresh(link)

            # Return updated node
            return await self.find_by_id(node_id)

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating extraction stats for node {node_id}: {e}")
            raise

    # ==============================================================================
    # CONVERSION HELPERS
    # ==============================================================================

    async def _model_to_entity_with_links(self, model: ResourceNode) -> ResourceNodeEntityPydantic:
        """Convert model to entity with full resource link information."""
        try:
            # Build resource links with full details
            resource_links = []
            for link in model.resource_links:
                link_data = {
                    'resource_id': link.resource_id,
                    'is_primary': link.is_primary,
                    'chance': link.chance,
                    'amount_min': link.amount_min,
                    'amount_max': link.amount_max,
                    'purity': link.purity,
                    'rarity': link.rarity,
                    'metadata': link._metadata or {}
                }
                
                # Add extraction statistics from metadata
                metadata = link._metadata or {}
                link_data.update({
                    'times_extracted': metadata.get('times_extracted', 0),
                    'total_extracted': metadata.get('total_extracted', 0),
                    'last_extracted_at': metadata.get('last_extracted_at')
                })
                
                # Add resource details if available
                if link.resource:
                    link_data.update({
                        'resource_name': link.resource.name,
                        'resource_description': link.resource.description,
                        'resource_rarity': link.resource.rarity.value if link.resource.rarity else None,
                        'resource_stack_size': link.resource.stack_size
                    })
                
                from app.game_state.entities.resource.resource_node_pydantic import ResourceNodeResourceEntityPydantic
                resource_links.append(ResourceNodeResourceEntityPydantic(**link_data))

            # Create entity
            entity_data = {
                'entity_id': model.id,
                'name': model.name,
                'description': model.description,
                'depleted': model.depleted,
                'status': model.status,
                'visibility': model.visibility,
                'resource_links': resource_links,
                'created_at': model.created_at,
                'updated_at': model.updated_at,
                'tags': model.tags or [],
                # Location information
                'location_id': model.location_id,
                'location_name': model.location.name if model.location else None,
                # Blueprint information (if tracked)
                'blueprint_id': getattr(model, 'blueprint_id', None),
            }

            return ResourceNodeEntityPydantic(**entity_data)

        except Exception as e:
            logger.error(f"Error converting model to entity: {e}")
            raise