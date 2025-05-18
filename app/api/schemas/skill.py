
from pydantic import BaseModel

class SkillRead(BaseModel):
    id: int
    name: str
    description: str
    category: str
    max_level: int

    class Config:
        has_attributes = True

class SkillCreate(BaseModel):
    name: str
    description: str
    category: str
    max_level: int

    class Config:
        has_attributes = True

class SkillCreateResponse(BaseModel):
    message: str
    Skill: SkillRead