# app/api/routes/resource_node_routes.py

"""
API routes for Resource Node Instances (Location-Centric Design).
All resource nodes are accessed through their locations.
Handles CRUD operations and resource extraction for node instances.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_async_db
from app.api.schemas.resource_node_schema import (
    ResourceNodeCreate,
    ResourceNodeUpdate,
    ResourceNodeRead,
    ResourceNodeSummary,
    ResourceExtractionRequest,
    ResourceExtractionResult
)
from app.game_state.services.resource.resource_node_service import ResourceNodeService
from app.game_state.enums.shared import StatusEnum
from app.game_state.enums.resource import ResourceNodeVisibilityEnum

router = APIRouter()


@router.get("/locations/{location_id}/resource-nodes/", response_model=List[ResourceNodeSummary])
async def get_location_resource_nodes(
    location_id: UUID,
    status_filter: Optional[StatusEnum] = Query(None, description="Filter by status"),
    visibility_filter: Optional[ResourceNodeVisibilityEnum] = Query(None, description="Filter by visibility"),
    depleted: Optional[bool] = Query(None, description="Filter by depletion status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all resource nodes in a specific location with optional filters."""
    service = ResourceNodeService(db)
    
    try:
        # Apply filters based on query parameters
        if status_filter and visibility_filter:
            # Would need a combined method for this - for now use status filter
            nodes = await service.get_nodes_by_location_and_status(location_id, status_filter, offset, limit)
        elif status_filter:
            nodes = await service.get_nodes_by_location_and_status(location_id, status_filter, offset, limit)
        elif visibility_filter:
            nodes = await service.get_nodes_by_location_and_visibility(location_id, visibility_filter, offset, limit)
        elif depleted is True:
            nodes = await service.get_depleted_nodes_in_location(location_id, offset, limit)
        elif depleted is False:
            nodes = await service.get_active_nodes_in_location(location_id, offset, limit)
        else:
            # Get all nodes in location
            nodes = await service.get_nodes_by_location(location_id, offset, limit)
        
        # Convert to summary format for listing
        summaries = []
        for node in nodes:
            summary = ResourceNodeSummary(
                id=node.id,
                name=node.name,
                description=node.description,
                location_id=node.location_id,
                location_name=node.location_name,
                blueprint_id=node.blueprint_id,
                blueprint_name=node.blueprint_name,
                depleted=node.depleted,
                status=node.status,
                visibility=node.visibility,
                total_resources=node.total_resources,
                primary_resources=node.primary_resources,
                total_extractions=node.total_extractions,
                last_extraction_at=node.last_extraction_at,
                created_at=node.created_at
            )
            summaries.append(summary)
        
        return summaries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving resource nodes for location {location_id}: {str(e)}"
        )


@router.get("/locations/{location_id}/resource-nodes/{node_id}", response_model=ResourceNodeRead)
async def get_location_resource_node(
    location_id: UUID,
    node_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific resource node in a location with full details."""
    service = ResourceNodeService(db)
    
    try:
        node = await service.find_by_id(node_id)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource node with ID {node_id} not found"
            )
        
        # Verify the node belongs to the specified location
        if node.location_id != location_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource node {node_id} not found in location {location_id}"
            )
        
        return node
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving resource node: {str(e)}"
        )


@router.post("/locations/{location_id}/resource-nodes/", response_model=ResourceNodeRead, status_code=status.HTTP_201_CREATED)
async def create_location_resource_node(
    location_id: UUID,
    node_data: ResourceNodeCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new resource node in a location."""
    service = ResourceNodeService(db)
    
    try:
        # Ensure the location_id in the URL matches the data
        node_data.location_id = location_id
        
        node = await service.create_node(node_data)
        return node
        
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
            detail=f"Error creating resource node: {str(e)}"
        )


@router.post("/locations/{location_id}/resource-nodes/from-blueprint/{blueprint_id}", response_model=ResourceNodeRead, status_code=status.HTTP_201_CREATED)
async def create_resource_node_from_blueprint(
    location_id: UUID,
    blueprint_id: UUID,
    overrides: Optional[Dict[str, Any]] = Body(None, description="Optional overrides for blueprint defaults"),
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new resource node from a blueprint."""
    service = ResourceNodeService(db)
    
    try:
        node = await service.create_node_from_blueprint(location_id, blueprint_id, overrides)
        return node
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating resource node from blueprint: {str(e)}"
        )


@router.patch("/locations/{location_id}/resource-nodes/{node_id}", response_model=ResourceNodeRead)
async def update_location_resource_node(
    location_id: UUID,
    node_id: UUID,
    node_data: ResourceNodeUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update a resource node in a location."""
    service = ResourceNodeService(db)
    
    try:
        # Verify the node exists and belongs to the location
        existing_node = await service.find_by_id(node_id)
        if not existing_node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource node with ID {node_id} not found"
            )
        
        if existing_node.location_id != location_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource node {node_id} not found in location {location_id}"
            )
        
        updated_node = await service.update_resource_node(node_id, node_data)
        if not updated_node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource node with ID {node_id} not found"
            )
        
        return updated_node
        
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
            detail=f"Error updating resource node: {str(e)}"
        )


@router.delete("/locations/{location_id}/resource-nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location_resource_node(
    location_id: UUID,
    node_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a resource node from a location."""
    service = ResourceNodeService(db)
    
    try:
        # Verify the node exists and belongs to the location
        existing_node = await service.find_by_id(node_id)
        if not existing_node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource node with ID {node_id} not found"
            )
        
        if existing_node.location_id != location_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource node {node_id} not found in location {location_id}"
            )
        
        success = await service.delete_resource_node(node_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource node with ID {node_id} not found"
            )
        
        # Return 204 No Content on successful deletion
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting resource node: {str(e)}"
        )


# ==============================================================================
# RESOURCE EXTRACTION ROUTES
# ==============================================================================

@router.post("/locations/{location_id}/resource-nodes/{node_id}/extract", response_model=ResourceExtractionResult)
async def extract_resources_from_node(
    location_id: UUID,
    node_id: UUID,
    extraction_request: ResourceExtractionRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Perform resource extraction from a node."""
    service = ResourceNodeService(db)
    
    try:
        # Verify the node exists and belongs to the location
        existing_node = await service.find_by_id(node_id)
        if not existing_node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource node with ID {node_id} not found"
            )
        
        if existing_node.location_id != location_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource node {node_id} not found in location {location_id}"
            )
        
        result = await service.extract_resources(node_id, extraction_request)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting resources: {str(e)}"
        )


# ==============================================================================
# DISCOVERY AND STATUS ROUTES
# ==============================================================================

@router.post("/locations/{location_id}/resource-nodes/{node_id}/discover", response_model=ResourceNodeRead)
async def discover_resource_node(
    location_id: UUID,
    node_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Mark a resource node as discovered."""
    service = ResourceNodeService(db)
    
    try:
        # Verify the node exists and belongs to the location
        existing_node = await service.find_by_id(node_id)
        if not existing_node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource node with ID {node_id} not found"
            )
        
        if existing_node.location_id != location_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource node {node_id} not found in location {location_id}"
            )
        
        # Update to discovered
        update_data = ResourceNodeUpdate(visibility=ResourceNodeVisibilityEnum.DISCOVERED)
        updated_node = await service.update_resource_node(node_id, update_data)
        
        return updated_node
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error discovering resource node: {str(e)}"
        )


@router.post("/locations/{location_id}/resource-nodes/{node_id}/deplete", response_model=ResourceNodeRead)
async def deplete_resource_node(
    location_id: UUID,
    node_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Mark a resource node as depleted."""
    service = ResourceNodeService(db)
    
    try:
        # Verify the node exists and belongs to the location
        existing_node = await service.find_by_id(node_id)
        if not existing_node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource node with ID {node_id} not found"
            )
        
        if existing_node.location_id != location_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource node {node_id} not found in location {location_id}"
            )
        
        # Update to depleted
        update_data = ResourceNodeUpdate(depleted=True, status=StatusEnum.INACTIVE)
        updated_node = await service.update_resource_node(node_id, update_data)
        
        return updated_node
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error depleting resource node: {str(e)}"
        )


# ==============================================================================
# SPECIALIZED QUERY ROUTES
# ==============================================================================

@router.get("/locations/{location_id}/resource-nodes/discovered", response_model=List[ResourceNodeSummary])
async def get_discovered_resource_nodes(
    location_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all discovered resource nodes in a location."""
    service = ResourceNodeService(db)
    
    try:
        nodes = await service.get_discovered_nodes_in_location(location_id, offset, limit)
        
        summaries = []
        for node in nodes:
            summary = ResourceNodeSummary(
                id=node.id,
                name=node.name,
                description=node.description,
                location_id=node.location_id,
                location_name=node.location_name,
                blueprint_id=node.blueprint_id,
                blueprint_name=node.blueprint_name,
                depleted=node.depleted,
                status=node.status,
                visibility=node.visibility,
                total_resources=node.total_resources,
                primary_resources=node.primary_resources,
                total_extractions=node.total_extractions,
                last_extraction_at=node.last_extraction_at,
                created_at=node.created_at
            )
            summaries.append(summary)
        
        return summaries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving discovered nodes: {str(e)}"
        )


@router.get("/locations/{location_id}/resource-nodes/active", response_model=List[ResourceNodeSummary])
async def get_active_resource_nodes(
    location_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all active (non-depleted) resource nodes in a location."""
    service = ResourceNodeService(db)
    
    try:
        nodes = await service.get_active_nodes_in_location(location_id, offset, limit)
        
        summaries = []
        for node in nodes:
            summary = ResourceNodeSummary(
                id=node.id,
                name=node.name,
                description=node.description,
                location_id=node.location_id,
                location_name=node.location_name,
                blueprint_id=node.blueprint_id,
                blueprint_name=node.blueprint_name,
                depleted=node.depleted,
                status=node.status,
                visibility=node.visibility,
                total_resources=node.total_resources,
                primary_resources=node.primary_resources,
                total_extractions=node.total_extractions,
                last_extraction_at=node.last_extraction_at,
                created_at=node.created_at
            )
            summaries.append(summary)
        
        return summaries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving active nodes: {str(e)}"
        )