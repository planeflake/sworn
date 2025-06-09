# app/game_state/repositories/resource_node_blueprint_repository.py

import logging
from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.game_state.repositories.base_repository import BaseRepository
from app.db.models.resources.resource_node_blueprint import ResourceNodeBlueprint
from app.db.models.resources.resource_node_blueprint_link import ResourceNodeBlueprintResource
from app.db.models.resources.resource_blueprint import ResourceBlueprint
from app.db.models.theme import ThemeDB
from app.game_state.entities.resource.resource_node_pydantic import ResourceNodeEntityPydantic
from app.game_state.enums.shared import StatusEnum

logger = logging.getLogger(__name__)


class ResourceNodeBlueprintRepository(BaseRepository[ResourceNodeEntityPydantic, ResourceNodeBlueprint, UUID]):
    """
    Repository for ResourceNodeBlueprint operations with complex resource link handling.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(
            db=db,
            model_cls=ResourceNodeBlueprint,
            entity_cls=ResourceNodeEntityPydantic
        )

    # ==============================================================================
    # BASIC CRUD OPERATIONS (Enhanced)
    # ==============================================================================

    async def find_by_id(self, blueprint_id: UUID) -> Optional[ResourceNodeEntityPydantic]:
        """Find blueprint by ID with full resource link details."""
        try:
            stmt = (
                select(ResourceNodeBlueprint)
                .options(
                    selectinload(ResourceNodeBlueprint.resource_links).selectinload(ResourceNodeBlueprintResource.resource),
                    selectinload(ResourceNodeBlueprint.resource_links).selectinload(ResourceNodeBlueprintResource.theme)
                )
                .where(ResourceNodeBlueprint.id == blueprint_id)
            )
            
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                return await self._model_to_entity_with_links(model)
            return None
            
        except Exception as e:
            logger.error(f"Error finding blueprint {blueprint_id}: {e}")
            raise

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[ResourceNodeEntityPydantic]:
        """Find all blueprints with resource links."""
        try:
            stmt = (
                select(ResourceNodeBlueprint)
                .options(
                    selectinload(ResourceNodeBlueprint.resource_links).selectinload(ResourceNodeBlueprintResource.resource),
                    selectinload(ResourceNodeBlueprint.resource_links).selectinload(ResourceNodeBlueprintResource.theme)
                )
                .offset(skip)
                .limit(limit)
                .order_by(ResourceNodeBlueprint.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            entities = []
            for model in models:
                entity = await self._model_to_entity_with_links(model)
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error finding all blueprints: {e}")
            raise

    # ==============================================================================
    # SPECIALIZED QUERY METHODS
    # ==============================================================================

    async def find_by_name(self, name: str) -> Optional[ResourceNodeEntityPydantic]:
        """Find blueprint by unique name."""
        try:
            stmt = (
                select(ResourceNodeBlueprint)
                .options(
                    selectinload(ResourceNodeBlueprint.resource_links).selectinload(ResourceNodeBlueprintResource.resource),
                    selectinload(ResourceNodeBlueprint.resource_links).selectinload(ResourceNodeBlueprintResource.theme)
                )
                .where(ResourceNodeBlueprint.name == name)
            )
            
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                return await self._model_to_entity_with_links(model)
            return None
            
        except Exception as e:
            logger.error(f"Error finding blueprint by name {name}: {e}")
            raise

    async def find_by_biome_type(self, biome_type: str, skip: int = 0, limit: int = 100) -> List[ResourceNodeEntityPydantic]:
        """Find blueprints by biome type."""
        try:
            stmt = (
                select(ResourceNodeBlueprint)
                .options(
                    selectinload(ResourceNodeBlueprint.resource_links).selectinload(ResourceNodeBlueprintResource.resource),
                    selectinload(ResourceNodeBlueprint.resource_links).selectinload(ResourceNodeBlueprintResource.theme)
                )
                .where(ResourceNodeBlueprint.biome_type == biome_type)
                .offset(skip)
                .limit(limit)
                .order_by(ResourceNodeBlueprint.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            entities = []
            for model in models:
                entity = await self._model_to_entity_with_links(model)
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error finding blueprints by biome type {biome_type}: {e}")
            raise

    async def find_by_status(self, status: StatusEnum, skip: int = 0, limit: int = 100) -> List[ResourceNodeEntityPydantic]:
        """Find blueprints by status."""
        try:
            stmt = (
                select(ResourceNodeBlueprint)
                .options(
                    selectinload(ResourceNodeBlueprint.resource_links).selectinload(ResourceNodeBlueprintResource.resource),
                    selectinload(ResourceNodeBlueprint.resource_links).selectinload(ResourceNodeBlueprintResource.theme)
                )
                .where(ResourceNodeBlueprint.status == status)
                .offset(skip)
                .limit(limit)
                .order_by(ResourceNodeBlueprint.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            entities = []
            for model in models:
                entity = await self._model_to_entity_with_links(model)
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error finding blueprints by status {status}: {e}")
            raise

    async def find_by_resource_id(self, resource_id: UUID, skip: int = 0, limit: int = 100) -> List[ResourceNodeEntityPydantic]:
        """Find blueprints that can yield a specific resource."""
        try:
            stmt = (
                select(ResourceNodeBlueprint)
                .join(ResourceNodeBlueprintResource)
                .options(
                    selectinload(ResourceNodeBlueprint.resource_links).selectinload(ResourceNodeBlueprintResource.resource),
                    selectinload(ResourceNodeBlueprint.resource_links).selectinload(ResourceNodeBlueprintResource.theme)
                )
                .where(ResourceNodeBlueprintResource.resource_id == resource_id)
                .offset(skip)
                .limit(limit)
                .order_by(ResourceNodeBlueprint.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            entities = []
            for model in models:
                entity = await self._model_to_entity_with_links(model)
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error finding blueprints by resource {resource_id}: {e}")
            raise

    async def find_by_world_id(self, world_id: UUID, skip: int = 0, limit: int = 100) -> List[ResourceNodeEntityPydantic]:
        """
        Find blueprints associated with a world through theme relationships.
        This queries blueprints that have resource links with themes belonging to the specified world.
        """
        try:
            # Join through resource links -> themes -> world to find world-associated blueprints
            stmt = (
                select(ResourceNodeBlueprint)
                .join(ResourceNodeBlueprintResource)
                .join(ThemeDB, ResourceNodeBlueprintResource.theme_id == ThemeDB.id)
                .options(
                    selectinload(ResourceNodeBlueprint.resource_links).selectinload(ResourceNodeBlueprintResource.resource),
                    selectinload(ResourceNodeBlueprint.resource_links).selectinload(ResourceNodeBlueprintResource.theme)
                )
                .where(ThemeDB.world_id == world_id)  # Assuming themes have world_id
                .distinct()  # Avoid duplicates if blueprint has multiple theme-linked resources
                .offset(skip)
                .limit(limit)
                .order_by(ResourceNodeBlueprint.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            entities = []
            for model in models:
                entity = await self._model_to_entity_with_links(model)
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error finding blueprints by world {world_id}: {e}")
            # If theme doesn't have world_id or query fails, fall back to getting all blueprints
            logger.warning(f"Falling back to all blueprints due to world query failure: {e}")
            return await self.find_all(skip, limit)

    # ==============================================================================
    # RESOURCE LINK MANAGEMENT
    # ==============================================================================

    async def add_resource_link(
        self, 
        blueprint_id: UUID, 
        resource_id: UUID, 
        link_data: Dict[str, Any]
    ) -> Optional[ResourceNodeEntityPydantic]:
        """Add a resource link to an existing blueprint."""
        try:
            # Check if blueprint exists
            blueprint = await self.db.get(ResourceNodeBlueprint, blueprint_id)
            if not blueprint:
                return None

            # Create new resource link
            link = ResourceNodeBlueprintResource(
                blueprint_id=blueprint_id,
                resource_id=resource_id,
                is_primary=link_data.get('is_primary', True),
                chance=link_data.get('chance', 1.0),
                amount_min=link_data.get('amount_min', 1),
                amount_max=link_data.get('amount_max', 1),
                purity=link_data.get('purity', 1.0),
                rarity=link_data.get('rarity', 'common'),
                theme_id=link_data.get('theme_id'),
                _metadata=link_data.get('metadata', {})
            )

            self.db.add(link)
            await self.db.commit()
            await self.db.refresh(blueprint)

            return await self.find_by_id(blueprint_id)

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error adding resource link to blueprint {blueprint_id}: {e}")
            raise

    async def remove_resource_link(self, blueprint_id: UUID, resource_id: UUID) -> bool:
        """Remove a resource link from a blueprint."""
        try:
            stmt = (
                select(ResourceNodeBlueprintResource)
                .where(
                    and_(
                        ResourceNodeBlueprintResource.blueprint_id == blueprint_id,
                        ResourceNodeBlueprintResource.resource_id == resource_id
                    )
                )
            )
            
            result = await self.db.execute(stmt)
            link = result.scalar_one_or_none()
            
            if link:
                await self.db.delete(link)
                await self.db.commit()
                return True
            
            return False

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error removing resource link from blueprint {blueprint_id}: {e}")
            raise

    # ==============================================================================
    # CONVERSION HELPERS
    # ==============================================================================

    async def _model_to_entity_with_links(self, model: ResourceNodeBlueprint) -> ResourceNodeEntityPydantic:
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
                
                # Add resource details if available
                if link.resource:
                    link_data.update({
                        'resource_name': link.resource.name,
                        'resource_description': link.resource.description,
                        'resource_rarity': link.resource.rarity.value if link.resource.rarity else None,
                        'resource_stack_size': link.resource.stack_size
                    })
                
                # Add theme details if available
                if link.theme:
                    link_data['theme_name'] = link.theme.name
                
                from app.game_state.entities.resource.resource_node_pydantic import ResourceNodeResourceEntityPydantic
                resource_links.append(ResourceNodeResourceEntityPydantic(**link_data))

            # Create entity
            entity_data = {
                'entity_id': model.id,
                'name': model.name,
                'description': model.description,
                'depleted': model.depleted,
                'status': model.status,
                'resource_links': resource_links,
                'created_at': model.created_at,
                'updated_at': model.updated_at,
                'tags': model.tags or [],
                # Map blueprint-specific fields
                'blueprint_id': model.id,  # Self-reference for consistency
                'biome_type': model.biome_type,
            }

            return ResourceNodeEntityPydantic(**entity_data)

        except Exception as e:
            logger.error(f"Error converting model to entity: {e}")
            raise