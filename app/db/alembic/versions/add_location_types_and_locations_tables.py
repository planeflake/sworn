"""Add location_types and locations tables

Revision ID: add_location_types_locations
Revises: 752eb9568a64
Create Date: 2025-05-24 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_location_types_locations'
down_revision: Union[str, None] = '752eb9568a64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create location_types table
    op.create_table('location_types',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('theme', sa.String(length=50), nullable=True),
        sa.Column('can_contain', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('required_attributes', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
        sa.Column('optional_attributes', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
        sa.Column('icon_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code', name='uq_location_type_code')
    )
    op.create_index(op.f('ix_location_types_code'), 'location_types', ['code'], unique=True)
    op.create_index(op.f('ix_location_types_theme'), 'location_types', ['theme'], unique=False)
    
    # Create location_entities table (instead of locations to avoid conflict)
    op.create_table('location_entities',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location_type_id', sa.UUID(), nullable=False),
        sa.Column('parent_id', sa.UUID(), nullable=True),
        sa.Column('parent_type_id', sa.UUID(), nullable=True),
        sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.ForeignKeyConstraint(['location_type_id'], ['location_types.id'], name='fk_location_type'),
        sa.ForeignKeyConstraint(['parent_id'], ['location_entities.id'], name='fk_parent_location'),
        sa.ForeignKeyConstraint(['parent_type_id'], ['location_types.id'], name='fk_parent_location_type'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('(parent_id IS NULL AND parent_type_id IS NULL) OR (parent_id IS NOT NULL AND parent_type_id IS NOT NULL)', name='valid_parent_check')
    )
    op.create_index(op.f('ix_location_entities_location_type_id'), 'location_entities', ['location_type_id'], unique=False)
    op.create_index(op.f('ix_location_entities_parent_id'), 'location_entities', ['parent_id'], unique=False)
    op.create_index(op.f('ix_location_entities_name'), 'location_entities', ['name'], unique=False)
    op.create_index(op.f('ix_location_entities_is_active'), 'location_entities', ['is_active'], unique=False)
    
    # Seed initial location types
    op.execute("""
    INSERT INTO location_types (code, name, description, theme, can_contain, required_attributes, optional_attributes, tags)
    VALUES 
        ('dimension', 'Dimension', 'A distinct dimensional plane of existence', 'universal', 
         ARRAY['cosmos', 'galaxy', 'world', 'zone', 'area', 'settlement', 'elemental_plane'],
         '[]', '[]', ARRAY['universal']),
         
        ('cosmos', 'Cosmos', 'A universe or distinct reality', 'space', 
         ARRAY['galaxy', 'star_system', 'celestial_body', 'zone', 'area'],
         '[]', '[]', ARRAY['space']),
         
        ('galaxy', 'Galaxy', 'A vast collection of star systems', 'space', 
         ARRAY['star_system', 'zone', 'area', 'settlement'],
         '[{"name":"galaxy_type","type":"string","description":"Type of galaxy","enum":["spiral","elliptical","irregular","lenticular"]}]',
         '[{"name":"diameter_ly","type":"number","description":"Diameter in light years"},{"name":"star_count","type":"number","description":"Estimated number of stars"}]',
         ARRAY['space', 'astronomical']),
         
        ('star_system', 'Star System', 'A star with its orbiting bodies', 'space', 
         ARRAY['celestial_body', 'constructed_habitat', 'zone', 'area'],
         '[]', '[]', ARRAY['space']),
         
        ('celestial_body', 'Celestial Body', 'A planet, moon, or asteroid', 'space', 
         ARRAY['zone', 'area', 'settlement'],
         '[]', '[]', ARRAY['space']),
         
        ('world', 'World', 'A planet-sized realm', 'fantasy', 
         ARRAY['zone', 'area', 'settlement'],
         '[]', '[]', ARRAY['fantasy']),
         
        ('zone', 'Zone', 'A large geographical region', 'universal', 
         ARRAY['area', 'settlement'],
         '[]', '[]', ARRAY['universal']),
         
        ('area', 'Area', 'A specific location within a region', 'universal', 
         ARRAY['settlement'],
         '[]', '[]', ARRAY['universal']),
         
        ('settlement', 'Settlement', 'An inhabited location', 'universal', 
         ARRAY[]::varchar[],
         '[]', '[{"name":"population","type":"integer","description":"Number of inhabitants"}]',
         ARRAY['universal']),
         
        ('elemental_plane', 'Elemental Plane', 'A realm composed of pure elemental energy', 'elemental', 
         ARRAY['zone', 'area', 'settlement'],
         '[{"name":"elemental_type","type":"string","description":"Primary element","enum":["fire","water","earth","air","void","lightning"]}]',
         '[{"name":"temperature","type":"number"},{"name":"magical_intensity","type":"number"}]',
         ARRAY['elemental', 'magical']),
         
        ('constructed_habitat', 'Constructed Habitat', 'An artificial structure for habitation', 'space', 
         ARRAY['zone', 'area', 'settlement'],
         '[]', '[]', ARRAY['space', 'artificial'])
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('location_entities')
    op.drop_table('location_types')