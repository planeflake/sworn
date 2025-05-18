# --- START OF FILE app/db/models/_template_model.py ---
# Rename this file to match your specific model (e.g., building.py, item.py)

# --- Core Python Imports ---
import uuid         # For generating/handling UUIDs in Python defaults       # For creating Enumerated types (like status or type fields)
from datetime import datetime # For timestamp fields
#from idlelib.format import FormatRegion
from typing import Optional, List, Dict, Any # For Python type hinting (improves code readability and tooling)
from app.game_state.enums.shared import StatusEnum

class RelatedModel: pass # Placeholder for actual related model import (e.g., ItemModel, LocationModel)

# --- Core SQLAlchemy Imports ---
from sqlalchemy import (
    Integer,        # Standard integer type
    String,         # Variable-length string (requires length usually)
    Text,           # Arbitrary-length text
    DateTime,       # Date and Time (consider timezone=True)
    Date,           # Date only
    Enum,           # Store Python Enum values (maps to VARCHAR or native ENUM)
    ForeignKey,     # For defining relationships between tables
    UniqueConstraint,# For defining multi-column uniqueness
    CheckConstraint,# For database-level value checks
    Index,          # For creating database indexes explicitly
    func            # For SQL functions (like func.now() for timestamps)
)
# Imports for newer mapped_column syntax (SQLAlchemy 2.0+)
from sqlalchemy.orm import (
    Mapped,         # Type hint for mapped attributes
    mapped_column,  # The primary way to define table columns
    relationship    # For defining relationships between models in the ORM
)
from sqlalchemy.dialects import postgresql as pg

# Import for specific dialects (especially PostgresSQL)
from sqlalchemy.dialects.postgresql import (
    JSONB,          # PostgresSQL binary JSON (indexed, preferred over JSON)
    ARRAY           # PostgresSQL array type (can store lists of strings, ints etc.)
)
# Import your project's declarative base class
from .base import Base # Assumes you have 'base.py' defining 'Base = declarative_base()'
# Import for server-side default generation (like UUIDs or sequences)
from sqlalchemy.sql import text

# --- Model Definition ---
# Rename 'TemplateModel' to your specific model name (e.g., Building, Item)
class Faction(Base):
    """
    SQLAlchemy ORM Model Template for Factions
    """
    __tablename__ = 'factions' # <<< REPLACE with actual table name

    # --- Example Primary Key ---
    # UUID is common for distributed systems or external exposure
    id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),   # Use native PG UUID, return Python UUID objects
        primary_key=True,       # Marks this as the primary key column
        server_default=text("gen_random_uuid()"), # DB generates default UUID (PG specific)
        # default=uuid.uuid4,   # Alternative: Python generates default UUID (use with init=False)
        # init=False            # Use if default is Python-side (like uuid.uuid4)
    )
    # Integer PK alternative (classic approach, often used with auto-increment)
    # id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # --- Example Basic Types ---
    name: Mapped[str] = mapped_column(
        String(100),            # VARCHAR(100), always specify length for String
        nullable=False,         # Column cannot be NULL
        index=True,             # Create a database index on this column
        unique=True             # Ensure all values in this column are unique
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,                   # Use Text for potentially long strings
        nullable=True           # Allows NULL values (default is False if not specified)
    )

    # --- Example Enum ---
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, name="status_enum", create_type=False), # Maps Python Enum to DB type
        nullable=False,
        default=StatusEnum.PENDING, # Default to one of the Enum members
        index=True
        # create_type=False: Assumes the ENUM type exists in DB (manage via migrations)
        # create_type=True: SQLAlchemy tries to create the ENUM type (can cause issues)
    )

    icon_path: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=""
    )

    member_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    leader_last_changed: Mapped[Optional[Date]] = mapped_column(
        Date,
        nullable=True
    )

    theme: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("themes.id", name="faction_theme_id"),
        nullable = True
    )

    # Timestamps for record tracking (usually init=False, handled by DB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(), # DB function for current time
        nullable=False
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),    # DB function updates this on every UPDATE statement
        server_default=func.now(),# Set on creation too
        nullable=True
    )

    # --- Example Complex Types (PostgreSQL Specific) ---
    # Store structured data directly in a column
    _metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,                  # Use JSONB for PostgreSQL (indexed)
        nullable=True,
        default=lambda: {}
    )

    tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),          # PostgreSQL Array of strings
        nullable=True,
        default=lambda: []
    )
    # Example: ARRAY(Integer) for a list of numbers


    # --- Example Relationship (defined via Foreign Key above) ---
    # Allows ORM navigation (e.g., my_template.related_model)
    # Assumes a 'RelatedModel' class exists.
    related_model: Mapped["RelatedModel"] = relationship(
        "RelatedModel",         # Target class name (string if defined later)
        back_populates="template_models", # Matches 'relationship' name in RelatedModel pointing back
        lazy="selectin",        # Good default loading strategy for async
        # innerjoin=True,       # Optional: Use INNER JOIN instead of LEFT OUTER JOIN for loading
    )

    # --- Table Arguments (Constraints, Indexes beyond single columns) ---
    __table_args__ = (
        # Example: Ensure combination of 'name' and 'related_model_id' is unique
        UniqueConstraint('name', 'id', name='uq_template_name_related'),
        # Example: Ensure 'value' is always non-negative
        CheckConstraint('value >= 0', name='chk_template_value_positive'),
        # Example: Multi-column index
        #Index('ix_template_status_date', 'status', 'event_timestamp'),
        # Example: Add schema specification if needed
        # {'schema': 'my_schema'}
    )

    # --- Standard Python Methods ---
    def __repr__(self) -> str:
        # Customize this for useful representation during debugging
        return f"<{self.__class__.__name__}(id={self.id!r}, name={self.name!r})>"

# --- Don't forget to define the "RelatedModel" class referenced above! ---
# class RelatedModel(Base):
#     __tablename__ = 'related_models'
#     id: Mapped[uuid.UUID] = mapped_column(pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
#     # ... other fields ...
#     # Relationship back to TemplateModel
#     template_models: Mapped[List["TemplateModel"]] = relationship(
#         "TemplateModel",
#         back_populates="related_model",
#         lazy="selectin"
#     )

# --- END OF FILE app/db/models/_template_model.py ---