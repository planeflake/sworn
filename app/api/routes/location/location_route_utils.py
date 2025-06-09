"""
API utils for location routes.
"""

from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.location_type import LocationType

from app.api.schemas.location import (
    LocationResponse,
    Reference,
    BuildingResponse,
    BuildingUpgradeResponse,
    ResourceResponse,
    ResourceNodeResponse,
    TravelConnectionResponse
)
from app.game_state.services.geography.location_service import LocationService
from app.db.models.travel_link import TravelLink
from app.db.models.building_instance import BuildingInstanceDB
from app.db.models.resources.resource_instance import ResourceInstance
from app.db.models.resources.resource_node import ResourceNode
from app.db.models.biome import Biome


async def build_location_response(location, location_service: LocationService) -> LocationResponse:
    """Convert location entity to comprehensive LocationResponse with all related data."""
    
    # Build basic location sub-type response if available
    location_sub_type = None
    if hasattr(location, 'location_sub_type') and location.location_sub_type:
        # For now, create a simple subtype reference
        # In the future, this could be a proper LocationSubType entity
        location_sub_type = Reference(
            id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder
            name=location.location_sub_type
        )
    
    # Get database session from the service
    db = location_service.db
    
    # Fetch all related data using the correct field name (location.id)
    buildings = await fetch_location_buildings(db, location.id)
    resources = await fetch_location_resources(db, location.id)
    resource_nodes = await fetch_location_resource_nodes(db, location.id)
    travel_connections = await fetch_travel_connections(db, location.id)
    
    # Build all reference objects
    location_type_ref = await fetch_location_type_reference(db, location.location_type_id)
    
    # Build theme reference
    theme_ref = None
    if getattr(location, 'theme_id', None):
        theme_ref = await fetch_theme_reference(db, location.theme_id)
    
    # Build world reference  
    world_ref = None
    if getattr(location, 'world_id', None):
        world_ref = await fetch_world_reference(db, location.world_id)
    
    # Build biome reference
    biome_ref = None
    if getattr(location, 'biome_id', None):
        biome_ref = await fetch_biome_reference(db, location.biome_id)
    
    # Build parent reference
    parent_ref = None
    if getattr(location, 'parent_id', None):
        parent_ref = await fetch_parent_reference(db, location.parent_id)
    
    # Build the response with new fields
    response = LocationResponse(
        id=location.id,
        name=location.name,
        description=location.description,
        location_sub_type=location_sub_type,
        location_type=location_type_ref,
        theme=theme_ref,
        world=world_ref,
        biome=biome_ref,
        type_id=location.location_type_id,
        type_code=getattr(location_type_ref, 'code', None),
        type=getattr(location_type_ref, 'name', None),
        parent_id=getattr(location, 'parent_id', None),
        parent_type=None,  # TODO: implement parent type logic
        parent=parent_ref,
        coordinates=getattr(location, 'coordinates', {}),
        attributes=getattr(location, 'attributes', {}),
        tags=getattr(location, 'tags', []),
        is_active=getattr(location, 'is_active', True),
        created_at=location.created_at,
        updated_at=location.updated_at.isoformat() if location.updated_at else None,
        buildings=buildings,
        resources=resources,
        resource_nodes=resource_nodes,
        travel_connections=travel_connections
    )

    return response


async def fetch_location_type_reference(db: AsyncSession, location_type_id: UUID) -> Reference:
    """Fetch location type reference data."""
    try:
        stmt = select(LocationType).where(LocationType.id == location_type_id)
        result = await db.execute(stmt)
        location_type = result.scalar_one_or_none()
        
        if not location_type:
            return Reference(
                id=location_type_id,
                name="Unknown Type",
                code="unknown"
            )
        
        return Reference(
            id=location_type.id,
            name=location_type.name,
            code=location_type.code
        )
    except Exception as e:
        # Return a fallback reference if database query fails
        return Reference(
            id=location_type_id,
            name="Unknown Type",
            code="unknown"
        )


async def fetch_theme_reference(db: AsyncSession, theme_id: UUID) -> Reference:
    """Fetch theme reference data."""
    try:
        from app.db.models.theme import ThemeDB
        stmt = select(ThemeDB).where(ThemeDB.id == theme_id)
        result = await db.execute(stmt)
        theme = result.scalar_one_or_none()
        
        if not theme:
            return Reference(id=theme_id, name="Unknown Theme")
        
        return Reference(id=theme.id, name=theme.name)
    except Exception:
        return Reference(id=theme_id, name="Unknown Theme")


async def fetch_world_reference(db: AsyncSession, world_id: UUID) -> Reference:
    """Fetch world reference data."""
    try:
        from app.db.models.world import World
        stmt = select(World).where(World.id == world_id)
        result = await db.execute(stmt)
        world = result.scalar_one_or_none()
        
        if not world:
            return Reference(id=world_id, name="Unknown World")
        
        return Reference(id=world.id, name=world.name)
    except Exception:
        return Reference(id=world_id, name="Unknown World")


async def fetch_biome_reference(db: AsyncSession, biome_id: UUID) -> Reference:
    """Fetch biome reference data."""
    try:
        stmt = select(Biome).where(Biome.id == biome_id)
        result = await db.execute(stmt)
        biome = result.scalar_one_or_none()
        
        if not biome:
            return Reference(id=biome_id, name="Unknown Biome")
        
        return Reference(id=biome.id, name=biome.name)
    except Exception:
        return Reference(id=biome_id, name="Unknown Biome")


async def fetch_parent_reference(db: AsyncSession, parent_id: UUID) -> Reference:
    """Fetch parent location reference data."""
    try:
        from app.db.models.location_instance import LocationInstance
        stmt = select(LocationInstance).where(LocationInstance.id == parent_id)
        result = await db.execute(stmt)
        parent = result.scalar_one_or_none()
        
        if not parent:
            return Reference(id=parent_id, name="Unknown Location")
        
        return Reference(id=parent.id, name=parent.name)
    except Exception:
        return Reference(id=parent_id, name="Unknown Location")


async def fetch_location_buildings(db: AsyncSession, location_id: UUID) -> List[BuildingResponse]:
    """Fetch buildings for a location."""
    from app.db.models.building_upgrade_blueprint import BuildingUpgradeBlueprint
    
    # First check if the building table has a location_id column
    # If not, we'll return empty list for now
    try:
        stmt = select(BuildingInstanceDB).where(BuildingInstanceDB.settlement_id == location_id)
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
                BuildingUpgradeBlueprint.parent_blueprint_id == building.building_blueprint_id
            )
            upgrade_result = await db.execute(upgrade_stmt)
            upgrade_blueprints = upgrade_result.scalars().all()
            
            for upgrade in upgrade_blueprints:
                upgrades.append(BuildingUpgradeResponse(
                    id=upgrade.id,
                    name=upgrade.name or "Upgrade",
                    resources=upgrade.resource_cost or [],
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
                resource_id=resource.resource_id,
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
                biomes = [Reference(id=b.id, name=b.name) for b in biome_records]
            
            # Fetch factions along the route
            factions = []
            if hasattr(link, 'faction_ids') and link.faction_ids:
                faction_stmt = select(Faction).where(Faction.id.in_(link.faction_ids))
                faction_result = await db.execute(faction_stmt)
                faction_records = faction_result.scalars().all()
                factions = [Reference(id=f.id, name=f.name) for f in faction_records]
            
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