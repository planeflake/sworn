"""merge heads

Revision ID: ffadf0df7a98
Revises: add_world_id_to_location, add_tool_tiers
Create Date: 2025-05-31 03:00:39.121642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffadf0df7a98'
down_revision: Union[str, None] = ('add_world_id_to_location', 'add_tool_tiers')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
