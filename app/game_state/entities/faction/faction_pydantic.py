from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import Field, ConfigDict

from app.game_state.enums.shared import StatusEnum
from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class FactionEntityPydantic(BaseEntityPydantic):
    id: UUID
    name: str
    description: Optional[str] = None
    status: StatusEnum = StatusEnum.ACTIVE
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {}
        }
    )