# --- START OF FILE app/db/models/theme.py ---
from sqlalchemy import Column, String, Text # Added Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text, func # Added func for timestamps
from sqlalchemy.sql.sqltypes import DateTime # Added DateTime
from typing import Optional
from .base import Base
from datetime import datetime # Added datetime for timestamps

class Theme(Base):
    """Theme model for SQLAlchemy ORM"""
    __tablename__ = 'themes' # Make sure this table exists in your DB

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), # Use as_uuid=True for Python UUID objects
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Use Text for longer descriptions
    # Optional: Add timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Add other columns corresponding to the entity

    def __repr__(self) -> str:
        return f"<Theme(id={self.id}, name='{self.name}')>"

# --- END OF FILE app/db/models/theme.py ---