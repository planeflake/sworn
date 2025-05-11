# --- START OF FILE app/db/models/blueprint_stage.py ---

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any # Added Dict, Any

from sqlalchemy import (
    Integer, String, Text, ForeignKey, UniqueConstraint, Index, func, text, DateTime, Float # Added Float
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID, JSONB # Added JSONB

from .base import Base

# Import related models for type hinting within TYPE_CHECKING block
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .building_blueprint import BuildingBlueprint
    from .blueprint_stage_feature import BlueprintStageFeature # Corrected from your previous file structure

class BlueprintStage(Base):
    """
    Represents a single stage/level of construction for a BuildingBlueprint.
    Costs and bonuses are stored as JSONB for simplicity in this version.
    """
    __tablename__ = 'blueprint_stages'

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    building_blueprint_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("building_blueprints.id", name="fk_stage_bp_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    stage_number: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Order of the stage (e.g., 1, 2, 3...)"
    )

    name: Mapped[str] = mapped_column( # Changed from Optional[str] to str and made nullable=False
        String(150), nullable=False, # To match Entity/Schema which expect a name
        comment="Name for the stage (e.g., Foundation, Framing)"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Optional description of work done in this stage."
    )

    duration_days: Mapped[float] = mapped_column( # Changed from Integer to Float
        Float, nullable=False, default=1.0, server_default='1.0', # Added default
        comment="Time required to complete this stage (e.g., in game days)."
    )

    # --- Store costs and bonuses as JSONB to match Entity/Schema ---
    # [{'resource_id': UUID_str, 'amount': int}]
    resource_costs: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True, comment="List of resource costs for this stage."
    )
    # [{'profession_id': UUID_str, 'time_modifier': float}]
    profession_time_bonus: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True, comment="Bonuses from professions affecting stage duration."
    )
    # [{'bonus_type': str, ...}]
    stage_completion_bonuses: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True, comment="Bonuses applied upon completing this stage."
    )
    # --- End JSONB fields ---

    # Relationship back to the parent Blueprint
    blueprint: Mapped["BuildingBlueprint"] = relationship(
        "BuildingBlueprint",
        back_populates="stages" # Matches 'stages' relationship in BuildingBlueprint
    )

    # Relationship to Optional Features (this relationship is with BlueprintStageFeatureDB model)
    optional_features: Mapped[List["BlueprintStageFeature"]] = relationship(
        "BlueprintStageFeature", # This should point to BlueprintStageFeatureDB model
        back_populates="stage", # Matches 'stage' relationship in BlueprintStageFeatureDB
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Timestamps for the stage definition itself
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    __table_args__ = (
        UniqueConstraint('building_blueprint_id', 'stage_number', name='uq_bp_stage_number'),
        Index('ix_bp_stage_bp_id_stage_number', 'building_blueprint_id', 'stage_number'),
    )

    def __repr__(self) -> str:
        return f"<BlueprintStage(id={self.id!r}, blueprint_id={self.building_blueprint_id!r}, stage={self.stage_number})>"

# --- END OF FILE app/db/models/blueprint_stage.py ---