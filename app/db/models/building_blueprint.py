# --- START OF FILE app/db/models/building_blueprint.py ---

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime,
    ForeignKey, UniqueConstraint, Index, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID, JSONB
from sqlalchemy.sql import text

from .base import Base
from .theme import Theme
# Import BlueprintStage only for type hinting if needed, avoid circular import issues
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .blueprint_stage import BlueprintStage # Correct path



class BuildingBlueprint(Base):
    """
    Building Blueprint SQLAlchemy ORM Model.
    Defines the multi-stage plan for constructing a building type.
    """
    __tablename__ = 'building_blueprints' # <<< Renamed table

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Foreign Key to Theme
    theme_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("themes.id", name="fk_building_blueprint_theme_id"), # Constraint name updated
        nullable=False,
        index=True
    )

    # Relationship to Theme
    theme: Mapped["Theme"] = relationship(
        "Theme",
        back_populates="building_blueprints", # Assumes Theme model has this relationship name
        lazy="selectin",
    )

    # Relationship to Stages (One Blueprint has Many Stages)
    # Make sure BlueprintStage is defined later or handle string reference correctly
    stages: Mapped[List["BlueprintStage"]] = relationship(
        "BlueprintStage",
        back_populates="blueprint",
        cascade="all, delete-orphan", # Delete stages if blueprint is deleted
        order_by="BlueprintStage.stage_number", # Ensure stages load in order
        lazy="selectin" # Load stages efficiently when blueprint is loaded
    )

    # Overall metadata, maybe unlock requirements, final building stats template?
    #metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
    ##    JSONB, nullable=True,
    #    comment="Overall blueprint metadata (e.g., final stats template, category)."
    #)

    is_unique_per_settlement: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default='false',
        comment="If true, only one INSTANCE based on this blueprint can exist per settlement."
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('name', 'theme_id', name='uq_building_blueprint_name_theme'),
        # {'schema': 'my_schema'} # Add schema if needed
    )

    def __repr__(self) -> str:
        return f"<BuildingBlueprint(id={self.id!r}, name={self.name!r})>"

# --- END OF FILE app/db/models/building_blueprint.py ---