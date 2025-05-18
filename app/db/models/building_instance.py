# --- START OF FILE app/db/models/building_instance.py ---
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
import enum

from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, Enum as SQLAlchemyEnum, func, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID, JSONB, ARRAY

from .base import Base
from app.game_state.enums.building import BuildingStatus # Import from proper enum location
from app.game_state.entities.character import CharacterEntity # Assuming this is the correct path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .building_blueprint import BuildingBlueprint
    from .settlement import Settlement
    # from .blueprint_stage_feature import BlueprintStageFeature
    # from .character import Character # For inhabitants/workers

class BuildingInstanceDB(Base): # Suffix with DB to avoid clash with domain entity
    __tablename__ = 'building_instances'

    # Using the entity's 'name' for the instance name
    # If entity_id from BaseEntity is to be the PK, that's fine.
    # Otherwise, define a separate PK here. Let's assume entity_id is the PK.
    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()") # <<< ADD THIS (or default=uuid.uuid4 if client generates)
    )       

    name: Mapped[str] = mapped_column(String(150), nullable=False) # Instance specific name, can default to blueprint name

    building_blueprint_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), ForeignKey("building_blueprints.id"), nullable=False, index=True
    )
    blueprint: Mapped["BuildingBlueprint"] = relationship(lazy="selectin") # No back_populates needed if blueprint doesn't track instances directly

    settlement_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), ForeignKey("settlements.id"), nullable=False, index=True
    )
    settlement: Mapped["Settlement"] = relationship(
        "Settlement", back_populates="building_instances" # Assumes 'building_instances' in Settlement model
    )

    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[BuildingStatus] = mapped_column(SQLAlchemyEnum(BuildingStatus, name="building_status_enum", create_type=False), nullable=False)
    current_hp: Mapped[int] = mapped_column(Integer, nullable=False)
    max_hp: Mapped[int] = mapped_column(Integer, nullable=False)

    inhabitants: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_inhabitants: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    construction_progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False) # 0.0 to 1.0 per stage
    current_stage_number: Mapped[int] = mapped_column(Integer, nullable=False, comment="The stage number currently being worked on or just completed.")

    # Store which optional features from blueprints have been built for THIS instance.
    # List of blueprint_stage_feature_ids (UUIDs)
    active_features: Mapped[Optional[List[uuid.UUID]]] = mapped_column(
        ARRAY(pgUUID(as_uuid=True)), nullable=True
    )

    residents: Mapped[List["CharacterEntity"]] = relationship(
        "Character",
        foreign_keys="[Character.current_building_home_id]", # String reference to avoid circular import
        back_populates="home_building"
    )
    workers: Mapped[List["CharacterEntity"]] = relationship(
        "Character",
        foreign_keys="[Character.current_building_workplace_id]", # String reference
        back_populates="work_building"
    )

    # [{'resource_id': UUID, 'quantity': int}]
    stored_resources: Mapped[Optional[Dict[uuid.UUID, int]]] = mapped_column(JSONB, nullable=True)
    # [{'profession_id': UUID, 'count': int}] or profession names
    assigned_workers: Mapped[Optional[Dict[str, int]]] = mapped_column(JSONB, nullable=True)

    instance_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationship for inhabitants/workers (see point 7)
    # characters_assigned_home: Mapped[List["Character"]] = relationship(
    #     "Character",
    #     secondary="building_character_homes", # Association table
    #     back_populates="home_building"
    # )
    # characters_assigned_work: Mapped[List["Character"]] = relationship(
    #     "Character",
    #     secondary="building_character_workplaces", # Association table
    #     back_populates="work_building"
    # )

    def __repr__(self) -> str:
        return f"<BuildingInstanceDB(id={self.id!r}, name='{self.name}', blueprint_id={self.building_blueprint_id})>"

# --- END OF FILE app/db/models/building_instance.py ---