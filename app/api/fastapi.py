from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import fastapi_swagger_dark as fsd

# your routers
from app.api.routes.world_routes import router as world_router
from app.api.routes.theme_routes import router as theme_router
from app.api.routes.settlement_routes import router as settlement_router
from app.api.routes.character_routes import router as character_router
from app.api.routes.resource_routes import router as resource_router
from app.api.routes.profession_routes import router as profession_router
from app.api.routes.skill_definition_routes import router as skill_definition_router
from app.api.routes.building_instance_routes import router as building_instance_router
from app.api.routes.building_blueprint_routes import router as building_blueprint_router
from app.api.routes.building_upgrade_blueprint_routes import router as building_upgrade_blueprint_router
from app.api.routes.biome_routes import router as biome_router
from app.api.routes.zone_routes import router as zone_router
from app.api.routes.location import location_type_router, location_router
from app.api.routes.action_routes import router as action_router
from app.api.routes.action_template_routes import router as action_template_router
from app.api.routes.tool_tier_routes import router as tool_tier_router
from app.api.routes.location.location_sub_types import router as location_sub_types_router
from app.api.routes.resource_node_blueprint_routes import router as resource_node_blueprint_router
from app.api.routes.resource_node_routes import router as resource_node_router
from app.api.routes.faction_routes import router as faction_router

#from app.api.routes.building_routes import router as building_router
#from app.api.routes.item_routes import router as item_router

fastapi = FastAPI(
    docs_url=None,  # Disable default docs URL|
    redoc_url=None,
    #swagger_ui_parameters=swagger_ui_params,
)

# install the dark-mode plugin on the app
fsd.install(fastapi)

# CORS
fastapi.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve local static files if you ever switch to a local CSS
# app.mount("/static", StaticFiles(directory="static"), name="static")

# include all your routers
fastapi.include_router(world_router,      prefix="/api/v1/worlds", tags=["World"])
fastapi.include_router(theme_router,      prefix="/api/v1/themes", tags=["Theme"])
fastapi.include_router(settlement_router, prefix="/api/v1/settlements", tags=["Settlement"])
fastapi.include_router(character_router,  prefix="/api/v1/characters", tags=["Character"])
fastapi.include_router(resource_router,   prefix="/api/v1/resources", tags=["Resource"])
fastapi.include_router(profession_router, prefix="/api/v1/professions", tags=["Profession"])
fastapi.include_router(skill_definition_router, prefix="/api/v1/skills", tags=["Skill"])
fastapi.include_router(building_instance_router, prefix="/api/v1/buildings", tags=["Buildings"])
fastapi.include_router(building_blueprint_router, prefix="/api/v1/building-blueprints", tags=["Building Blueprints"])
fastapi.include_router(building_upgrade_blueprint_router, prefix="/api/v1/building-upgrade-blueprints", tags=["Building Upgrade Blueprints"])
fastapi.include_router(biome_router, prefix="/api/v1/biomes", tags=["Biomes"])
fastapi.include_router(zone_router, prefix="/api/v1/zones", tags=["Zones"])
fastapi.include_router(location_type_router, prefix="/api/v1/location-types", tags=["Location Types"])
fastapi.include_router(location_router, prefix="/api/v1/locations", tags=["Locations"])
fastapi.include_router(action_router, prefix="/api/v1", tags=["Actions"])
fastapi.include_router(action_template_router, prefix="/api/v1/action-templates", tags=["Action Templates"])
fastapi.include_router(tool_tier_router, prefix="/api/v1/tool-tiers", tags=["Tool Tiers"])
#app.include_router(building_router,   prefix="/api/v1", tags=["building"])
#app.include_router(item_router,       prefix="/api/v1", tags=["item"])
fastapi.include_router(location_sub_types_router, prefix="/api/v1/location-subtypes", tags=["Location Subtypes"])
fastapi.include_router(resource_node_blueprint_router, prefix="/api/v1/resource-node-blueprints", tags=["Resource Node Blueprints"])
fastapi.include_router(resource_node_router, prefix="/api/v1", tags=["Resource Nodes"])
fastapi.include_router(faction_router, prefix="/api/v1", tags=["Factions"])

@fastapi.get("/status")
def status():
    """Check the status of the API"""
    return {"status": 200}
