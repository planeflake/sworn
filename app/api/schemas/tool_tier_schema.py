from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID


class ToolTierCreateSchema(BaseModel):
    """Schema for creating tool tiers."""
    name: str = Field(..., min_length=1, max_length=255)
    theme_id: UUID
    tier_name: str = Field(..., min_length=1, max_length=100)
    tier_level: int = Field(..., ge=1, le=10)
    effectiveness_multiplier: float = Field(1.0, ge=0.1, le=10.0)
    description: str = ""
    icon: Optional[str] = None
    required_tech_level: int = Field(0, ge=0)
    required_materials: List[UUID] = Field(default_factory=list)
    flavor_text: Optional[str] = None
    color_hex: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Steel Tools",
                "theme_id": "123e4567-e89b-12d3-a456-426614174000",
                "tier_name": "Steel",
                "tier_level": 3,
                "effectiveness_multiplier": 1.5,
                "description": "High-quality steel craftsmanship",
                "required_tech_level": 2,
                "color_hex": "#4682B4",
                "flavor_text": "Forged with precision and care"
            }
        }
    )


class ToolTierUpdateSchema(BaseModel):
    """Schema for updating tool tiers."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    tier_name: Optional[str] = Field(None, min_length=1, max_length=100)
    tier_level: Optional[int] = Field(None, ge=1, le=10)
    effectiveness_multiplier: Optional[float] = Field(None, ge=0.1, le=10.0)
    description: Optional[str] = None
    icon: Optional[str] = None
    required_tech_level: Optional[int] = Field(None, ge=0)
    required_materials: Optional[List[UUID]] = None
    flavor_text: Optional[str] = None
    color_hex: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')


class ToolTierResponseSchema(BaseModel):
    """Schema for tool tier responses."""
    entity_id: UUID
    name: str
    theme_id: UUID
    tier_name: str
    tier_level: int
    effectiveness_multiplier: float
    description: str
    icon: Optional[str]
    required_tech_level: int
    required_materials: List[UUID]
    flavor_text: Optional[str]
    color_hex: Optional[str]


class ThemeProgressionCreateSchema(BaseModel):
    """Schema for creating a complete theme progression."""
    theme_id: UUID
    theme_name: str = Field(..., description="Theme name (fantasy, sci-fi, post-apocalyptic, lovecraftian)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "theme_id": "123e4567-e89b-12d3-a456-426614174000",
                "theme_name": "fantasy"
            }
        }
    )


class ToolTierProgressionResponseSchema(BaseModel):
    """Schema for complete tool tier progression response."""
    theme_id: UUID
    theme_name: str
    tiers: List[ToolTierResponseSchema]
    total_tiers: int