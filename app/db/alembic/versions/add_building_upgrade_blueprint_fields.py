"""Add parent_blueprint_id, stage, and construction_time to building_upgrade_blueprints

Revision ID: add_bub_fields
Revises: af29366a6cd6
Create Date: 2025-01-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_bub_fields'
down_revision = 'af29366a6cd6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to building_upgrade_blueprints table
    op.add_column('building_upgrade_blueprints', sa.Column('parent_blueprint_id', sa.String(length=150), nullable=True))
    op.add_column('building_upgrade_blueprints', sa.Column('stage', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('building_upgrade_blueprints', sa.Column('construction_time', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    # Remove the columns
    op.drop_column('building_upgrade_blueprints', 'construction_time')
    op.drop_column('building_upgrade_blueprints', 'stage')
    op.drop_column('building_upgrade_blueprints', 'parent_blueprint_id')