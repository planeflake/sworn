"""
Location schemas package.
"""
from app.api.schemas.location.location_type_schema import (
    AttributeDefinition,
    LocationTypeBase,
    LocationTypeCreate,
    LocationTypeUpdate,
    LocationTypeResponse
)
from app.api.schemas.location.location_schema import (
    LocationBase,
    LocationCreate,
    LocationUpdate,
    LocationReference,
    LocationResponse,
    LocationSubTypeResponse,
    ThemeReference,
    BiomeReference,
    FactionReference,
    BuildingResponse,
    BuildingUpgradeResponse,
    ResourceResponse,
    ResourceNodeResponse,
    TravelConnectionResponse,

)