import uuid
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

# Many-to-many association table between zones and themes
zone_theme_association = Table(
    'zone_theme_association',
    Base.metadata,
    Column('zone_id', UUID(as_uuid=True), ForeignKey('zones.id'), primary_key=True),
    Column('theme_id', UUID(as_uuid=True), ForeignKey('themes.id'), primary_key=True)
)