"""
Model Analyzer Module

Extracts field information and metadata from SQLAlchemy models using introspection.
"""

import inspect
import logging
from typing import Dict, List, Any, Type, Optional
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import DeclarativeBase
from importlib import import_module

# Type mapping from SQLAlchemy to Python types
TYPE_MAPPING = {
    'Integer': 'int',
    'SmallInteger': 'int',
    'BigInteger': 'int',
    'Float': 'float',
    'Numeric': 'float',
    'String': 'str',
    'Text': 'str',
    'Boolean': 'bool',
    'DateTime': 'datetime',
    'Date': 'date',
    'Time': 'time',
    'Interval': 'timedelta',
    'Enum': 'str',  # Could be more specific based on enum values
    'UUID': 'UUID',
    'ARRAY': 'List',
    'JSON': 'Dict[str, Any]',
    'JSONB': 'Dict[str, Any]',
    'LargeBinary': 'bytes',
}

# Map SQLAlchemy type to Python type
def map_sqlalchemy_to_python_type(sa_type: Any) -> str:
    """Map a SQLAlchemy type to its corresponding Python type."""
    type_name = sa_type.__class__.__name__
    
    # Handle dialect-specific types
    if hasattr(sa_type, '__visit_name__'):
        dialect_name = sa_type.__visit_name__
        if dialect_name == 'UUID':
            return 'UUID'
        elif dialect_name == 'JSONB':
            return 'Dict[str, Any]'
    
    # Use mapping or default to Any
    return TYPE_MAPPING.get(type_name, 'Any')

def get_default_value(column: Any) -> str:
    """Convert a SQLAlchemy column default to a Python default expression as string."""
    if column.default is None:
        if column.nullable:
            return 'None'
        else:
            return 'field(default_factory=lambda: ...)'
    
    # Handle callable defaults
    if column.default.is_callable:
        return 'field(default_factory=lambda: ...)'
    
    # Handle scalar defaults
    if column.default.is_scalar:
        value = column.default.arg
        if isinstance(value, str):
            return f'"{value}"'
        elif value is None:
            return 'None'
        elif isinstance(value, bool):
            return str(value)
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            return 'field(default_factory=lambda: ...)'
    
    return 'field(default_factory=lambda: ...)'

def get_model_class(model_path: str) -> Type[DeclarativeBase]:
    """Load a SQLAlchemy model class from its import path."""
    try:
        module_path, class_name = model_path.rsplit('.', 1)
        module = import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        logging.error(f"Failed to import model {model_path}: {e}")
        raise ImportError(f"Could not import model class {model_path}") from e

def analyze_model(config) -> Dict[str, Any]:
    """
    Analyze a SQLAlchemy model and extract field information.
    
    Args:
        config: The generator configuration with model information
        
    Returns a dictionary with:
    - model_name: Name of the model class
    - table_name: Name of the database table
    - fields: List of dictionaries with field information
    - relationships: List of dictionaries with relationship information
    """
    # Import model class from module path
    if config.model_module:
        model_class = get_model_class(f"{config.model_module}.{config.model_class_name}")
    else:
        # Try to guess the model module from model name
        try:
            model_class = get_model_class(f"app.db.models.{config.model_class_name.lower()}.{config.model_class_name}")
        except ImportError:
            # Try with the base models package
            model_class = get_model_class(f"app.db.models.{config.model_class_name}")
    """
    Analyze a SQLAlchemy model and extract field information.
    
    Returns a dictionary with:
    - model_name: Name of the model class
    - table_name: Name of the database table
    - fields: List of dictionaries with field information
    - relationships: List of dictionaries with relationship information
    """
    mapper = sa_inspect(model_class)
    entity_name = model_class.__name__
    
    # Extract field information
    fields = []
    for column in mapper.columns:
        python_type = map_sqlalchemy_to_python_type(column.type)
        default_value = get_default_value(column)
        
        # Handle foreign keys - foreign_keys is a set, not a list
        foreign_key = None
        if column.foreign_keys:
            fk = next(iter(column.foreign_keys), None)
            if fk:
                foreign_key = fk.column.table.name
                
        fields.append({
            'name': column.name,
            'attribute_name': column.key,  # The attribute name in the model
            'type': python_type,
            'nullable': column.nullable,
            'primary_key': column.primary_key,
            'uuid_type': python_type == 'UUID',
            'default': default_value,
            'foreign_key': foreign_key
        })
    
    # Extract relationship information
    relationships = []
    for rel in mapper.relationships:
        target_entity = rel.mapper.class_.__name__
        
        # Handle local_remote_pairs - it's a collection, not necessarily indexable
        foreign_key = None
        if rel.local_remote_pairs:
            try:
                # Get the first pair
                pair = next(iter(rel.local_remote_pairs))
                if pair and len(pair) >= 1:
                    foreign_key = pair[0].name
            except (IndexError, TypeError):
                foreign_key = None
                
        relationships.append({
            'name': rel.key,
            'target_entity': target_entity,
            'target_table': rel.target.name,
            'uselist': rel.uselist,  # True for one-to-many, False for one-to-one
            'direction': 'to_many' if rel.uselist else 'to_one',
            'foreign_key': foreign_key,
        })
    
    # Separate required and optional fields
    required_fields = [f for f in fields if not f['nullable'] and not f['primary_key']]
    optional_fields = [f for f in fields if f['nullable'] or f['primary_key']]
    
    # Generate type annotations for fields
    for field in fields:
        nullable = field['nullable']
        python_type = field['type']
        
        if nullable:
            field['type_annotation'] = f"Optional[{python_type}]"
        else:
            field['type_annotation'] = python_type
        
        # Mark UUID fields
        field['is_uuid'] = python_type == 'UUID'
        
        # Set required flag
        field['required'] = not nullable and not field['primary_key']
    
    # Add more detailed relationship information
    for rel in relationships:
        rel['is_collection'] = rel['uselist']
        if rel['uselist']:
            rel['type'] = f"List[{rel['target_entity']}]"
        else:
            rel['type'] = rel['target_entity']
        
        # Add placeholder description
        rel['description'] = f"Related {rel['target_entity']}{'s' if rel['uselist'] else ''}"
    
    # Generate additional names needed for templating
    entity_name = model_class.__name__
    entity_name_snake = ''.join(['_' + c.lower() if c.isupper() else c for c in entity_name]).lstrip('_')
    entity_name_snake_plural = entity_name_snake + 's'
    entity_name_readable = ' '.join(word.capitalize() for word in entity_name_snake.split('_'))
    
    # Generate API path if not specified
    api_route_prefix = entity_name_snake_plural
    api_tag = entity_name
    
    # Determine files for imports
    entity_file = entity_name_snake
    repository_file = f"{entity_name_snake}_repository"
    manager_file = f"{entity_name_snake}_manager"
    service_file = f"{entity_name_snake}_service"
    schema_file = f"{entity_name_snake}_schema"
    model_file = entity_name_snake
    
    return {
        'model_name': model_class.__name__,
        'entity_name': entity_name,
        'entity_name_snake': entity_name_snake,
        'entity_name_snake_plural': entity_name_snake_plural,
        'entity_name_readable': entity_name_readable,
        'table_name': mapper.local_table.name,
        'fields': fields,
        'required_fields': required_fields,
        'optional_fields': optional_fields,
        'relationships': relationships,
        'api_route_prefix': api_route_prefix,
        'api_tag': api_tag,
        'entity_file': entity_file,
        'repository_file': repository_file,
        'manager_file': manager_file,
        'service_file': service_file,
        'schema_file': schema_file,
        'model_file': model_file,
    }