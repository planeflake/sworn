# --- START OF FILE app/db/models/building_upgrade_blueprint.py ---
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any # Keep Any for flexibility in JSON

from sqlalchemy import (
    Integer, String, Text, ForeignKey, UniqueConstraint, Index, func, text, DateTime, Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID, JSONB

from .base import Base
from typing import TYPE_CHECKING
# if TYPE_CHECKING:
    # from .building_blueprint import BuildingBlueprint

class BuildingUpgradeBlueprint(Base):
    """
    Defines an upgrade that can be applied to an existing BuildingInstance
    or chosen during initial construction.
    """
    __tablename__ = 'building_upgrade_blueprints'

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    target_blueprint_criteria: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    prerequisites: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    resource_cost: Mapped[Optional[Dict[str, int]]] = mapped_column(
        JSONB, nullable=True,
        comment="Resource costs. E.g., {'<resource_uuid_str>': 50, '<another_resource_uuid_str>': 20}"
    )
    profession_cost: Mapped[Optional[Dict[str, int]]] = mapped_column(
        JSONB, nullable=True,
        comment="Profession costs (worker count). E.g., {'<profession_def_uuid_str>': 1}"
    )
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default='1')

    effects: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    is_initial_choice: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default='false')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    #Create index with a specific name
    __table_args__ = (Index('ix_bldg_upg_bp_name', 'name'),)

    def __repr__(self) -> str:
        return f"<BuildingUpgradeBlueprint(id={self.id!r}, name='{self.name!r}')>"

# --- END OF FILE ---