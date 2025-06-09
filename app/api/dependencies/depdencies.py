from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.async_session import get_db_session  # Adjust import based on your project structure

from app.game_state.services.geography.location_sub_type_service import LocationSubTypeService

async def get_location_subtype_service(
    db: AsyncSession = Depends(get_db_session)  # Inject db session directly
) -> LocationSubTypeService:
    """Dependency to get location subtype service"""
    return LocationSubTypeService(db)  # Pass db to service