import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Boolean, DateTime, func, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ActionTemplate(Base):
    __tablename__ = 'action_templates'
    
    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey('action_categories.id'), 
        nullable=False
    )
    description: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    action_verb: Mapped[str] = mapped_column(String(50), nullable=False, default="perform")
    
    # Requirements (stored as JSONB for flexibility)
    requirements: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    
    # Rewards (stored as JSONB array)
    possible_rewards: Mapped[list] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    
    # Timing and progression
    base_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    difficulty_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_skill_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # UI and display
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    flavor_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_repeatable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Unlock conditions
    prerequisite_action_ids: Mapped[list] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    unlock_world_day: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
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
    category: Mapped["ActionCategory"] = relationship(
        "ActionCategory",
        back_populates="action_templates"
    )