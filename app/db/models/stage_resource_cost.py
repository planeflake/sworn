# --- START OF FILE app/db/models/stage_resource_cost.py ---

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID

from .base import Base
# Import related models only for type hints if needed
if TYPE_CHECKING:
    from .blueprint_stage import BlueprintStage
    from .resource import Resource # Assuming you have resource.py

class StageResourceCost(Base):
    """
    Association object linking a BlueprintStage to a Resource required
    for that stage, including the count.
    """
    __tablename__ = 'stage_resource_costs'

    blueprint_stage_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("blueprint_stages.id", name="fk_resource_cost_stage_id", ondelete="CASCADE"),
        primary_key=True # Part of composite PK
    )

    resource_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("resources.id", name="fk_resource_cost_resource_id", ondelete="CASCADE"), # Assumes resources table and UUID PK
        primary_key=True # Part of composite PK
    )

    count: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Number of units of this resource required for the stage."
    )

    # Optional: Relationships for easy ORM navigation
    stage: Mapped["BlueprintStage"] = relationship(
        "BlueprintStage",
        back_populates="resource_costs"
    )
    resource: Mapped["Resource"] = relationship( # Assumes Resource model exists
        "Resource",
        lazy="joined" # Or selectin; joined might be okay for simple lookups
        # No back_populates needed unless Resource needs to know all stages it's used in
    )

    # Define composite primary key constraint explicitly (SQLAlchemy >= 1.4 often infers)
    __table_args__ = (
        PrimaryKeyConstraint('blueprint_stage_id', 'resource_id', name='pk_stage_resource_costs'),
        # {'schema': 'my_schema'}
    )

    def __repr__(self) -> str:
        return f"<StageResourceCost(stage={self.blueprint_stage_id!r}, resource={self.resource_id!r}, count={self.count})>"

# --- END OF FILE app/db/models/stage_resource_cost.py ---