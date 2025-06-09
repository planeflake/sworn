"""Fix genre enum values to uppercase

Revision ID: [new_revision_id]
Revises: 9fbe3e39a9e1
Create Date: [current_timestamp]

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '[new_revision_id]'  # Generate new ID
down_revision: Union[str, None] = '9fbe3e39a9e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix genre enum to use uppercase values."""

    # Drop the existing column first
    op.drop_column('themes', 'genre')

    # Drop the old enum type
    op.execute("DROP TYPE IF EXISTS genre")

    # Create new enum with uppercase values
    genre_enum = postgresql.ENUM(
        'FANTASY',
        'SCI_FI',
        'MODERN',
        'HISTORICAL',
        'HORROR',
        'STEAMPUNK',
        'POST_APOCALYPTIC',
        'CYBERPUNK',
        'PREHISTORIC',
        'VICTORIAN',
        name='genre'
    )
    genre_enum.create(op.get_bind())

    # Add the column back with correct enum
    op.add_column('themes', sa.Column('genre', genre_enum, nullable=True))


def downgrade() -> None:
    """Revert to the previous broken state."""

    # Drop the column
    op.drop_column('themes', 'genre')

    # Drop the enum
    op.execute("DROP TYPE IF EXISTS genre")

    # Recreate the old broken enum (for consistency with previous migration)
    genre_enum = postgresql.ENUM(
        'fantasy',
        'sci_fi',
        'modern',
        'historical',
        'horror',
        'steampunk',
        'post_apocalyptic',
        'cyberpunk',
        'prehistoric',
        'victorian',
        name='genre'
    )
    genre_enum.create(op.get_bind())

    # Add back the column with mismatched enum
    op.add_column('themes', sa.Column('genre', sa.Enum('FANTASY', 'SCI_FI', 'MODERN', 'HISTORICAL', 'MYSTICAL', 'STEAMPUNK', 'POST_APOCALYPTIC', 'COSMIC', 'PREHISTORIC', 'VICTORIAN', name='genre'), nullable=True))