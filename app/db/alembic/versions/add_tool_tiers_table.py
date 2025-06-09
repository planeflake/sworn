"""add tool_tiers table

Revision ID: add_tool_tiers
Revises: add_action_templates
Create Date: 2025-01-29 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = 'add_tool_tiers'
down_revision: Union[str, None] = 'add_action_templates'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tool_tiers table
    op.create_table('tool_tiers',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('theme_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tier_name', sa.String(length=100), nullable=False),
        sa.Column('tier_level', sa.Integer(), nullable=False),
        sa.Column('effectiveness_multiplier', sa.Float(), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=False),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('required_tech_level', sa.Integer(), nullable=False),
        sa.Column('required_materials', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column('flavor_text', sa.String(length=500), nullable=True),
        sa.Column('color_hex', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.ForeignKeyConstraint(['theme_id'], ['themes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for common queries
    op.create_index('ix_tool_tiers_theme_id', 'tool_tiers', ['theme_id'])
    op.create_index('ix_tool_tiers_tier_level', 'tool_tiers', ['tier_level'])
    op.create_index('ix_tool_tiers_required_tech_level', 'tool_tiers', ['required_tech_level'])


def downgrade() -> None:
    op.drop_index('ix_tool_tiers_required_tech_level', table_name='tool_tiers')
    op.drop_index('ix_tool_tiers_tier_level', table_name='tool_tiers')
    op.drop_index('ix_tool_tiers_theme_id', table_name='tool_tiers')
    op.drop_table('tool_tiers')