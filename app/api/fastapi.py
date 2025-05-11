from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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

#from app.api.routes.building_routes import router as building_router
#from app.api.routes.item_routes import router as item_router

# Dark-mode CSS for Swagger UI (CDN or local)
#swagger_ui_params = {
#    "customCssUrl": "https://cdn.jsdelivr.net/gh/Amoenus/SwaggerDark@main/swagger-dark.css"
#}

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
#app.include_router(building_router,   prefix="/api/v1", tags=["building"])
#app.include_router(item_router,       prefix="/api/v1", tags=["item"])

@fastapi.get("/status")
def status():
    """Check the status of the API"""
    return {"status": 200}
