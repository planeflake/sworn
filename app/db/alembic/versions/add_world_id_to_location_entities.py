"""Add world_id to location_entities table

Revision ID: add_world_id_to_location_entities
Revises: add_location_types_locations
Create Date: 2025-05-24 23:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_world_id_to_location'
down_revision: Union[str, None] = 'add_location_types_locations'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add world_id column to location_entities table."""
    # Add world_id column to location_entities
    op.add_column('location_entities',
        sa.Column('world_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_location_world_id',
        'location_entities', 'worlds',
        ['world_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Create index
    op.create_index(
        'ix_location_entities_world_id',
        'location_entities', ['world_id']
    )


def downgrade() -> None:
    """Remove world_id column from location_entities table."""
    # Drop foreign key constraint
    op.drop_constraint('fk_location_world_id', 'location_entities', type_='foreignkey')
    
    # Drop index
    op.drop_index('ix_location_entities_world_id', table_name='location_entities')
    
    # Drop column
    op.drop_column('location_entities', 'world_id')