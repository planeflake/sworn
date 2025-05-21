# app/db/models/resources/resource_node_link.py


from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.sql.sqltypes import Boolean, Float, Integer, String

from ..base import Base

class ResourceNodeResource(Base):
    __tablename__ = "resource_node_resources"

    node_id = mapped_column(ForeignKey("resource_nodes.id"), primary_key=True)
    resource_id = mapped_column(ForeignKey("resources.id"), primary_key=True)

    is_primary = mapped_column(Boolean, default=True)  # primary or secondary
    chance = mapped_column(Float, default=1.0)          # 1.0 = 100%, 0.15 = 15%
    amount_min = mapped_column(Integer, default=1)
    amount_max = mapped_column(Integer, default=1)
    purity = mapped_column(Float, default=1.0)
    rarity = mapped_column(String, default="common")

    node = relationship("ResourceNode", back_populates="resource_links")
    resource = relationship("Resource", back_populates="node_links")
