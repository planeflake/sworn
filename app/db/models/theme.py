# --- START OF FILE app/db/models/theme.py ---

import uuid
from datetime import datetime
from typing import Optional, List # Added List

from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID

from .base import Base

# TYPE CHECKING IMPORTS
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .building_blueprint import BuildingBlueprint # For the back_populates

class Theme(Base):
    __tablename__ = 'themes'

    id: Mapped[uuid.UUID] = mapped_column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationship to BuildingBlueprints
    building_blueprints: Mapped[List["BuildingBlueprint"]] = relationship(
        "BuildingBlueprint",
        back_populates="theme", # Matches 'theme' in BuildingBlueprint model
        cascade="all, delete-orphan" # Optional: if deleting a theme deletes its blueprints
    )

    def __repr__(self) -> str:
        return f"<Theme(id={self.id!r}, name={self.name!r})>"

# --- END OF FILE app/db/models/theme.py ---