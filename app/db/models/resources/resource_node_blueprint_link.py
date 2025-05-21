# app/db/models/resources/resource_node_blueprint_link.py

import uuid
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Boolean, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.resources.resource_node_blueprint import ResourceNodeBlueprint
    from app.db.models.resources.resource_blueprint import Resource
    from app.db.models.theme import ThemeDB


class ResourceNodeBlueprintResource(Base):
    __tablename__ = "resource_node_blueprint_resources"

    blueprint_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("resource_node_blueprints.id", ondelete="CASCADE"),
        primary_key=True
    )

    resource_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("resources.id", ondelete="CASCADE"),
        primary_key=True
    )

    is_primary: Mapped[bool] = mapped_column(default=True)
    chance: Mapped[float] = mapped_column(default=1.0)
    amount_min: Mapped[int] = mapped_column(default=1)
    amount_max: Mapped[int] = mapped_column(default=1)
    purity: Mapped[float] = mapped_column(default=1.0)
    rarity: Mapped[str] = mapped_column(String(50), default="common")

    _metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict
    )

    theme_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("themes.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    blueprint: Mapped["ResourceNodeBlueprint"] = relationship(
        back_populates="resource_links",
        lazy="selectin"
    )

    resource: Mapped["Resource"] = relationship(
        back_populates="blueprint_links",
        lazy="selectin"
    )

    theme: Mapped[Optional["ThemeDB"]] = relationship(
        "ThemeDB",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<ResourceNodeBlueprintResource("
            f"blueprint_id={self.blueprint_id}, "
            f"resource_id={self.resource_id}, "
            f"chance={self.chance})>"
        )
