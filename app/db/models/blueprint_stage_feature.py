# --- START OF FILE app/db/models/blueprint_stage_feature.py ---
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, Text,
    ForeignKey, UniqueConstraint, Index, func, text,DateTime, Float
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID, JSONB

from .base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .blueprint_stage import BlueprintStage
    # from .profession_definition import ProfessionDefinition # If you have this model

class BlueprintStageFeature(Base):
    __tablename__ = 'blueprint_stage_features'

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    blueprint_stage_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), ForeignKey("blueprint_stages.id"), nullable=False, index=True
    )
    stage: Mapped["BlueprintStage"] = relationship(
        "BlueprintStage", back_populates="optional_features"
    )

    feature_key: Mapped[str] = mapped_column(String(100), nullable=False, comment="Unique key for this feature within the stage, e.g., 'arrow_slits'.")
    name: Mapped[str] = mapped_column(String(150), nullable=False) # e.g., "Arrow Slits"
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # [{'profession_id': UUID}] or profession names/keys
    required_professions: Mapped[Optional[List[uuid.UUID]]] = mapped_column(
        JSONB, nullable=True, # Could also be ARRAY(pgUUID) if always UUIDs
        comment="List of profession IDs required to build this specific feature."
    )

    # Resource costs specific to THIS feature, additional to stage costs
    # [{'resource_id': UUID, 'amount': int}]
    additional_resource_costs: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)

    # Additional time specific to THIS feature
    additional_duration_days: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # What this feature provides. E.g., {'stat_bonus': {'ranged_damage_mod': 0.1}, 'ability': 'sniper_shot'}
    effects: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Could add: mutual_exclusions: List[str] (keys of other features in this stage it cannot be built with)
    # icon: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    __table_args__ = (
        UniqueConstraint('blueprint_stage_id', 'feature_key', name='uq_stage_feature_key'),
    )

    def __repr__(self) -> str:
        return f"<BlueprintStageFeature(id={self.id!r}, stage_id={self.blueprint_stage_id}, name='{self.name}')>"
# --- END OF FILE app/db/models/blueprint_stage_feature.py ---