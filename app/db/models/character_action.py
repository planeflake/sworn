import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import String, Integer, Float, DateTime, Enum as SQLEnum, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from app.game_state.entities.action.character_action_pydantic import ActionType, ActionStatus

class CharacterAction(Base):
    __tablename__ = 'character_actions'
    
    # Using 'id' as primary key to match your pattern (maps to entity_id)
    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    
    # Inheriting common fields pattern from your base entities
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        onupdate=func.now()
    )
    
    # Action-specific fields
    character_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        nullable=False, 
        index=True
    )
    action_type: Mapped[ActionType] = mapped_column(
        SQLEnum(ActionType), 
        nullable=False, 
        index=True
    )
    target_id: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID(as_uuid=True))
    location_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    status: Mapped[ActionStatus] = mapped_column(
        SQLEnum(ActionStatus), 
        default=ActionStatus.QUEUED, 
        index=True
    )
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    result: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)