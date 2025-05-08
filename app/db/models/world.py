from sqlalchemy import Column,Integer,String,DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from .base import Base

class World(Base):
    """World model for SQLAlchemy ORM"""
    __tablename__ = 'worlds'

    id: Mapped[UUID] = mapped_column(
    UUID, 
    primary_key=True,
    server_default=text("gen_random_uuid()"),  # PostgreSQL function to generate UUID
    )
    theme_id: Mapped[UUID] = mapped_column(UUID, nullable=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, default="Default World")
    day: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    season: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    #settlements: Mapped[list] = mapped_column(String(50), nullable=True, default="[]")
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        """
            String representation of the World object for debugging/logging
            Shows field values in a readable format
        """
        return f"<World(id={self.id}, name={self.name}, day={self.day}, season={self.season})>"
    
    def __eq__(self, other: object) -> bool:
        """
            Equality check for World objects
            Compares two World objects based on their attributes
            Returns True if all attributes match, False otherwise    
        """
        if not isinstance(other, World):
            return NotImplemented
        return self.id == other.id and self.name == other.name and self.day == other.day and self.season == other.season
    
    def __to_dict__(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "day": self.day,
            "season": self.season,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }