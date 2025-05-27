# Migrating Entities from Dataclasses to Pydantic

This document outlines the process for converting our domain entities from Python dataclasses to Pydantic models.

## Why Migrate to Pydantic?

1. **Better Validation**: Pydantic offers more robust data validation than dataclasses
2. **Schema Generation**: Automatic JSON schema generation for API documentation
3. **Serialization**: Built-in methods for JSON serialization/deserialization
4. **Consistency**: Aligns with our API schema design (already using Pydantic)
5. **Type Coercion**: Automatic type conversion for compatible types

## Migration Strategy

We're using a gradual migration approach:

1. Create new Pydantic versions of each entity with `_pydantic.py` suffix
2. Keep the original dataclass implementations for backward compatibility
3. Use the `pydantic_bridge.py` module to handle conversions when needed
4. Update managers and services to work with both versions during transition
5. Eventually replace all dataclass usage with Pydantic models

## Conversion Steps for Each Entity

When converting a dataclass entity to Pydantic:

1. Create a new file named `[entity_name]_pydantic.py`
2. Import from `pydantic` instead of `dataclasses`
3. Use `BaseModel` and `Field` instead of `dataclass` and `field`
4. Change class naming: `EntityNamePydantic` instead of `EntityName`
5. Add the `Config` class with appropriate settings
6. Replace data validation logic with Pydantic validators
7. Update the `to_dict()` method as needed
8. Add the new entity to the `pydantic_bridge.py` mappings

## Conversion Example

```python
# Original dataclass
@dataclass
class ThemeEntity(BaseEntity):
    description: Optional[str] = None
    genre: Optional[str] = None
    style: Optional[str] = None
    
    name: str = "Default Theme"

# Pydantic version
class ThemeEntityPydantic(BaseEntityPydantic):
    description: Optional[str] = None
    genre: Optional[str] = None
    style: Optional[str] = None
    
    name: str = "Default Theme"
    
    class Config:
        from_attributes = True
        
        # Schema examples for documentation
        json_schema_extra = {
            "example": {
                "name": "Fantasy Theme",
                "description": "A high fantasy medieval setting",
                "genre": "Fantasy",
                "style": "Medieval"
            }
        }
```

## Using Validation Features

Pydantic offers powerful validation capabilities:

```python
from pydantic import BaseModel, Field, field_validator

class BuildingBlueprintPydantic(BaseEntityPydantic):
    theme_id: UUID
    metadata_: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('metadata_')
    @classmethod
    def validate_metadata(cls, v):
        """Ensure metadata has required structure."""
        if v is None:
            v = {}
        if 'attributes' not in v:
            v['attributes'] = []
        return v
```

## Testing Your Converted Entities

When you convert an entity, make sure to:

1. Test instantiation with various inputs
2. Test validation works as expected
3. Test serialization via `model.model_dump()` or `model.dict()`
4. Test the `to_dict()` method if customized
5. Verify compatibility with existing code via the bridge module

## Next Steps

1. Continue converting all entities to Pydantic models
2. Update service and manager layers to use the new models
3. Update repository layer to handle Pydantic models
4. Update any tests to work with the new model formats
5. Eventually phase out the dataclass versions

## Questions or Issues?

Contact the development team with any questions about the migration process.