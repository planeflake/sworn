"""
Base Manager - Contains generic CRUD operations for any entity type
"""
import uuid
from typing import Optional, TypeVar, Type, Dict, Any, Generic
from datetime import datetime

# Type variable for any entity class
T = TypeVar('T')

class BaseManager(Generic[T]):
    """
    Generic base manager for common CRUD operations.
    
    This manager provides generic operations that can work with any entity type,
    not just worlds.
    """
    
    @staticmethod
    def create(entity_class: Type[T], entity_id: Optional[uuid.UUID] = None, **kwargs) -> T:
        """
        Create a new entity instance.
        
        Only passes the provided values to the entity constructor,
        relying on the entity's __init__ for default values.
        
        Args:
            entity_class: The class of entity to create
            entity_id: Optional custom ID for the entity
            **kwargs: Additional attributes to set on the entity
            
        Returns:
            A new instance of the specified entity type
        """
        # Generate UUID if no entity_id provided
        if not entity_id:
            entity_id = uuid.uuid4()
        
        # Create new entity with provided ID and optional kwargs
        # Let the entity's __init__ handle default values for unprovided fields
        entity_kwargs = {"entity_id": entity_id}
        
        # We don't need to set created_at as BaseEntity provides the default
        # Only override if explicitly provided
        entity_kwargs.update(kwargs)
        
        return entity_class(**entity_kwargs)
    
    @staticmethod
    def update(entity: T, **kwargs) -> T:
        """
        Update an existing entity with new values.
        
        Args:
            entity: The entity to update
            **kwargs: New values to set on the entity
            
        Returns:
            The updated entity
        """
        # Set updated_at timestamp
        setattr(entity, 'updated_at', datetime.now())
        
        # Update entity attributes
        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        return entity