# --- START OF FILE app/db/models/character.py ---

#Base Imports
import uuid
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any # For type hinting

# Core SQLAlchemy imports
from sqlalchemy import (
    Integer, String, DateTime, func, ForeignKey, Boolean, Enum, Text
)
# Imports for newer mapped_column syntax
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Import for specific dialects if needed (like PostgreSQL)
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.dialects.postgresql import JSONB # Use JSONB for PostgreSQL indexable JSON

#from app.game_state.models.location import LocationModel # Import related models
#from app.game_state.models.item import ItemModel

class LocationModel: pass # Placeholder for actual Location model import
class ItemModel: pass # Placeholder for actual Item model import
class SkillModel: pass # Placeholder for actual Skill model import
class PlayerAccountModel: pass # Placeholder for actual PlayerAccount model import

# Import your project's declarative base
from .base import Base

# Import for server-side UUID generation if using it
from sqlalchemy.sql import text

# --- Define Enums used in the model ---
from app.game_state.enums.character import CharacterTypeEnum, CharacterStatusEnum


class Character(Base):
    """
    SQLAlchemy ORM Model for Characters (Players and NPCs).
    This template includes examples of various field types and options.
    """
    __tablename__ = 'characters' # Choose your table name

    # --- Primary Key ---
    # Using UUID is generally recommended for IDs that might be exposed externally
    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), # Use PostgreSQL UUID type, store as Python UUID
        primary_key=True,
        # Use server_default for DB-generated UUIDs (requires extension like pgcrypto or built-in)
        server_default=text("gen_random_uuid()"),
        # Alternative if generating UUID in Python before insert:
        # default=uuid.uuid4
        # init=False # Use init=False if default is Python-side (like uuid.uuid4)
                     # Keep init=True (default) if you might provide it sometimes
                     # or rely on server_default primarily.
    )

    # --- Required Fields (Usually strings, numbers, enums) ---
    name: Mapped[str] = mapped_column(
        String(100), # Specify a reasonable length
        nullable=False,
        index=True # Index names if you search by them frequently
    )

    character_type: Mapped[CharacterTypeEnum] = mapped_column(
        Enum(CharacterTypeEnum, name="character_type_enum", create_type=False), # Link to Python Enum
        nullable=False,
        index=True # Index type if you filter by it often
    )

    # --- Optional Fields ---
    # Use Optional[] type hint and nullable=True
    description: Mapped[Optional[str]] = mapped_column(
        Text, # Use Text for longer descriptions
        nullable=True
    )

    # --- Fields with Defaults ---
    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1 # Python-side default (assigned if not provided)
        # server_default=text("1") # Alternative: DB-side default
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    status: Mapped[CharacterStatusEnum] = mapped_column(
        Enum(CharacterStatusEnum, name="character_status_enum", create_type=False),
        nullable=False,
        default=CharacterStatusEnum.ALIVE # Default Enum value
    )

    # --- Complex Types (JSON, DateTime) ---
    # Use JSONB for PostgreSQL as it's generally better (indexable)
    # Store stats, attributes, potentially simple inventory/flags
    stats: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        # Use default_factory for mutable types like dict/list
        default=lambda: {}
    )

    # Example: Storing equipment slots (could also be related tables)
    equipment: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: {}
    )

    # --- Timestamps ---
    # Use timezone=True for timezone awareness
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(), # Let the DB handle creation time
        nullable=False
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(), # Let the DB handle updates automatically
        server_default=func.now(), # Also set on creation
        nullable=True,
    )

    last_login: Mapped[Optional[datetime]] = mapped_column( # Player-specific maybe?
        DateTime(timezone=True),
        nullable=True
    )

    # --- Foreign Keys (Linking TO other tables) ---
    # Example: Link to a Player Accounts table (if separating player auth)
    # This assumes 'player_accounts.id' is the PK of your accounts table
    # This would likely only be populated if character_type == 'PLAYER'
    player_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        pgUUID(as_uuid=True),
        #ForeignKey("player_accounts.id", name="fk_character_player_account"), # Name the FK constraint
        nullable=True, # Must be nullable if NPCs don't have accounts
        unique=True, # A player account should only link to one character
        index=True
    )

    # Example: Current location (assuming a 'locations' table)
    #current_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    #   pgUUID(as_uuid=True),
    #    #ForeignKey("locations.id", name="fk_character_location"),
    #    nullable=True, # Maybe characters can be 'nowhere'?
    #    index=True
    #)

    # --- Relationships (Linking FROM other tables / defining collections) ---
    # Use relationship() to define how this model connects to others in Python code
    # These do NOT create database columns but allow ORM navigation (e.g., character.items)

    # Example: One-to-Many -> Character (one) has many Items (many)
    # Assumes an 'Item' model exists with an 'owner_character_id' ForeignKey back to 'characters.id'
    #items: Mapped[List["ItemModel"]] = relationship(
    #    "Item", # The class name of the related model (as a string if defined later)
    #    back_populates="owner", # Must match the 'relationship' name in the Item model pointing back here
    #    lazy="selectin", # Recommended loading strategy for async to avoid N+1 queries
    #    cascade="all, delete-orphan" # Example: delete items if character is deleted
    #)

    # Example: Many-to-One -> Character (many) belongs to one Location (one)
    # Links from the 'current_location_id' ForeignKey defined above
    #current_location: Mapped[Optional["LocationModel"]] = relationship(
     #   "Location", # Class name of the Location model
        # 'back_populates' links to the relationship defined on the Location model
        # (e.g., Location model might have 'characters: Mapped[List["Character"]] = relationship(..., back_populates="current_location")')
    #    back_populates="characters_at_location", # Choose a descriptive name for the other side
    #    lazy="selectin"
    #)

    # Example: Many-to-Many -> Character (many) has many Skills (many)
    # This requires an 'association table' defined elsewhere (e.g., character_skills_association)
    # The association table typically has 'character_id' and 'skill_id' foreign keys.
    #skills: Mapped[List["SkillModel"]] = relationship(
    #    "Skill", # Class name of the Skill model
    #    secondary="character_skills_association", # Name of the association table/object
    #    back_populates="characters", # Name of the relationship on the Skill model pointing back
    #    lazy="selectin"
    #)


    # --- Standard Python Methods ---
    def __repr__(self) -> str:
        return f"<Character(id={self.id!r}, name={self.name!r}, type={self.character_type.name})>"

    # Add other methods relevant to the DB model if needed,
    # but keep business logic in Managers/Services.


# --- Optional: Define Association Table for Many-to-Many ---
# (If using Many-to-Many, define the association table, often in a separate file or here)
# from sqlalchemy import Table, Column
#
# character_skills_association = Table(
#     "character_skills", # Table name in the database
#     Base.metadata,
#     Column("character_id", pgUUID(as_uuid=True), ForeignKey("characters.id"), primary_key=True),
#     Column("skill_id", pgUUID(as_uuid=True), ForeignKey("skills.id"), primary_key=True),
#     # Add other columns to the association if needed (e.g., proficiency level)
#     # Column("proficiency", Integer, nullable=False, default=1)
# )


# Remember to define related models like Item, Location, Skill, PlayerAccount elsewhere
# in your app/db/models/ directory.

# --- END OF FILE app/db/models/character.py ---