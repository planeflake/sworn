"""add action categories and templates tables

Revision ID: add_action_categories_and_templates_tables
Revises: add_character_actions_table
Create Date: 2025-01-29 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = 'add_action_templates'
down_revision: Union[str, None] = 'add_char_actions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create action_categories table
    op.create_table('action_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('parent_category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.String(length=1000), nullable=False),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.ForeignKeyConstraint(['parent_category_id'], ['action_categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create action_templates table
    op.create_table('action_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=False),
        sa.Column('action_verb', sa.String(length=50), nullable=False),
        sa.Column('requirements', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('possible_rewards', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column('base_duration_seconds', sa.Integer(), nullable=False),
        sa.Column('difficulty_level', sa.Integer(), nullable=False),
        sa.Column('max_skill_level', sa.Integer(), nullable=True),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('flavor_text', sa.String(length=500), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('is_repeatable', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('prerequisite_action_ids', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column('unlock_world_day', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['action_categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('action_templates')
    op.drop_table('action_categories')