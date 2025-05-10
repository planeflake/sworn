# --- START OF FILE app/db/models/blueprint_stage.py ---

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Integer, String, Text, ForeignKey, UniqueConstraint, Index, func, text, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID

from .base import Base
# Import related models for type hinting within TYPE_CHECKING block
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .building_blueprint import BuildingBlueprint
    from .stage_resource_cost import StageResourceCost
    from .stage_profession_cost import StageProfessionCost

class BlueprintStage(Base):
    """
    Represents a single stage/level of construction for a BuildingBlueprint.
    """
    __tablename__ = 'blueprint_stages'

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    building_blueprint_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("building_blueprints.id", name="fk_stage_bp_id", ondelete="CASCADE"), # Shortened FK name
        nullable=False,
        index=True
    )

    stage_number: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Order of the stage (e.g., 1, 2, 3...)"
    )

    name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        comment="Optional name for the stage (e.g., Foundation, Framing)"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Optional description of work done in this stage."
    )

    duration_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default='1',
        comment="Time required to complete this stage (e.g., in game days)."
    )

    # Relationship back to the parent Blueprint
    blueprint: Mapped["BuildingBlueprint"] = relationship(
        "BuildingBlueprint",
        back_populates="stages" # Matches 'stages' relationship in BuildingBlueprint
    )

    # Relationship to Resource Costs for this stage
    resource_costs: Mapped[List["StageResourceCost"]] = relationship(
        "StageResourceCost",
        back_populates="stage", # Matches 'stage' in StageResourceCost
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Relationship to Profession Costs for this stage
    profession_costs: Mapped[List["StageProfessionCost"]] = relationship(
        "StageProfessionCost",
        back_populates="stage", # Matches 'stage' in StageProfessionCost
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Timestamps for the stage definition itself
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False # Added timezone=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True # Added timezone=True, made nullable
    )

    __table_args__ = (
        UniqueConstraint('building_blueprint_id', 'stage_number', name='uq_bp_stage_number'), # Shortened
        Index('ix_bp_stage_bp_id_stage_number', 'building_blueprint_id', 'stage_number'), # Shortened
        # {'schema': 'my_schema'}
    )

    def __repr__(self) -> str:
        return f"<BlueprintStage(id={self.id!r}, blueprint_id={self.building_blueprint_id!r}, stage={self.stage_number})>"

# --- END OF FILE app/db/models/blueprint_stage.py ---