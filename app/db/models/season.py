# --- START OF FILE app/db/models/season.py ---

from sqlalchemy import Integer, String, DateTime, func, ForeignKey # Added ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as pgUUID # Use alias
from .base import Base
import uuid # Import uuid
from datetime import datetime # Import datetime
from typing import Optional # Import Optional

class Season(Base):
    """Season model for SQLAlchemy ORM"""
    __tablename__ = 'seasons'

    # --- Fields REQUIRED in Python __init__ (Non-Defaults first) ---
    # Foreign Key to themes table (No Python default, required)
    theme_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("themes.id"), # <<< Make sure 'themes.id' exists
        nullable=False
        # init=True is default
    )

    # --- Fields OPTIONAL/PROVIDED in Python __init__ (Defaults available) ---
    # Primary Key (Has default, but can be provided)
    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
        # init=True is default
    )
    # Name (Has default, but can be provided)
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Default Season" # Changed default name
        # init=True is default
    )
    # Description (Has default, but can be provided)
    description: Mapped[Optional[str]] = mapped_column( # Use Optional for nullable
        String(255),
        nullable=True,
        default=""
        # init=True is default
    )
    # Duration (Has default, but can be provided)
    duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=90 # Example default duration (e.g., days)
        # init=True is default
    )

    # --- Timestamps (Excluded from __init__) ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), # Add timezone
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column( # Make Optional
        DateTime(timezone=True), # Add timezone
        onupdate=func.now(),
        server_default=func.now(), # Optional: sets on insert
        nullable=True
    )

    # Relationship back to Theme (define Theme model elsewhere)
    # theme: Mapped["Theme"] = relationship(back_populates="seasons")

    def __repr__(self) -> str:
        """
            String representation of the Season object for debugging/logging
        """
        return f"<Season(id={self.id}, name='{self.name}', duration={self.duration})>"

    def __eq__(self, other: object) -> bool:
        """
            Equality check based on primary key.
        """
        if not isinstance(other, Season):
            return NotImplemented
        return self.id == other.id

    def __to_dict__(self) -> dict:
        """Convert selected fields to dictionary"""
        return {
            "id": str(self.id) if self.id else None,
            "theme_id": str(self.theme_id) if self.theme_id else None,
            "name": self.name,
            "description": self.description,
            "duration": self.duration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }