from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlalchemy import (
    String, Text, DateTime, func, ForeignKey, Float, Index, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY

from .base import Base

# TYPE CHECKING IMPORTS
if TYPE_CHECKING:
    from .location_instance import LocationInstance
    from .location_type import LocationType
    from .theme import ThemeDB


class LocationSubType(Base):
    """
    SQLAlchemy ORM Model for Location Sub Types.
    Defines specific subtypes within each location type for different themes.
    """
    __tablename__ = 'location_sub_types'
    __table_args__ = (
        Index('idx_location_subtype_code', 'code'),
        Index('idx_location_subtype_type_theme', 'location_type_id', 'theme_id'),
        Index('idx_location_subtype_rarity', 'rarity'),
        {'extend_existing': True}
    )

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )

    # Core identification
    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        comment="Unique code identifier for the subtype"
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Human-readable name"
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Detailed description of this subtype"
    )

    # Foreign key relationships
    location_type_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey('location_types.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to the parent location type"
    )
    theme_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey('themes.id', ondelete='CASCADE'),
        nullable=False,
        comment="Reference to the theme this subtype belongs to"
    )

    # Subtype-specific attributes (JSON fields)
    required_attributes: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default='[]',
        comment="Attributes that must be present for this subtype"
    )
    optional_attributes: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default='[]',
        comment="Attributes that may be present for this subtype"
    )

    # Visual and categorization
    icon_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Path to icon file for this subtype"
    )
    tags: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
        server_default='{}',
        comment="Tags for categorization and filtering"
    )

    # Gameplay mechanics
    rarity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default='common',
        server_default='common',
        comment="How common this subtype is"
    )
    generation_weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        server_default='1.0',
        comment="Weight for procedural generation"
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now()
    )

    # Relationships
    location_type: Mapped["LocationType"] = relationship(
        "LocationType",
        back_populates="sub_types",
        lazy="select"
    )
    theme: Mapped["ThemeDB"] = relationship(
        "ThemeDB",
        back_populates="location_sub_types",
        lazy="select"
    )
    location_instances: Mapped[List["LocationInstance"]] = relationship(
        "LocationInstance",
        back_populates="sub_type",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<LocationSubType(code='{self.code}', name='{self.name}', theme='{self.theme.name if self.theme else 'Unknown'}')>"

