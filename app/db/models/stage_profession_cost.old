# --- START OF FILE app/db/models/stage_profession_cost.py ---

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID

from .base import Base
# Import related models only for type hints if needed
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .blueprint_stage import BlueprintStage

class StageProfessionCost(Base):
    """
    Association object linking a BlueprintStage to a Profession required
    for that stage, including the number of workers.
    Professions are identified by their string name/ID.
    """
    __tablename__ = 'stage_profession_costs'

    blueprint_stage_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("blueprint_stages.id", name="fk_profession_cost_stage_id", ondelete="CASCADE"),
        primary_key=True # Part of composite PK
    )

    # Store the profession identifier as a string.
    # If you later create a ProfessionDefinitions table with a UUID PK, change this to:
    # profession_definition_id: Mapped[uuid.UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey("profession_definitions.id"), primary_key=True)
    profession_name: Mapped[str] = mapped_column(
        String(100), # Adjust length as needed for profession names/IDs
        primary_key=True, # Part of composite PK
        index=True
    )

    count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default='1',
        comment="Number of workers with this profession required for the stage."
    )

    # Optional: Relationship back to the stage
    stage: Mapped["BlueprintStage"] = relationship(
        "BlueprintStage",
        back_populates="profession_costs"
    )

    # Note: No direct ORM relationship for profession_name unless you have a mapped ProfessionDefinition table.

    # Define composite primary key constraint explicitly
    __table_args__ = (
        PrimaryKeyConstraint('blueprint_stage_id', 'profession_name', name='pk_stage_profession_costs'),
        # {'schema': 'my_schema'}
    )

    def __repr__(self) -> str:
        return f"<StageProfessionCost(stage={self.blueprint_stage_id!r}, profession='{self.profession_name}', count={self.count})>"

# --- END OF FILE app/db/models/stage_profession_cost.py ---