"""
API utils for location routes.
"""

from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.schemas.location import (
    LocationResponse,
    LocationSubTypeResponse,
    ThemeReference,
    BiomeReference,
    FactionReference,
    BuildingResponse,
    BuildingUpgradeResponse,
    ResourceResponse,
    ResourceNodeResponse,
    TravelConnectionResponse
)
from app.game_state.services.location.location_service import LocationService
from app.db.models.travel_link import TravelLink
from app.db.models.building_instance import BuildingInstanceDB
from app.db.models.resources.resource_instance import ResourceInstance
from app.db.models.resources.resource_node import ResourceNode


async def build_location_response(location, location_service: LocationService) -> LocationResponse:
    """Convert location entity to comprehensive LocationResponse with all related data."""
    
    # Build basic location sub-type response if available
    location_sub_type = None
    if hasattr(location, 'location_sub_type') and location.location_sub_type:
        # For now, create a simple sub-type reference
        # In the future, this could be a proper LocationSubType entity
        location_sub_type = LocationSubTypeResponse(
            id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder
            name=location.location_sub_type
        )
    
    # Get database session from the service
    db = location_service.db
    
    # Fetch all related data
    buildings = await fetch_location_buildings(db, location.entity_id)
    resources = await fetch_location_resources(db, location.entity_id)
    resource_nodes = await fetch_location_resource_nodes(db, location.entity_id)
    travel_connections = await fetch_travel_connections(db, location.entity_id)
    
    # Build the response with new fields
    response = LocationResponse(
        id=location.entity_id,
        name=location.name,
        description=location.description,
        location_type_id=location.location_type_id,
        location_sub_type=location_sub_type,
        theme_id=getattr(location, 'theme_id', None),
        parent_id=location.parent.location_id if location.parent else None,
        biome_id=getattr(location, 'biome_id', None),
        coordinates=location.coordinates,
        attributes=location.attributes,
        tags=location.tags,
        is_active=location.is_active,
        created_at=location.created_at.isoformat() if location.created_at else "",
        updated_at=location.updated_at.isoformat() if location.updated_at else None,
        buildings=buildings,
        resources=resources,
        resource_nodes=resource_nodes,
        travel_connections=travel_connections
    )

    return response


async def fetch_location_buildings(db: AsyncSession, location_id: UUID) -> List[BuildingResponse]:
    """Fetch buildings for a location."""
    from app.db.models.building_upgrade_blueprint import BuildingUpgradeBlueprint
    
    # First check if the building table has a location_id column
    # If not, we'll return empty list for now
    try:
        stmt = select(BuildingInstanceDB).where(BuildingInstanceDB.location_id == location_id)
        result = await db.execute(stmt)
        buildings = result.scalars().all()
    except Exception:
        # Column doesn't exist yet, return empty list
        return []
    
    building_responses = []
    for building in buildings:
        # Fetch upgrade options for this building
        upgrades = []
        try:
            upgrade_stmt = select(BuildingUpgradeBlueprint).where(
                BuildingUpgradeBlueprint.building_blueprint_id == building.building_blueprint_id
            )
            upgrade_result = await db.execute(upgrade_stmt)
            upgrade_blueprints = upgrade_result.scalars().all()
            
            for upgrade in upgrade_blueprints:
                upgrades.append(BuildingUpgradeResponse(
                    id=upgrade.id,
                    name=upgrade.name or "Upgrade",
                    resources=upgrade.resource_costs or [],
                    bonus=upgrade.effects or {}
                ))
        except Exception:
            # Upgrade system might not be fully implemented yet
            pass
        
        building_responses.append(BuildingResponse(
            building_id=building.id,
            name=building.name or "Unknown Building",
            building_type=getattr(building, 'building_type', 'unknown'),
            level=getattr(building, 'level', 1),
            status=getattr(building, 'status', 'functional'),
            upgrades=upgrades
        ))
    
    return building_responses


async def fetch_location_resources(db: AsyncSession, location_id: UUID) -> List[ResourceResponse]:
    """Fetch stored resources for a location."""
    try:
        stmt = select(ResourceInstance).where(ResourceInstance.location_id == location_id)
        result = await db.execute(stmt)
        resources = result.scalars().all()
        
        resource_responses = []
        for resource in resources:
            resource_responses.append(ResourceResponse(
                resource_id=resource.resource_blueprint_id,
                name=resource.resource_blueprint.name if hasattr(resource, 'resource_blueprint') and resource.resource_blueprint else "Unknown Resource",
                quantity=getattr(resource, 'quantity', 0),
                unit=getattr(resource, 'unit', 'units')
            ))
        
        return resource_responses
    except Exception:
        # Table might not have location_id column yet
        return []


async def fetch_location_resource_nodes(db: AsyncSession, location_id: UUID) -> List[ResourceNodeResponse]:
    """Fetch resource nodes for a location."""
    try:
        stmt = select(ResourceNode).where(ResourceNode.location_id == location_id)
        result = await db.execute(stmt)
        nodes = result.scalars().all()
        
        node_responses = []
        for node in nodes:
            node_responses.append(ResourceNodeResponse(
                node_id=node.id,
                resource_id=getattr(node, 'resource_blueprint_id', node.id),
                name=getattr(node, 'name', 'Resource Node'),
                extraction_rate=getattr(node, 'current_extraction_rate', 0),
                max_extraction_rate=getattr(node, 'max_extraction_rate', 0),
                unit=f"{node.resource_blueprint.base_unit}/day" if hasattr(node, 'resource_blueprint') and node.resource_blueprint else "units/day",
                depleted=getattr(node, 'is_depleted', False)
            ))
        
        return node_responses
    except Exception:
        # Table might not have location_id column yet
        return []


async def fetch_travel_connections(db: AsyncSession, location_id: UUID) -> List[TravelConnectionResponse]:
    """Fetch travel connections from a location."""
    from app.db.models.biome import Biome
    from app.db.models.faction import Faction
    
    try:
        stmt = select(TravelLink).where(TravelLink.from_location_id == location_id)
        result = await db.execute(stmt)
        links = result.scalars().all()
        
        connection_responses = []
        for link in links:
            # Fetch biomes along the route
            biomes = []
            if hasattr(link, 'biome_ids') and link.biome_ids:
                biome_stmt = select(Biome).where(Biome.id.in_(link.biome_ids))
                biome_result = await db.execute(biome_stmt)
                biome_records = biome_result.scalars().all()
                biomes = [BiomeReference(id=b.id, name=b.name) for b in biome_records]
            
            # Fetch factions along the route
            factions = []
            if hasattr(link, 'faction_ids') and link.faction_ids:
                faction_stmt = select(Faction).where(Faction.id.in_(link.faction_ids))
                faction_result = await db.execute(faction_stmt)
                faction_records = faction_result.scalars().all()
                factions = [FactionReference(id=f.id, name=f.name) for f in faction_records]
            
            # Calculate dynamic danger level
            # For now, use base danger level - this can be enhanced with character-specific calculations
            danger_level = getattr(link, 'base_danger_level', 1)
            
            connection_responses.append(TravelConnectionResponse(
                travel_link_id=link.id,
                name=link.name,
                biomes=biomes,
                factions=factions,
                speed=link.speed,
                path_type=link.path_type,
                terrain_modifier=link.terrain_modifier,
                danger_level=danger_level,
                visibility=link.visibility
            ))
        
        return connection_responses
    except Exception:
        # TravelLink table might not exist yet
        return []