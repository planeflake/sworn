# --- START OF FILE app/db/models/item.py ---

import uuid
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Integer, String, Text, Boolean, Float, Numeric, DateTime,
    Enum as SQLAlchemyEnum, ForeignKey, UniqueConstraint, CheckConstraint, Index, func, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID, JSONB, ARRAY

from .base import Base

# TYPE CHECKING IMPORTS
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .character import Character
    # from .location import Location # If items can be directly at locations
    # from .item_definition import ItemDefinition # If you create item definitions

class ItemStatus(enum.Enum):
    PRISTINE = "PRISTINE"
    USED = "USED"
    BROKEN = "BROKEN"

class ItemType(enum.Enum):
    WEAPON = "WEAPON"
    ARMOR = "ARMOR"
    CONSUMABLE = "CONSUMABLE"
    MATERIAL = "MATERIAL"
    QUEST = "QUEST"
    CURRENCY = "CURRENCY"
    MISC = "MISC"

class Item(Base):
    """
    SQLAlchemy ORM Model for Items.
    """
    __tablename__ = 'items'

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    # Link to an ItemDefinition model if you have one (highly recommended for non-unique items)
    # item_definition_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    #     pgUUID(as_uuid=True), ForeignKey("item_definitions.id"), index=True, nullable=True
    # )
    # item_definition: Mapped[Optional["ItemDefinition"]] = relationship("ItemDefinition")

    # If not using definitions, core attributes are here:
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    item_type: Mapped[Optional[ItemType]] = mapped_column(
        SQLAlchemyEnum(ItemType, name="item_type_enum", create_type=False), # Manage ENUM type via Alembic
        nullable=True, index=True
    )
    value: Mapped[Optional[Any]] = mapped_column(Numeric(10, 2), nullable=True) # Gold value for example
    is_stackable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default='false')
    # weight: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)
    # required_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Instance-specific attributes
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default='1')
    status: Mapped[Optional[ItemStatus]] = mapped_column(
        SQLAlchemyEnum(ItemStatus, name="item_status_enum", create_type=False), # Manage ENUM type via Alembic
        nullable=True, index=True, default=ItemStatus.PRISTINE
    )

    # --- Ownership and Location ---
    owner_character_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("characters.id", name="fk_item_owner_char_id", ondelete="SET NULL"), # Set NULL if owner deleted
        nullable=True,
        index=True
    )
    # container_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(pgUUID(as_uuid=True), ForeignKey("items.id", name="fk_item_container_id", ondelete="CASCADE"), nullable=True, index=True)
    # location_id: Mapped[Optional[uuid.UUID]] = mapped_column(pgUUID(as_uuid=True), ForeignKey("locations.id", name="fk_item_location_id", ondelete="SET NULL"), nullable=True, index=True)

    # --- Relationships ---
    owner: Mapped[Optional["Character"]] = relationship(
        "Character",
        foreign_keys=[owner_character_id],
        back_populates="items"
    )
    # container: Mapped[Optional["Item"]] = relationship("Item", remote_side=[id], back_populates="items_in_container", foreign_keys=[container_item_id])
    # items_in_container: Mapped[List["Item"]] = relationship("Item", back_populates="container")
    # location: Mapped[Optional["Location"]] = relationship("Location", foreign_keys=[location_id], back_populates="items_at_location")

    # --- Complex Data ---
    _metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
       JSONB, nullable=True, default=lambda: {},
       comment="Instance-specific data, e.g., magical properties, durability, crafter_id."
    )

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=True)

    __table_args__ = (
        CheckConstraint('quantity > 0', name='chk_item_quantity_positive'),
        # Index('ix_item_owner_character_id', 'owner_character_id'), # Already indexed by column definition
    )

    def __repr__(self) -> str:
        owner_id_str = f"owner={self.owner_character_id!r}" if self.owner_character_id else "unowned"
        return f"<Item(id={self.id!r}, name={self.name!r}, qty={self.quantity}, {owner_id_str})>"

# --- END OF FILE app/db/models/item.py ---