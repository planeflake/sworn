# app/api/routes/resource_node_blueprint_routes.py

"""
API routes for Resource Node Blueprints.
Handles CRUD operations and resource link management for blueprint templates.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_async_db
from app.api.schemas.resource_node_blueprint_schema import (
    ResourceNodeBlueprintCreate,
    ResourceNodeBlueprintUpdate,
    ResourceNodeBlueprintRead,
    ResourceNodeBlueprintSummary,
    ResourceLinkCreate
)
from app.game_state.services.resource.resource_node_blueprint_service import ResourceNodeBlueprintService
from app.game_state.enums.shared import StatusEnum

router = APIRouter()


@router.get("/", response_model=List[ResourceNodeBlueprintSummary])
async def get_resource_node_blueprints(
    biome_type: Optional[str] = Query(None, description="Filter by biome type"),
    status: Optional[StatusEnum] = Query(None, description="Filter by status"),
    resource_id: Optional[UUID] = Query(None, description="Filter by resource that can be yielded"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get resource node blueprints with optional filters."""
    service = ResourceNodeBlueprintService(db)
    
    try:
        if resource_id:
            blueprints = await service.get_blueprints_by_resource(resource_id, offset, limit)
        elif biome_type:
            blueprints = await service.get_blueprints_by_biome(biome_type, offset, limit)
        elif status:
            blueprints = await service.get_blueprints_by_status(status, offset, limit)
        else:
            # Get all blueprints
            blueprints = await service.find_all(offset, limit)
        
        # Convert to summary format for listing
        summaries = []
        for blueprint in blueprints:
            summary = ResourceNodeBlueprintSummary(
                id=blueprint.id,
                name=blueprint.name,
                description=blueprint.description,
                biome_type=blueprint.biome_type,
                status=blueprint.status,
                total_resources=blueprint.total_resources,
                primary_resources=blueprint.primary_resources,
                created_at=blueprint.created_at
            )
            summaries.append(summary)
        
        return summaries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving blueprints: {str(e)}"
        )


@router.get("/{blueprint_id}", response_model=ResourceNodeBlueprintRead)
async def get_resource_node_blueprint(
    blueprint_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific resource node blueprint with full details."""
    service = ResourceNodeBlueprintService(db)
    
    try:
        blueprint = await service.find_by_id(blueprint_id)
        if not blueprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blueprint with ID {blueprint_id} not found"
            )
        
        return blueprint
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving blueprint: {str(e)}"
        )


@router.get("/name/{blueprint_name}", response_model=ResourceNodeBlueprintRead)
async def get_resource_node_blueprint_by_name(
    blueprint_name: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a resource node blueprint by unique name."""
    service = ResourceNodeBlueprintService(db)
    
    try:
        blueprint = await service.get_blueprint_by_name(blueprint_name)
        if not blueprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blueprint with name '{blueprint_name}' not found"
            )
        
        return blueprint
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving blueprint by name: {str(e)}"
        )


@router.post("/", response_model=ResourceNodeBlueprintRead, status_code=status.HTTP_201_CREATED)
async def create_resource_node_blueprint(
    blueprint_data: ResourceNodeBlueprintCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new resource node blueprint."""
    service = ResourceNodeBlueprintService(db)
    
    try:
        blueprint = await service.create_blueprint(blueprint_data)
        return blueprint
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating blueprint: {str(e)}"
        )


@router.patch("/{blueprint_id}", response_model=ResourceNodeBlueprintRead)
async def update_resource_node_blueprint(
    blueprint_id: UUID,
    blueprint_data: ResourceNodeBlueprintUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update an existing resource node blueprint."""
    service = ResourceNodeBlueprintService(db)
    
    try:
        blueprint = await service.update_resource_node_blueprint(blueprint_id, blueprint_data)
        if not blueprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blueprint with ID {blueprint_id} not found"
            )
        
        return blueprint
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating blueprint: {str(e)}"
        )


@router.delete("/{blueprint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource_node_blueprint(
    blueprint_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a resource node blueprint."""
    service = ResourceNodeBlueprintService(db)
    
    try:
        success = await service.delete_resource_node_blueprint(blueprint_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blueprint with ID {blueprint_id} not found"
            )
        
        # Return 204 No Content on successful deletion
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting blueprint: {str(e)}"
        )


# ==============================================================================
# RESOURCE LINK MANAGEMENT ROUTES
# ==============================================================================

@router.post("/{blueprint_id}/resources", response_model=ResourceNodeBlueprintRead)
async def add_resource_to_blueprint(
    blueprint_id: UUID,
    resource_link: ResourceLinkCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Add a resource link to an existing blueprint."""
    service = ResourceNodeBlueprintService(db)
    
    try:
        blueprint = await service.add_resource_to_blueprint(blueprint_id, resource_link)
        if not blueprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blueprint with ID {blueprint_id} not found"
            )
        
        return blueprint
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding resource to blueprint: {str(e)}"
        )


@router.delete("/{blueprint_id}/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_resource_from_blueprint(
    blueprint_id: UUID,
    resource_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Remove a resource link from a blueprint."""
    service = ResourceNodeBlueprintService(db)
    
    try:
        success = await service.remove_resource_from_blueprint(blueprint_id, resource_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource link not found for blueprint {blueprint_id} and resource {resource_id}"
            )
        
        # Return 204 No Content on successful deletion
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing resource from blueprint: {str(e)}"
        )


# ==============================================================================
# ADMINISTRATIVE AND SPECIALIZED QUERY ROUTES
# ==============================================================================

@router.get("/admin/all", response_model=List[ResourceNodeBlueprintRead])
async def get_all_blueprints_admin(
    limit: int = Query(1000, ge=1, le=5000, description="Maximum number of results (higher limit for admin)"),
    offset: int = Query(0, ge=0),
    include_inactive: bool = Query(False, description="Include inactive/disabled blueprints"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Administrative route to get all blueprints with full details.
    Higher limits and includes inactive blueprints when requested.
    """
    service = ResourceNodeBlueprintService(db)
    
    try:
        if include_inactive:
            # Get all blueprints regardless of status
            blueprints = await service.find_all(offset, limit)
        else:
            # Get only active blueprints
            blueprints = await service.get_blueprints_by_status(StatusEnum.ACTIVE, offset, limit)
        
        return blueprints
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving all blueprints: {str(e)}"
        )


@router.get("/world/{world_id}", response_model=List[ResourceNodeBlueprintSummary])
async def get_blueprints_by_world(
    world_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get blueprints associated with a specific world.
    This finds blueprints through theme associations in resource links.
    """
    service = ResourceNodeBlueprintService(db)
    
    try:
        blueprints = await service.get_blueprints_by_world(world_id, offset, limit)
        
        # Convert to summary format
        summaries = []
        for blueprint in blueprints:
            summary = ResourceNodeBlueprintSummary(
                id=blueprint.id,
                name=blueprint.name,
                description=blueprint.description,
                biome_type=blueprint.biome_type,
                status=blueprint.status,
                total_resources=blueprint.total_resources,
                primary_resources=blueprint.primary_resources,
                created_at=blueprint.created_at
            )
            summaries.append(summary)
        
        return summaries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving blueprints for world {world_id}: {str(e)}"
        )


# ==============================================================================
# SPECIALIZED QUERY ROUTES
# ==============================================================================

@router.get("/biome/{biome_type}", response_model=List[ResourceNodeBlueprintSummary])
async def get_blueprints_by_biome(
    biome_type: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all blueprints for a specific biome type."""
    service = ResourceNodeBlueprintService(db)
    
    try:
        blueprints = await service.get_blueprints_by_biome(biome_type, offset, limit)
        
        # Convert to summary format
        summaries = []
        for blueprint in blueprints:
            summary = ResourceNodeBlueprintSummary(
                id=blueprint.id,
                name=blueprint.name,
                description=blueprint.description,
                biome_type=blueprint.biome_type,
                status=blueprint.status,
                total_resources=blueprint.total_resources,
                primary_resources=blueprint.primary_resources,
                created_at=blueprint.created_at
            )
            summaries.append(summary)
        
        return summaries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving blueprints for biome {biome_type}: {str(e)}"
        )


@router.get("/resource/{resource_id}/blueprints", response_model=List[ResourceNodeBlueprintSummary])
async def get_blueprints_yielding_resource(
    resource_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all blueprints that can yield a specific resource."""
    service = ResourceNodeBlueprintService(db)
    
    try:
        blueprints = await service.get_blueprints_by_resource(resource_id, offset, limit)
        
        # Convert to summary format
        summaries = []
        for blueprint in blueprints:
            summary = ResourceNodeBlueprintSummary(
                id=blueprint.id,
                name=blueprint.name,
                description=blueprint.description,
                biome_type=blueprint.biome_type,
                status=blueprint.status,
                total_resources=blueprint.total_resources,
                primary_resources=blueprint.primary_resources,
                created_at=blueprint.created_at
            )
            summaries.append(summary)
        
        return summaries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving blueprints for resource {resource_id}: {str(e)}"
        )