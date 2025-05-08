"""
Building entity model
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class BuildingEntity():
    """ settlement state """
    id: UUID
    name: str 
    description: str
    inhabitants: int
    max_inhabitants: int
    building_type: int
    building_requirements: str
    building_level: int
    building_level_max: int
    world_id: UUID
    resources: list
    world_id: UUID
    created_at: datetime
    updated_at: datetime