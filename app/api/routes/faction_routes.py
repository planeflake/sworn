"""
API routes for factions.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_db
from app.game_state.services.faction.faction_service import FactionService
from app.api.schemas.faction_schema import FactionResponse, FactionCreate


router = APIRouter()

@router.get("/", response_model=List[FactionResponse])
async def get_factions(
        db: AsyncSession = Depends(get_async_db)):
    faction_service = FactionService(db)
    factions = await faction_service.find_all()
    return [FactionResponse.model_validate(faction.model_dump()) for faction in factions]

@router.post("/", response_model=FactionResponse)
async def create_faction(
        faction_data: FactionCreate,
        db: AsyncSession = Depends(get_async_db),        ):
        faction_service = FactionService(db)
        faction = await faction_service.create_entity(faction_data.model_dump())
        logging.info(f"[FactionRoutes] Created faction: {faction.model_dump()}")
        return FactionResponse.model_validate(faction.model_dump())