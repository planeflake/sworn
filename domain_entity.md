# Domain Entity Generator

A tool to automate the creation of domain entities and related components from SQLAlchemy models.

## Overview

This generator would create a complete set of domain components from a single SQLAlchemy model:

- Domain Entity class
- Repository class
- Manager class
- Service class 
- API schemas (Create, Read, Update)
- API routes (CRUD operations)
- Basic tests

## Implementation Scope

The generator would be a **moderate-sized project** (2-3 days of focused work) with these components:

### 1. Model Analysis Tool (~4-6 hours)
- Parse SQLAlchemy model class
- Extract fields, types, relationships
- Identify primary/foreign keys
- Map SQLAlchemy types to domain entity types

### 2. Template System (~4-6 hours)
- Create Jinja2 templates for each component
- Design template inheritance structure
- Support customization points

### 3. Code Generation (~4-6 hours)
- Transform analyzed model into template context
- Generate code for each component
- Handle imports and dependencies
- Apply naming conventions

### 4. Configuration System (~2-3 hours)
- Allow customization of generated output
- Support overriding default behaviors
- Configure naming patterns

### 5. CLI Interface (~2-3 hours)
- Create command-line interface
- Process arguments and options
- Handle errors gracefully

## Project Structure

```
app/
└── tools/
    └── generators/
        ├── __init__.py
        ├── cli.py              # Command-line interface
        ├── model_analyzer.py   # Extracts model information
        ├── code_generator.py   # Handles code generation
        ├── config.py           # Configuration options
        └── templates/          # Jinja2 templates
            ├── entity.py.j2
            ├── repository.py.j2
            ├── manager.py.j2
            ├── service.py.j2
            ├── api_schema.py.j2
            ├── api_routes.py.j2
            └── tests.py.j2
```

## Sample CLI Usage

```bash
# Generate all components for a model
python -m app.tools.generators.cli --model app.db.models.zone.Zone --output-dir generated

# Generate only specific components
python -m app.tools.generators.cli --model app.db.models.zone.Zone --components entity,repository

# Use custom template overrides
python -m app.tools.generators.cli --model app.db.models.zone.Zone --template-dir my_templates
```

## Sample Template for Entity

```jinja
# {{ entity_name }}.py - Generated code

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from app.game_state.entities.base import BaseEntity

@dataclass
class {{ entity_name }}Entity(BaseEntity):
    """
    Represents a {{ entity_name }} in the game (Domain Entity).
    Inherits entity_id and name as fields from BaseEntity.
    """
    # Required fields
    {% for field in required_fields %}
    {{ field.name }}: {{ field.type }}
    {% endfor %}
    
    # Optional fields with defaults
    {% for field in optional_fields %}
    {{ field.name }}: {{ field.type }} = {{ field.default }}
    {% endfor %}
    
    # Relationship fields
    {% for rel in relationships %}
    {{ rel.name }}: {{ rel.type }} = field(default_factory=list)
    {% endfor %}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert {{ entity_name }}Entity to a dictionary with safe serialization."""
        data = {
            "id": str(self.entity_id),
            "name": self.name,
            {% for field in all_fields %}
            "{{ field.name }}": {% if field.uuid_type %}str(self.{{ field.name }}) if self.{{ field.name }} else None{% else %}self.{{ field.name }}{% endif %},
            {% endfor %}
            {% for rel in relationships %}
            # Skip {{ rel.name }} as it's only used internally, not for API serialization
            {% endfor %}
        }
        return data
```

## Sample Template for Repository

```jinja
# {{ entity_name|lower }}_repository.py - Generated code

from app.game_state.repositories.base_repository import BaseRepository
from app.game_state.entities.{{ entity_name|lower }} import {{ entity_name }}Entity
from app.db.models.{{ model_path }} import {{ model_name }}
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from sqlalchemy.future import select
import logging

class {{ entity_name }}Repository(BaseRepository[{{ entity_name }}Entity, {{ model_name }}, UUID]):
    """
    Repository for {{ entity_name }} entities.
    """
    def __init__(self, db):
        """Initialize with database session."""
        super().__init__(db=db, model_cls={{ model_name }}, entity_cls={{ entity_name }}Entity)
        logging.debug(f"{{ entity_name }}Repository initialized")
        
    {% for relationship in relationships %}
    async def find_by_{{ relationship.foreign_key|snake_case }}(self, {{ relationship.foreign_key|snake_case }}: UUID) -> List[{{ entity_name }}Entity]:
        """Find all {{ entity_name|lower }}s by their {{ relationship.foreign_key|snake_case }}."""
        stmt = select(self.model_cls).where(self.model_cls.{{ relationship.foreign_key|snake_case }} == {{ relationship.foreign_key|snake_case }})
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        return [await self._convert_to_entity(db_obj) for db_obj in db_objs]
    {% endfor %}
    
    # Add custom repository methods here
```

## Challenges and Considerations

1. **Field Mapping Complexity**: Handling all SQLAlchemy field types and their domain equivalents
2. **Relationships**: Correctly generating code for many-to-one, one-to-many, many-to-many
3. **Imports**: Managing import statements across generated files
4. **Customization**: Balancing configurability vs. complexity
5. **Integration**: Ensuring generated code follows project conventions

## Quick Prototype Approach

For a minimal viable prototype:

1. Create a simple script that just generates entity and repository classes
2. Use string templates rather than Jinja2 for the first version
3. Hard-code the conventions for your project
4. Manually modify the output as needed

This would take ~4-8 hours and give you a sense of whether the full generator is worth building.

## Benefits

- **Consistency**: Ensures all domain components follow the same patterns
- **Productivity**: Eliminates repetitive boilerplate coding
- **Accuracy**: Reduces the risk of typos or manual errors
- **Maintainability**: Makes it easier to change patterns across all entities

## Return on Investment

For an RPG game with many entity types:
- Initial investment: 2-3 days
- Payoff point: After generating 5-10 complete entity sets
- Long-term benefit: Days or weeks of development time saved