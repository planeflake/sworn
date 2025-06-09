# --- FILE: app/db/models/location_instance.py ---

import uuid
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from sqlalchemy import ForeignKey, String, DateTime, func, Boolean, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from .base import Base
from .locations.location_faction_presence import LocationFactionPresence

if TYPE_CHECKING:
    from .world import World
    from .location_type import LocationType
    from .character import Character
    from .resources.resource_node import ResourceNode
    from .theme import ThemeDB
    from .biome import Biome
    from .faction import Faction
    from .travel_link import TravelLink
    from .wildlife import Wildlife
    from .location_sub_type import LocationSubType


class LocationInstance(Base):
    """
    SQLAlchemy ORM Model for Location Instances in the game world.
    Each location instance has a type that defines its properties and behavior.
    """
    __tablename__ = "location_entities"
    __table_args__ = (
        # drop the old “parent_type must equal location_type” rule,
        # and only forbid self-parenting:
        CheckConstraint(
            "parent_id IS NULL OR parent_id <> id",
            name="ck_location_no_self_parent"
        ),
        {'extend_existing': True},
    )

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # --- Foreign Keys ---
    # Added in migration add_world_id_to_location_entities
    # Initially nullable until populated
    world_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("worlds.id", name="fk_location_world_id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    location_type_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("location_types.id", name="fk_location_type_id"),
        nullable=False,
        index=True
    )

    # Parent relationship (self-referential)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("location_entities.id", name="fk_parent_location", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Parent type relationship
    parent_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("location_types.id", name="fk_parent_location_type", ondelete="SET NULL"),
        nullable=True
    )



    # Theme and biome references
    theme_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("themes.id", name="fk_location_theme_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    biome_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("biomes.id", name="fk_location_biome_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    sub_type_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey('location_sub_types.id'),
        nullable=True
    )
    sub_type: Mapped[Optional["LocationSubType"]] = relationship("LocationSubType")
    
    # Base danger level for this location
    base_danger_level: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default='1',
        comment="Base danger level from 1-10"
    )
    
    # Faction that controls this location
    controlled_by_faction_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("factions.id", name="fk_location_controlling_faction", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Factions present in this location and their percentage.
    present_factions: Mapped[list[LocationFactionPresence]] = relationship(
        "LocationFactionPresence",
        back_populates = "location",
        cascade = "all, delete-orphan",
        lazy = "selectin",
    )

    # Attributes and metadata
    attributes: Mapped[Dict[str, Any]] = mapped_column(
        pg.JSONB, nullable=False, server_default='{}',
        comment="Custom attributes for the location entity."
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=func.cast(True, Boolean),
        index=True
    )
    
    # Tags for categorization
    tags: Mapped[Optional[List[str]]] = mapped_column(
        pg.ARRAY(String), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # --- Relationships ---
    # Relationship to world, nullable until migration is run
    world: Mapped[Optional["World"]] = relationship(
        "World", 
        back_populates="locations", 
        lazy="selectin"
    )

    location_type: Mapped["LocationType"] = relationship(
        "LocationType",
        back_populates="locations",
        foreign_keys=[location_type_id],
        lazy="selectin"
    )



    parent_type: Mapped[Optional["LocationType"]] = relationship(
        "LocationType",
        back_populates="parent_locations",
        foreign_keys=[parent_type_id],
        lazy="selectin"
    )
    
    parent: Mapped[Optional["LocationInstance"]] = relationship(
        "LocationInstance",
        remote_side=[id],
        back_populates="children",
        foreign_keys=[parent_id],
        lazy="selectin"
    )
    
    children: Mapped[List["LocationInstance"]] = relationship(
        "LocationInstance",
        back_populates="parent",
        foreign_keys=[parent_id],
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    characters_at_location: Mapped[List["Character"]] = relationship(
        "Character",
        foreign_keys="[Character.current_location_id]",
        primaryjoin="LocationInstance.id == Character.current_location_id",
        lazy="selectin",
        viewonly=True  # To avoid circular dependencies
    )
    
    # Resource nodes at this location
    resource_nodes: Mapped[List["ResourceNode"]] = relationship(
        "ResourceNode",
        back_populates="location",
        lazy="selectin"
    )
    
    # Theme relationship
    theme: Mapped[Optional["ThemeDB"]] = relationship(
        "ThemeDB",
        foreign_keys=[theme_id],
        lazy="selectin"
    )
    
    # Biome relationship
    biome: Mapped[Optional["Biome"]] = relationship(
        "Biome",
        foreign_keys=[biome_id],
        lazy="selectin"
    )
    
    # Controlling faction relationship
    controlling_faction: Mapped[Optional["Faction"]] = relationship(
        "Faction",
        foreign_keys=[controlled_by_faction_id],
        lazy="selectin"
    )
    
    # Travel link relationships
    outgoing_travel_links: Mapped[List["TravelLink"]] = relationship(
        "TravelLink",
        foreign_keys="[TravelLink.from_location_id]",
        back_populates="from_location",
        lazy="selectin"
    )
    
    incoming_travel_links: Mapped[List["TravelLink"]] = relationship(
        "TravelLink",
        foreign_keys="[TravelLink.to_location_id]",
        back_populates="to_location",
        lazy="selectin"
    )
    
    # Wildlife inhabiting this location
    wildlife: Mapped[List["Wildlife"]] = relationship(
        "Wildlife",
        back_populates="location",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        type_code = self.location_type.code if self.location_type else None
        parent_id = str(self.parent_id) if self.parent_id else None
        return f"<LocationInstance(id={self.id!r}, name={self.name!r}, type={type_code}, parent_id={parent_id})>"