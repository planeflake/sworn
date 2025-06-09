from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from app.game_state.enums.shared import RarityEnum

class LocationSubtype(BaseModel):
    """
    Pydantic model for location subtypes within each location type and theme.
    Links to both the parent location type and theme.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the subtype")

    # Core identification
    code: str = Field(..., description="Unique code identifier for the subtype (e.g., 'spiral_galaxy')")
    name: str = Field(..., description="Human-readable name (e.g., 'Spiral Galaxy')")
    description: str = Field(..., description="Detailed description of this subtype")

    # Relationships
    location_type_id: UUID = Field(..., description="Reference to the parent location type")
    theme_id: UUID = Field(..., description="Reference to the theme this subtype belongs to")

    # Subtype-specific attributes
    required_attributes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Attributes that must be present for this subtype"
    )
    optional_attributes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Attributes that may be present for this subtype"
    )

    # Visual and categorization
    icon_path: Optional[str] = Field(default=None, description="Path to icon file for this subtype")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization and filtering")

    # Gameplay mechanics
    rarity: Optional[str] = Field(
        default="common",
        description="How common this subtype is (common, uncommon, rare, legendary)"
    )
    generation_weight: float = Field(
        default=1.0,
        description="Weight for procedural generation (higher = more likely to be generated)"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)

    # Configuration
    class Config:
        # Use enum values for serialization
        use_enum_values = True
        # Allow population by field name or alias
        allow_population_by_field_name = True
        # Generate schema with examples
        schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "code": "spiral_galaxy",
                "name": "Spiral Galaxy",
                "description": "A galaxy with spiral arms extending from a central bulge",
                "location_type_id": "503879ac-acc4-43d6-afa4-29d4a5bb2348",
                "theme_id": "theme-uuid-here",
                "required_attributes": [
                    {
                        "name": "arm_count",
                        "type": "integer",
                        "description": "Number of spiral arms",
                        "min_value": 2,
                        "max_value": 8
                    }
                ],
                "optional_attributes": [
                    {
                        "name": "central_black_hole_mass",
                        "type": "number",
                        "description": "Mass of central black hole in solar masses"
                    }
                ],
                "icon_path": "/icons/spiral_galaxy.svg",
                "tags": ["astronomical", "spiral", "common"],
                "rarity": "common",
                "generation_weight": 1.0
            }
        }

