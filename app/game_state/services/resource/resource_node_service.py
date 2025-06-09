# app/game_state/services/resource_node_service.py

from uuid import UUID, uuid4
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.services.core.base_service import BaseService
from app.game_state.repositories.resource_node_repository import ResourceNodeRepository
from app.game_state.entities.resource.resource_node_pydantic import ResourceNodeEntityPydantic
from app.api.schemas.resource_node_schema import (
    ResourceNodeCreate, 
    ResourceNodeRead, 
    ResourceNodeUpdate,
    ResourceExtractionRequest,
    ResourceExtractionResult
)
from app.game_state.enums.shared import StatusEnum
from app.game_state.enums.resource import ResourceNodeVisibilityEnum


class ResourceNodeService(BaseService[ResourceNodeEntityPydantic, ResourceNodeCreate, ResourceNodeRead]):
    """
    Service layer for ResourceNode instance operations.
    Handles node creation from blueprints, resource extraction, and location-centric operations.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(
            db=db,
            repository=ResourceNodeRepository(db),
            entity_class=ResourceNodeEntityPydantic,
            response_class=ResourceNodeRead
        )

    # ==============================================================================
    # RESOURCE NODE CREATION (from blueprints)
    # ==============================================================================

    async def create_node(self, node_data: ResourceNodeCreate) -> ResourceNodeRead:
        """
        Create a new resource node instance, optionally from a blueprint.
        """
        # Use BaseService creation pattern with node-specific validation
        entity_dict = node_data.model_dump(exclude_unset=True)
        
        # Validation phase using BaseService validation
        await self._validate_creation(entity_dict, ResourceNodeCreate)
        
        # Pre-creation processing for node-specific logic
        await self._pre_create_processing(entity_dict, node_data)
        
        # Generate ID if not provided
        if 'id' not in entity_dict or entity_dict['id'] is None:
            entity_dict['id'] = uuid4()
        
        # Convert to entity and create
        entity = ResourceNodeEntityPydantic.model_validate(entity_dict)
        created_entity = await self.repository.create(entity)
        
        # Post-creation processing (handle blueprint inheritance and resource links)
        await self._post_create_processing(created_entity, node_data)
        
        # Build response with full details
        response = await self._build_node_response(created_entity)
        
        self.logger.info(f"Successfully created ResourceNode {created_entity.id}")
        return response

    async def create_node_from_blueprint(self, location_id: UUID, blueprint_id: UUID, overrides: Optional[Dict[str, Any]] = None) -> ResourceNodeRead:
        """Create a resource node instance from a blueprint."""
        try:
            # Get the blueprint entity from base service
            from app.game_state.services.resource.resource_node_blueprint_service import ResourceNodeBlueprintService
            blueprint_service = ResourceNodeBlueprintService(self.db)
            blueprint_entity = await blueprint_service.find_by_id(blueprint_id)
            
            if not blueprint_entity:
                raise ValueError(f"Blueprint not found: {blueprint_id}")

            # Create node data from blueprint entity
            node_create_data = ResourceNodeCreate(
                name=overrides.get('name', f"{blueprint_entity.name} Instance"),
                description=overrides.get('description', blueprint_entity.description),
                location_id=location_id,
                blueprint_id=blueprint_id,
                status=overrides.get('status', StatusEnum.PENDING),
                visibility=overrides.get('visibility', ResourceNodeVisibilityEnum.HIDDEN),
                depleted=overrides.get('depleted', blueprint_entity.depleted),
                tags=overrides.get('tags', blueprint_entity.tags or []),
                metadata=overrides.get('metadata', {}),
                resource_link_overrides=overrides.get('resource_link_overrides', {})
            )

            return await self.create_node(node_create_data)

        except Exception as e:
            self.logger.error(f"Error creating node from blueprint {blueprint_id}: {e}")
            raise

    # ==============================================================================
    # LOCATION-CENTRIC QUERIES
    # ==============================================================================

    async def get_nodes_by_location(self, location_id: UUID, skip: int = 0, limit: int = 100) -> List[ResourceNodeRead]:
        """Get all resource nodes in a specific location."""
        entities = await self.repository.find_by_location_id(location_id, skip, limit)
        return [await self._build_node_response(entity) for entity in entities]

    async def get_nodes_by_location_and_status(
        self, 
        location_id: UUID, 
        status: StatusEnum, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ResourceNodeRead]:
        """Get resource nodes by location and status."""
        entities = await self.repository.find_by_location_and_status(location_id, status, skip, limit)
        return [await self._build_node_response(entity) for entity in entities]

    async def get_nodes_by_location_and_visibility(
        self, 
        location_id: UUID, 
        visibility: ResourceNodeVisibilityEnum, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ResourceNodeRead]:
        """Get resource nodes by location and visibility."""
        entities = await self.repository.find_by_location_and_visibility(location_id, visibility, skip, limit)
        return [await self._build_node_response(entity) for entity in entities]

    async def get_discovered_nodes_in_location(self, location_id: UUID, skip: int = 0, limit: int = 100) -> List[ResourceNodeRead]:
        """Get discovered resource nodes in a location."""
        return await self.get_nodes_by_location_and_visibility(location_id, ResourceNodeVisibilityEnum.DISCOVERED, skip, limit)

    async def get_active_nodes_in_location(self, location_id: UUID, skip: int = 0, limit: int = 100) -> List[ResourceNodeRead]:
        """Get active (non-depleted) resource nodes in a location."""
        entities = await self.repository.find_by_location_and_status(location_id, StatusEnum.ACTIVE, skip, limit)
        # Filter out depleted nodes
        active_entities = [entity for entity in entities if not entity.depleted]
        return [await self._build_node_response(entity) for entity in active_entities]

    async def get_depleted_nodes_in_location(self, location_id: UUID, skip: int = 0, limit: int = 100) -> List[ResourceNodeRead]:
        """Get depleted resource nodes in a location."""
        entities = await self.repository.find_depleted_in_location(location_id, skip, limit)
        return [await self._build_node_response(entity) for entity in entities]

    # ==============================================================================
    # RESOURCE EXTRACTION OPERATIONS
    # ==============================================================================

    async def extract_resources(
        self, 
        node_id: UUID, 
        extraction_request: ResourceExtractionRequest
    ) -> ResourceExtractionResult:
        """
        Perform resource extraction from a node.
        This simulates the extraction process and updates node state.
        """
        try:
            node_entity = await self.repository.find_by_id(node_id)
            if not node_entity:
                return ResourceExtractionResult(
                    success=False,
                    message=f"Resource node {node_id} not found"
                )

            if node_entity.depleted:
                return ResourceExtractionResult(
                    success=False,
                    message="Resource node is depleted"
                )

            if node_entity.status != StatusEnum.ACTIVE:
                return ResourceExtractionResult(
                    success=False,
                    message=f"Resource node is not active (status: {node_entity.status})"
                )

            # Simulate resource extraction
            extracted_resources = []
            total_extraction_attempts = 0

            for resource_link in node_entity.resource_links:
                total_extraction_attempts += 1
                
                # Calculate extraction chance with modifiers
                base_chance = resource_link.chance
                modified_chance = base_chance * extraction_request.tool_efficiency * extraction_request.character_skill
                modified_chance = min(modified_chance, 1.0)  # Cap at 100%

                # Simulate chance roll
                import random
                if random.random() <= modified_chance:
                    # Calculate extraction amount
                    base_amount = random.randint(resource_link.amount_min, resource_link.amount_max)
                    modified_amount = int(base_amount * extraction_request.tool_efficiency)
                    modified_amount = max(1, modified_amount)  # Minimum 1

                    # Calculate quality
                    base_quality = resource_link.purity
                    modified_quality = min(base_quality * extraction_request.character_skill, 1.0)

                    extracted_resource = {
                        "resource_id": str(resource_link.resource_id),
                        "resource_name": getattr(resource_link, 'resource_name', 'Unknown Resource'),
                        "amount": modified_amount,
                        "quality": round(modified_quality, 2)
                    }
                    extracted_resources.append(extracted_resource)

                    # Update extraction statistics
                    await self.repository.update_extraction_stats(
                        node_id, 
                        resource_link.resource_id, 
                        modified_amount
                    )

            # Check if node should be depleted (simple logic - can be enhanced)
            if total_extraction_attempts > 0 and not extracted_resources:
                # Multiple failed extractions might indicate depletion
                pass  # Could implement depletion logic here

            success = len(extracted_resources) > 0
            message = f"Successfully extracted {len(extracted_resources)} resource types" if success else "No resources extracted"

            return ResourceExtractionResult(
                success=success,
                resources_extracted=extracted_resources,
                node_depleted=False,  # Would need more complex logic
                message=message
            )

        except Exception as e:
            self.logger.error(f"Error extracting resources from node {node_id}: {e}")
            return ResourceExtractionResult(
                success=False,
                message=f"Extraction failed: {str(e)}"
            )

    # ==============================================================================
    # OVERRIDE HOOK METHODS FOR NODE-SPECIFIC LOGIC
    # ==============================================================================

    async def _validate_creation(self, entity_dict: Dict[str, Any], validation_schema=None):
        """Node-specific validation"""
        # Base FK validation handles location_id and blueprint_id validation automatically
        await super()._validate_creation(entity_dict, validation_schema)

    async def _pre_create_processing(self, entity_dict: Dict[str, Any], original_data: ResourceNodeCreate):
        """Node-specific pre-creation processing"""
        try:
            # Validate location exists
            location_id = entity_dict.get('location_id')
            if location_id:
                await self.validator.validate_entity_exists(
                    entity_id=location_id,
                    service_name="location",
                    entity_name="Location"
                )

            # Validate blueprint if provided
            blueprint_id = entity_dict.get('blueprint_id')
            if blueprint_id:
                await self.validator.validate_entity_exists(
                    entity_id=blueprint_id,
                    service_name="resource_node_blueprint",
                    entity_name="ResourceNodeBlueprint"
                )

            # Set default values
            if 'status' not in entity_dict:
                entity_dict['status'] = StatusEnum.PENDING
            
            if 'visibility' not in entity_dict:
                entity_dict['visibility'] = ResourceNodeVisibilityEnum.HIDDEN

            if 'depleted' not in entity_dict:
                entity_dict['depleted'] = False

            if 'tags' not in entity_dict:
                entity_dict['tags'] = []

        except Exception as e:
            self.logger.error(f"Node pre-creation validation failed: {e}")
            raise

    async def _post_create_processing(self, created_entity: ResourceNodeEntityPydantic, original_data: ResourceNodeCreate):
        """Node-specific post-creation processing"""
        self.logger.info(f"Resource node {created_entity.name} created successfully with ID {created_entity.id}")
        
        # Handle blueprint inheritance and resource link creation
        if original_data.blueprint_id:
            await self._inherit_from_blueprint(created_entity, original_data)

    async def _inherit_from_blueprint(self, node_entity: ResourceNodeEntityPydantic, original_data: ResourceNodeCreate):
        """Inherit resource links from blueprint with any overrides."""
        try:
            # Get blueprint details
            from app.game_state.services.resource.resource_node_blueprint_service import ResourceNodeBlueprintService
            blueprint_service = ResourceNodeBlueprintService(self.db)
            blueprint = await blueprint_service.find_by_id(original_data.blueprint_id)
            
            if not blueprint:
                return

            # Create resource links based on blueprint
            overrides = original_data.resource_link_overrides or {}
            
            for blueprint_link in blueprint.resource_links:
                # Apply any overrides for this resource
                resource_overrides = overrides.get(blueprint_link.resource_id, {})
                
                # Create link data with blueprint defaults and overrides
                link_data = {
                    'resource_id': blueprint_link.resource_id,
                    'is_primary': resource_overrides.get('is_primary', blueprint_link.is_primary),
                    'chance': resource_overrides.get('chance', blueprint_link.chance),
                    'amount_min': resource_overrides.get('amount_min', blueprint_link.amount_min),
                    'amount_max': resource_overrides.get('amount_max', blueprint_link.amount_max),
                    'purity': resource_overrides.get('purity', blueprint_link.purity),
                    'rarity': resource_overrides.get('rarity', blueprint_link.rarity),
                    'metadata': resource_overrides.get('metadata', {})
                }

                # Add resource link to node (would need to be implemented in repository)
                # await self.repository.add_resource_link(node_entity.id, blueprint_link.resource_id, link_data)

        except Exception as e:
            self.logger.warning(f"Failed to inherit from blueprint: {e}")

    async def _build_node_response(self, entity: ResourceNodeEntityPydantic) -> ResourceNodeRead:
        """Build detailed node response with statistics."""
        try:
            # Convert entity to base response data
            response_data = entity.model_dump()
            
            # Add node-specific calculations
            total_resources = len(entity.resource_links)
            primary_resources = sum(1 for link in entity.resource_links if link.is_primary)
            secondary_resources = total_resources - primary_resources

            # Calculate extraction statistics
            total_extractions = sum(getattr(link, 'times_extracted', 0) for link in entity.resource_links)
            last_extraction_times = [getattr(link, 'last_extracted_at', None) for link in entity.resource_links if getattr(link, 'last_extracted_at', None)]
            last_extraction_at = max(last_extraction_times) if last_extraction_times else None

            # Build the complete response
            response_data.update({
                'id': entity.id,
                'total_resources': total_resources,
                'primary_resources': primary_resources,
                'secondary_resources': secondary_resources,
                'total_extractions': total_extractions,
                'last_extraction_at': last_extraction_at,
                # Add location and blueprint names if available
                'location_name': getattr(entity, 'location_name', None),
                'blueprint_name': getattr(entity, 'blueprint_name', None),
            })

            return ResourceNodeRead.model_validate(response_data)

        except Exception as e:
            self.logger.error(f"Error building node response: {e}")
            raise

    # ==============================================================================
    # BACKWARD COMPATIBILITY METHODS
    # ==============================================================================

    async def create_resource_node(self, node_data: ResourceNodeCreate) -> ResourceNodeRead:
        """Backward compatibility method"""
        return await self.create_node(node_data)

    async def update_resource_node(self, node_id: UUID, update_data: ResourceNodeUpdate) -> Optional[ResourceNodeRead]:
        """Backward compatibility method"""
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_entity = await self.update_entity(node_id, update_dict)
        if updated_entity:
            return await self._build_node_response(updated_entity)
        return None

    async def delete_resource_node(self, node_id: UUID) -> bool:
        """Backward compatibility method"""
        return await self.delete_entity(node_id)