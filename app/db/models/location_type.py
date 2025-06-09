# --- START OF FILE app/db/models/location_type.py ---

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    String, Text, DateTime, func, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY

from .base import Base

# TYPE CHECKING IMPORTS
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .location_instance import LocationInstance
    from .location_sub_type import LocationSubType

class LocationType(Base):
    """
    SQLAlchemy ORM Model for Location Types.
    Defines different types of locations and their containment rules.
    """
    __tablename__ = 'location_types'
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Theme for this location type (e.g., fantasy, space, medieval)
    theme: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    
    # Containment rules - what location types this type can contain
    can_contain: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True,
        comment="Codes of location types that can be children of this type."
    )
    
    # Required and optional attributes
    required_attributes: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb"),
        comment="Schema of required attributes for this location type."
    )
    
    optional_attributes: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb"),
        comment="Schema of optional attributes for this location type."
    )
    
    # Visual representation
    icon_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Subtype options for this location type (e.g., Village, Town, Capital for settlement)
    sub_types: Mapped[List["LocationSubType"]] = relationship(
        "LocationSubType",
        back_populates="location_type",
        cascade="all, delete-orphan"
    )

    # Tags for categorization
    tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
    
    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    
    # --- Relationships ---
    # These relationships connect to LocationInstance, which is what we'll rename
    # the current Location class to. This avoids confusion with domain entities.
    locations: Mapped[List["LocationInstance"]] = relationship(
        "LocationInstance",
        back_populates="location_type",
        foreign_keys="[LocationInstance.location_type_id]",
        lazy="selectin"
    )

    # This relationship loads locations that have this location type as their parent
    parent_locations: Mapped[List["LocationInstance"]] = relationship(
        "LocationInstance",
        foreign_keys="[LocationInstance.parent_type_id]",
        back_populates="parent_type",
        lazy="selectin",
        viewonly=True  # Make this viewonly to avoid circular loading issues
    )
    
    def __repr__(self) -> str:
        return f"<LocationType(id={self.id!r}, code={self.code!r}, name={self.name!r})>"

# --- END OF FILE app/db/models/location_type.py ---