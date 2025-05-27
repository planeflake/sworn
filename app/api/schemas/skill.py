
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class SkillRead(BaseModel):
    id: UUID = Field(None, description="Unique ID of the world.")
    name: str = Field(None, max_length=100, description="A name of the world.")
    description: str  = Field(None, max_length=1000, description="A description of the world.")
    category: str = Field(None, description="Current game day in the world.")
    max_level: int

    model_config = ConfigDict(from_attributes=True)

class SkillCreate(BaseModel):
    id: UUID = Field(None, description="Unique ID of the world.")
    name: str = Field(None, max_length=100, description="A name of the world.")
    description: str = Field(None, max_length=1000, description="A description of the world.")
    category: str = Field(None, description="Current game day in the world.")
    max_level: int = Field(None, description="Maximum level of the skill.", ge=1)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Swordsmanship",
                "description": "Improves skill with swords and blades.",
                "category": "Combat",
                "max_level": 10
            }
        }
    )

class SkillCreateResponse(BaseModel):
    message: str
    Skill: SkillRead