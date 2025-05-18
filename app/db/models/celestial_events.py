# --- START OF FILE app/db/models/celestial_event.py ---

import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import Table, Column, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects import postgresql as pg

from .base import Base

# Import ThemeDB only for type checking to satisfy PyCharm
if TYPE_CHECKING:
    from app.db.models.theme import ThemeDB


# Association table between celestial events and themes
celestial_event_themes = Table(
    "celestial_event_themes",
    Base.metadata,
    Column("event_id", pg.UUID(as_uuid=True), ForeignKey("celestial_events.id", ondelete="CASCADE")),
    Column("theme_id", pg.UUID(as_uuid=True), ForeignKey("themes.id", ondelete="CASCADE"))
)


class CelestialEventDB(Base):
    __tablename__ = "celestial_events"

    id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon_path: Mapped[str] = mapped_column(Text, nullable=False)
    actions: Mapped[List[str]] = mapped_column(pg.ARRAY(Text), nullable=False)

    created_at: Mapped[datetime] = mapped_column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(pg.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship to themes
    themes: Mapped[List["ThemeDB"]] = relationship(
        "ThemeDB",                            # string avoids circular import
        secondary=celestial_event_themes
    )

    def __repr__(self) -> str:
        return f"<CelestialEventDB(id={self.id!r}, name={self.name!r})>"

# --- END OF FILE app/db/models/celestial_event.py ---
