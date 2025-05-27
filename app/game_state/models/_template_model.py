# --- START OF FILE app/game_state/models/_template_api_model.py ---
# Rename this file to match your specific model (e.g., building_api_model.py, item_api_model.py)

# --- Core Python Imports ---
import uuid
import enum
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any

# --- Pydantic Imports ---
from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator, model_validator, ConfigDict

# --- Import API Enums & Other API Models ---
# Use Enums defined for the API layer (might be same as domain enums)
# from app.game_state.enums import ExampleStatusEnum # Example
class ExampleStatusEnum(enum.Enum): # Placeholder definition
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

# Use other API models for nested structures
# from .related_api_model import RelatedApiModel # Example import
class RelatedApiModel(BaseModel): # Placeholder definition
    id: uuid.UUID
    name: str
    model_config = ConfigDict(from_attributes=True)

# --- API Model Definition ---
# Rename 'TemplateApiModel'
class TemplateApiModel(BaseModel):
    """
    API MODEL (DTO) TEMPLATE (Pydantic BaseModel).
    Defines the data structure for API requests/responses.
    """
    # --- Identifier ---
    # Often 'id' in API, map from 'entity_id' in domain/db model
    id: uuid.UUID = Field(..., validation_alias='entity_id', serialization_alias='id')
    # Use '...' as first arg in Field to mark as required

    # --- Basic Types (with examples of validation) ---
    name: str = Field(..., min_length=1, max_length=100) # Add validation rules
    description: Optional[str] = None # Keep None as default for optional fields
    count: Optional[int] = Field(None, ge=0) # Example: must be >= 0 if provided
    value: Optional[float] = Field(None, gt=0) # Example: must be > 0 if provided
    is_enabled: bool = True # Can provide defaults

    # --- Enum ---
    status: ExampleStatusEnum = ExampleStatusEnum.ACTIVE # Can provide default

    # --- Specialized Types (Pydantic provides many) ---
    # email: Optional[EmailStr] = None
    # website: Optional[HttpUrl] = None

    # --- Date/Time ---
    event_timestamp: Optional[datetime] = None
    start_date: Optional[date] = None

    # --- Complex Types (Dicts, Lists of primitives or nested API Models) ---
    metadata: Optional[Dict[str, Any]] = {} # Default to empty dict if usually present
    tags: Optional[List[str]] = [] # Default to empty list
    related_items: List[RelatedApiModel] = [] # Use the nested API model

    # --- Links (usually exposed as IDs) ---
    related_model_id: Optional[uuid.UUID] = None

    # --- Timestamps (Read-only often) ---
    created_at: Optional[datetime] = Field(None, description="Read-only timestamp")
    updated_at: Optional[datetime] = Field(None, description="Read-only timestamp")

    # --- Pydantic Configuration ---
    model_config = ConfigDict(
        # Essential for creating API model from Domain Entity or DB Model attributes
        from_attributes=True,

        # Essential if using aliases for validation (e.g., 'entity_id' -> 'id')
        populate_by_name=True
    )

        # Optional: Customize JSON schema generation
        # json_schema_extra = {
        #     "example": {
        #         "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        #         "name": "Example Item",
        #         "count": 10,
        #         "status": "ACTIVE",
        #         # ... other example fields
        #     }
        # }

        # Optional: Add custom validation/serialization logic if needed
        # frozen = True # Make instances immutable

    # --- Custom Validators (Optional) ---
    # Use @field_validator for single fields
    # @field_validator('name')
    # def check_name_not_default(cls, v):
    #     if v == "Default Template Name":
    #         raise ValueError("'name' cannot be the default")
    #     return v

    # Use @model_validator for checks involving multiple fields
    # @model_validator(mode='before') # or 'after'
    # def check_dates(cls, data):
    #     if isinstance(data, dict): # Check if it's dict data (before validation)
    #         start = data.get('start_date')
    #         event = data.get('event_timestamp')
    #         # ... add validation logic ...
    #     return data


# --- END OF FILE app/game_state/models/_template_api_model.py ---