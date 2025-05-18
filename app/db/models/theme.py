# --- START OF FILE app/db/models/theme.py ---

import uuid
from datetime import datetime
from typing import Optional #, #TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects import postgresql as pg

from .base import Base
#from app.db.models.celestial_events import celestial_event_themes  # <-- Import the association table

# Import CelestialEventDB only for type checking to satisfy PyCharm
#if TYPE_CHECKING:
    #from app.db.models.celestial_events import CelestialEventDB


class ThemeDB(Base):
    __tablename__ = 'themes'

    id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


    def __repr__(self) -> str:
        return f"<ThemeDB(id={self.id!r}, name={self.name!r})>"

# --- END OF FILE app/db/models/theme.py ---
