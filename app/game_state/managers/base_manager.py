"""
Base Manager - Contains generic CRUD operations for any entity type
"""
import uuid
from typing import Optional, TypeVar, Type, Dict, Any, Generic

# Type variable for any entity class
T = TypeVar('T')

class BaseManager(Generic[T]):
    """
    Generic base manager for common CRUD operations.
    
    This manager provides generic operations that can work with any entity type,
    not just worlds.
    """
    
    @staticmethod
    def create(entity_class: Type[T], id: Optional[str] = None, **kwargs) -> T:
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
        if not id:
            id = str(uuid.uuid4())
        
        # Create new entity with provided ID and optional kwargs
        # Let the entity's __init__ handle default values for unprovided fields
        entity_kwargs = {"entity_id": id}
        entity_kwargs.update(kwargs)
        
        return entity_class(**entity_kwargs)