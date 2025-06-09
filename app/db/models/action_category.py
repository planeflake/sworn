import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Boolean, DateTime, func, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ActionCategory(Base):
    __tablename__ = 'action_categories'
    
    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey('action_categories.id'), 
        nullable=True
    )
    description: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
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
    parent_category: Mapped[Optional["ActionCategory"]] = relationship(
        "ActionCategory", 
        remote_side=[id],
        back_populates="child_categories"
    )
    child_categories: Mapped[list["ActionCategory"]] = relationship(
        "ActionCategory",
        back_populates="parent_category"
    )
    action_templates: Mapped[list["ActionTemplate"]] = relationship(
        "ActionTemplate",
        back_populates="category"
    )