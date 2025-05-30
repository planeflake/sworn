"""add metadata field to skill_definitions table

Revision ID: 37da347a5033
Revises: b5e2d7a9c12f
Create Date: 2025-05-17 03:36:45.831044

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '37da347a5033'
down_revision: Union[str, None] = 'b5e2d7a9c12f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # First create the character_trait_enum type
    character_trait_enum = sa.Enum('DEFENSIVE', 'AGGRESSIVE', 'SUPPORTIVE', 'STRATEGIC', 'ECONOMICAL', 'EXPANSIVE', 'CULTURAL', 'SPIRITUAL', name='character_trait_enum')
    character_trait_enum.create(op.get_bind(), checkfirst=True)
    
    # Now we can add the columns safely
    op.add_column('characters', sa.Column('character_traits', character_trait_enum, nullable=True))
    op.create_index(op.f('ix_characters_character_traits'), 'characters', ['character_traits'], unique=False)
    op.add_column('skill_definitions', sa.Column('_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Additional data like XP curve type, related stats, etc.'))
    op.add_column('skills', sa.Column('category', sa.String(length=100), nullable=True))
    op.add_column('skills', sa.Column('icon_path', sa.String(length=255), nullable=True))
    op.add_column('skills', sa.Column('status', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('skills', 'status')
    op.drop_column('skills', 'icon_path')
    op.drop_column('skills', 'category')
    op.drop_column('skill_definitions', '_metadata')
    op.drop_index(op.f('ix_characters_character_traits'), table_name='characters')
    op.drop_column('characters', 'character_traits')
    
    # Finally, drop the enum type
    sa.Enum(name='character_trait_enum').drop(op.get_bind(), checkfirst=True)
    # ### end Alembic commands ###
