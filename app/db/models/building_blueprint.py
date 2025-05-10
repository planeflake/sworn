# --- START OF FILE app/db/models/building_blueprint.py ---

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime,
    ForeignKey, UniqueConstraint, Index, func, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID, JSONB

from .base import Base
# Import related models for type hinting within TYPE_CHECKING block
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .theme import Theme
    from .blueprint_stage import BlueprintStage

class BuildingBlueprint(Base):
    """
    Building Blueprint SQLAlchemy ORM Model.
    Defines the multi-stage plan for constructing a building type.
    """
    __tablename__ = 'building_blueprints'

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # --- Foreign Key and Relationship to Theme ---
    theme_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("themes.id", name="fk_bp_theme_id"), # Shortened FK name
        nullable=False, # Assuming a blueprint must belong to a theme
        index=True
    )
    theme: Mapped["Theme"] = relationship(
        "Theme",
        back_populates="building_blueprints", # Matches relationship in Theme model
        lazy="selectin",
    )

    # --- Relationship to Stages ---
    # One Blueprint has Many Stages
    stages: Mapped[List["BlueprintStage"]] = relationship(
        "BlueprintStage",
        back_populates="blueprint", # Matches 'blueprint' relationship in BlueprintStage
        cascade="all, delete-orphan", # Delete stages if blueprint is deleted
        order_by="BlueprintStage.stage_number", # Ensure stages load in order
        lazy="selectin"
    )

    # --- Other Attributes ---
    _metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
       JSONB, nullable=True,
       comment="Overall blueprint metadata (e.g., final stats template, category)."
    )
    is_unique_per_settlement: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default='false',
        comment="If true, only one INSTANCE based on this blueprint can exist per settlement."
    )

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False # Added timezone=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=True # Added timezone=True, made nullable
    )

    __table_args__ = (
        UniqueConstraint('name', 'theme_id', name='uq_bp_name_theme'), # Shortened constraint name
        # {'schema': 'my_schema'}
    )

    def __repr__(self) -> str:
        return f"<BuildingBlueprint(id={self.id!r}, name={self.name!r})>"

# --- END OF FILE app/db/models/building_blueprint.py ---