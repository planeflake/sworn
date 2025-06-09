"""add_unique_constraint_biome_id

Revision ID: fbb8882d1992
Revises: dff1ba0b778a
Create Date: 2025-06-02 02:22:35.614009

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fbb8882d1992'
down_revision: Union[str, None] = 'dff1ba0b778a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique constraint to biome_id column in biomes table."""
    # Add unique constraint on biome_id column
    op.create_unique_constraint(
        'uq_biomes_biome_id',  # Constraint name
        'biomes',              # Table name
        ['biome_id']           # Column(s)
    )


def downgrade() -> None:
    """Remove unique constraint from biome_id column."""
    # Drop the unique constraint
    op.drop_constraint(
        'uq_biomes_biome_id',  # Constraint name
        'biomes',              # Table name
        type_='unique'
    )
