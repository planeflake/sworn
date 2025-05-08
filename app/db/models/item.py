# --- START OF FILE app/db/models/item.py ---

import uuid
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Integer, String, Text, Boolean, Float, Numeric, DateTime, Date, Time,
    Enum as SQLAlchemyEnum, ForeignKey, UniqueConstraint, CheckConstraint, Index, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID, JSONB, ARRAY
from sqlalchemy.sql import text

from .base import Base
# Import Character only needed for type hinting if using TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .character import Character

# Define any Item-specific enums here or import
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
    CURRENCY = "CURRENCY" # Or handle currency separately
    MISC = "MISC"

class Item(Base):
    """
    SQLAlchemy ORM Model for Items.
    Represents individual items in the game world, potentially owned by characters.
    """
    __tablename__ = 'items'

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    # --- Item Definition Link ---
    # Often, specific instances link to a 'template' or 'definition'
    # item_definition_id: Mapped[uuid.UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey("item_definitions.id"), index=True, nullable=False)
    # item_definition: Mapped["ItemDefinition"] = relationship("ItemDefinition") # Assumes ItemDefinition model exists

    # --- Item Instance Attributes ---
    # If not using definitions, store core attributes here
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # Or get from definition
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Or get from definition
    item_type: Mapped[Optional[ItemType]] = mapped_column( # Or get from definition
        SQLAlchemyEnum(ItemType, name="item_type_enum", create_type=False),
        nullable=True, index=True
    )
    value: Mapped[Optional[Any]] = mapped_column( # Base value, or instance value if modified
        Numeric(10, 2), nullable=True
    )
    status: Mapped[Optional[ItemStatus]] = mapped_column( # Condition of this specific item
        SQLAlchemyEnum(ItemStatus, name="item_status_enum", create_type=False),
        nullable=True, index=True, default=ItemStatus.PRISTINE
    )
    quantity: Mapped[int] = mapped_column( # For stackable items
        Integer, nullable=False, default=1, server_default='1'
    )
    is_stackable: Mapped[bool] = mapped_column( # Or get from definition
         Boolean, nullable=False, default=False, server_default='false'
    )
    # Add fields like weight, required_level, effects etc. if not using definitions,
    # or store instance-specific modifiers in metadata.

    # --- Ownership / Location ---
    # Foreign Key to the Character owning this item instance (optional)
    owner_character_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("characters.id", name="fk_item_owner_character_id"), # Links to characters table
        nullable=True, # Allow items not owned by a character (e.g., in world, chest)
        index=True
    )

    # Foreign Key to a potential container (e.g., a chest, could be another Item instance)
    # container_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(pgUUID(as_uuid=True), ForeignKey("items.id"), nullable=True, index=True)

    # Foreign key to a location if the item is on the ground / in a world location directly
    # location_id: Mapped[Optional[uuid.UUID]] = mapped_column(pgUUID(as_uuid=True), ForeignKey("locations.id"), nullable=True, index=True)

    # --- Relationships ---
    # Relationship back to the Character owner
    owner: Mapped[Optional["Character"]] = relationship(
        "Character",
        back_populates="items" # Matches 'items' relationship in Character model
    )

    # Relationship to container item (self-referential)
    # items_in_container: Mapped[List["Item"]] = relationship("Item", back_populates="container")
    # container: Mapped[Optional["Item"]] = relationship("Item", remote_side=[id], back_populates="items_in_container")

    # Relationship to location if directly placed
    # location: Mapped[Optional["Location"]] = relationship("Location", back_populates="items_at_location")


    # --- Complex Data ---
    #metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
    #    JSONB, nullable=True, default=lambda: {},
    #    comment="Instance-specific data, e.g., magical properties, durability."
    #)

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # --- Table Args ---
    __table_args__ = (
        CheckConstraint('quantity > 0', name='chk_item_quantity_positive'),
        # Add other constraints/indexes
    )

    def __repr__(self) -> str:
        owner_id = f"owner={self.owner_character_id!r}" if self.owner_character_id else "no owner"
        return f"<Item(id={self.id!r}, name={self.name!r}, qty={self.quantity}, {owner_id})>"

# --- END OF FILE app/db/models/item.py ---