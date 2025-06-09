"""Add character_actions table

Revision ID: add_char_actions
Revises: add_bub_fields
Create Date: 2025-01-28 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_char_actions'
down_revision = 'add_bub_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    action_type_enum = postgresql.ENUM(
        'gather', 'build', 'craft', 'trade', 'move', 'rest',
        name='actiontype',
        create_type=False
    )
    action_type_enum.create(op.get_bind(), checkfirst=True)
    
    action_status_enum = postgresql.ENUM(
        'queued', 'in_progress', 'completed', 'failed', 'cancelled',
        name='actionstatus', 
        create_type=False
    )
    action_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create character_actions table
    op.create_table('character_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action_type', action_type_enum, nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', action_status_enum, nullable=False, server_default='queued'),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.Column('progress', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_character_actions_character_id', 'character_id'),
        sa.Index('ix_character_actions_action_type', 'action_type'),
        sa.Index('ix_character_actions_status', 'status'),
    )


def downgrade() -> None:
    # Drop table
    op.drop_table('character_actions')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS actiontype')
    op.execute('DROP TYPE IF EXISTS actionstatus')