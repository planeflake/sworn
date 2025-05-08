# --- START OF FILE app/db/models/_template_model.py ---
# Rename this file to match your specific model (e.g., building.py, item.py)

# --- Core Python Imports ---
import uuid         # For generating/handling UUIDs in Python defaults
import enum         # For creating Enumerated types (like status or type fields)
from datetime import datetime # For timestamp fields
from typing import Optional, List, Dict, Any # For Python type hinting (improves code readability and tooling)

class RelatedModel: pass # Placeholder for actual related model import (e.g., ItemModel, LocationModel)

# --- Core SQLAlchemy Imports ---
from sqlalchemy import (
    Integer,        # Standard integer type
    BigInteger,     # Larger integer type
    SmallInteger,   # Smaller integer type
    String,         # Variable-length string (requires length usually)
    Text,           # Arbitrary-length text
    Boolean,        # True/False values
    Float,          # Floating point numbers
    Numeric,        # Fixed-precision decimal numbers (good for currency)
    DateTime,       # Date and Time (consider timezone=True)
    Date,           # Date only
    Time,           # Time only (consider timezone=True)
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
# Import for specific dialects (especially PostgreSQL)
from sqlalchemy.dialects.postgresql import (
    UUID as pgUUID, # PostgreSQL native UUID type
    JSONB,          # PostgreSQL binary JSON (indexed, preferred over JSON)
    ARRAY           # PostgreSQL array type (can store lists of strings, ints etc.)
)
# Import your project's declarative base class
from .base import Base # Assumes you have 'base.py' defining 'Base = declarative_base()'
# Import for server-side default generation (like UUIDs or sequences)
from sqlalchemy.sql import text

# --- Optional: Define Enums used specifically by this model ---
# It's often better to define Enums in a central 'types.py' or similar
class ExampleStatusEnum(enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"

# --- Model Definition ---
# Rename 'TemplateModel' to your specific model name (e.g., Building, Item)
class TemplateModel(Base):
    """
    SQLAlchemy ORM Model Template.
    Replace 'TemplateModel' and table name. Use fields below as examples.
    """
    __tablename__ = 'your_table_name' # <<< REPLACE with actual table name

    # --- Example Primary Key ---
    # UUID is common for distributed systems or external exposure
    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),   # Use native PG UUID, return Python UUID objects
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

    count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
        # default=0             # Example Python-side default
    )

    value: Mapped[Optional[float]] = mapped_column(
        Float,                  # Standard float, precision can vary by DB backend
        nullable=True
    )

    price: Mapped[Optional[Any]] = mapped_column( # Use Any if precision matters significantly
        Numeric(10, 2),         # Example: DECIMAL(10, 2) - 10 total digits, 2 after decimal
        nullable=True
    )

    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,           # Python-side default for new objects
        server_default='true'   # DB-level default for rows inserted via raw SQL etc.
    )

    # --- Example Enum ---
    status: Mapped[ExampleStatusEnum] = mapped_column(
        Enum(ExampleStatusEnum, name="example_status_enum", create_type=False), # Maps Python Enum to DB type
        nullable=False,
        default=ExampleStatusEnum.PENDING, # Default to one of the Enum members
        index=True
        # create_type=False: Assumes the ENUM type exists in DB (manage via migrations)
        # create_type=True: SQLAlchemy tries to create the ENUM type (can cause issues)
    )

    # --- Example Date/Time ---
    # Store with timezone information!
    event_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    start_date: Mapped[Optional[Date]] = mapped_column(
        Date,
        nullable=True
    )

    # Timestamps for record tracking (usually init=False, handled by DB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(), # DB function for current time
        nullable=False,
        init=False              # Exclude from Python __init__
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),    # DB function updates this on every UPDATE statement
        server_default=func.now(),# Set on creation too
        nullable=True,          # Optional, based on requirements
        init=False              # Exclude from Python __init__
    )

    # --- Example Complex Types (PostgreSQL Specific) ---
    # Store structured data directly in a column
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,                  # Use JSONB for PostgreSQL (indexed)
        nullable=True,
        default=lambda: {},     # Use default_factory for mutable types like dict
        init=False              # Often excluded from init
    )

    tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),          # PostgreSQL Array of strings
        nullable=True,
        default=lambda: [],     # Use default_factory for mutable lists
        init=False
    )
    # Example: ARRAY(Integer) for a list of numbers

    # --- Example Foreign Key ---
    # Links this table to another table ('related_models')
    related_model_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("related_models.id", name="fk_template_related"), # Specify target table.column and constraint name
        nullable=False,         # Or True if the relationship is optional
        index=True              # Often good to index FKs
    )

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
        UniqueConstraint('name', 'related_model_id', name='uq_template_name_related'),
        # Example: Ensure 'value' is always non-negative
        CheckConstraint('value >= 0', name='chk_template_value_positive'),
        # Example: Multi-column index
        Index('ix_template_status_date', 'status', 'event_timestamp'),
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