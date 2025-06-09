import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, Boolean, DateTime, func, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ToolTier(Base):
    __tablename__ = 'tool_tiers'
    
    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    theme_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey('themes.id'), 
        nullable=False
    )
    tier_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tier_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    effectiveness_multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    description: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Unlock requirements
    required_tech_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    required_materials: Mapped[list] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    
    # Theme-specific flavor
    flavor_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    color_hex: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # #FFFFFF format
    
    # Timestamps
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
    
    # Metadata
    tags: Mapped[list] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    meta_data: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    
    # Relationships
    theme: Mapped["ThemeDB"] = relationship("ThemeDB", back_populates="tool_tiers")
    
    # Indexes for common queries
    __table_args__ = (
        # Index for theme + tier level queries
        {'comment': 'Tool tiers define progression within themes'}
    )