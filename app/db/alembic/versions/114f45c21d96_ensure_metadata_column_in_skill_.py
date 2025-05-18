"""ensure_metadata_column_in_skill_definitions

Revision ID: 114f45c21d96
Revises: 37da347a5033
Create Date: 2025-05-17 11:59:04.992759

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '114f45c21d96'
down_revision: Union[str, None] = '37da347a5033'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if the _metadata column exists, if not rename metadata to _metadata or add _metadata
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('skill_definitions')]
    
    if '_metadata' not in columns:
        if 'metadata' in columns:
            # Rename metadata to _metadata
            op.alter_column('skill_definitions', 'metadata', new_column_name='_metadata', 
                           existing_type=sa.dialects.postgresql.JSONB)
        else:
            # Add _metadata column if neither exists
            from sqlalchemy.dialects import postgresql
            op.add_column('skill_definitions', 
                         sa.Column('_metadata', postgresql.JSONB(), nullable=True, 
                                  comment='Additional data like XP curve type, related stats, etc.'))


def downgrade() -> None:
    """Downgrade schema."""
    # We won't truly downgrade since this is a column naming fix
    pass
