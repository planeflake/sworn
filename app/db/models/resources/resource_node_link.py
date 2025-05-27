# app/db/models/resources/resource_node_link.py

import uuid
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql.sqltypes import Boolean, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from ..base import Base

# Both class names should be available for imports
class ResourceNodeResource(Base):
    __tablename__ = "resource_node_resources"
    __table_args__ = {'extend_existing': True}

    node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resource_nodes.id"), primary_key=True)
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resources.id"), primary_key=True)

    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)  # primary or secondary
    chance: Mapped[float] = mapped_column(Float, default=1.0)          # 1.0 = 100%, 0.15 = 15%
    amount_min: Mapped[int] = mapped_column(Integer, default=1)
    amount_max: Mapped[int] = mapped_column(Integer, default=1)
    purity: Mapped[float] = mapped_column(Float, default=1.0)
    rarity: Mapped[str] = mapped_column(String, default="common")
    _metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default=dict)

    node = relationship("ResourceNode", back_populates="resource_links")
    resource = relationship("ResourceBlueprint", back_populates="node_links")

    def __repr__(self) -> str:
        return f"<ResourceNodeResource(node_id={self.node_id}, resource_id={self.resource_id})>"

# Alias for backward compatibility and model/__init__.py references
ResourceNodeLink = ResourceNodeResource