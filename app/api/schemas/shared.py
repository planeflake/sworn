# app/api/schemas/shared.py (or a common place for shared schemas)
from pydantic import BaseModel, Field
from typing import List, TypeVar, Generic, Optional

DataType = TypeVar('DataType')

class PaginatedResponse(BaseModel, Generic[DataType]):
    items: List[DataType]
    total: int
    limit: int
    skip: int
    page: Optional[int] = None # If you want to include page number
    pages: Optional[int] = None # If you want to include total pages

    model_config = { # Pydantic v2
        "from_attributes": True
    }