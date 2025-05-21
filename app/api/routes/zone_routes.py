from app.game_state.services.zone_service import ZoneService
from app.api.schemas.zone_api_schema import  ZoneCreatedResponse, ZoneCreate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Body
from app.db.dependencies import get_async_db
import logging

router = APIRouter()

@router.post("/", response_model=ZoneCreatedResponse)
async def create_zone(
        zone_data: ZoneCreate = Body(...),
        db: AsyncSession = Depends(get_async_db)
    ):
    """Endpoint to create a new zone."""
    logging.info(f"[ZoneRoutes] Request to create zone with data: {zone_data.model_dump()}")
    zone_service = ZoneService(db=db)
    zone_api_model = await zone_service.create_zone(zone_data)
    return zone_api_model

