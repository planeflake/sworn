# Domain Entity Generator

A tool for automatically generating domain entity components from SQLAlchemy models.

## Overview

This generator creates the following components based on SQLAlchemy models:

- Domain Entities
- Repositories
- Managers
- Services
- API Schemas
- API Routes

## Usage

You can use the generator as a CLI tool:

```bash
# Generate all components for the World model
python -m app.tools.generators World

# Generate only entity and repository for the Settlement model
python -m app.tools.generators Settlement --no-manager --no-service --no-api-schema --no-api-routes

# Specify model module path for a model in a different package
python -m app.tools.generators Character --model-module app.db.models.character

# Force overwrite existing files
python -m app.tools.generators Resource --force

# Change output directory
python -m app.tools.generators Building --output-dir ./custom_output
```

## Configuration

Command-line options:

- `model_class`: SQLAlchemy model class name to generate from (required)
- `--model-module`: Python module path to the model class
- `--output-dir`, `-o`: Output directory for generated files
- `--no-entity`: Skip domain entity generation
- `--no-repository`: Skip repository generation
- `--no-manager`: Skip manager generation
- `--no-service`: Skip service generation
- `--no-api-schema`: Skip API schema generation
- `--no-api-routes`: Skip API routes generation
- `--force`: Overwrite existing files
- `--api-prefix`: API route prefix (default: pluralized snake_case of entity name)
- `--api-tag`: API tag for documentation (default: entity name)
- `--tests`: Generate test files
- `--verbose`, `-v`: Verbose output

## Template Customization

The generator uses Jinja2 templates located in the `templates` directory. You can customize these templates to match your project's coding style and patterns.

## Example

For a model named `World`, the generator will create:

- `app/game_state/entities/world_entity.py`
- `app/game_state/repositories/world_repository.py`
- `app/game_state/managers/world_manager.py`
- `app/game_state/services/world_service.py`
- `app/api/schemas/world_schema.py`
- `app/api/routes/world_routes.py`

## Benefits

- Ensures consistent implementation of domain architecture patterns
- Reduces boilerplate code
- Maintains consistent naming conventions
- Accelerates development of new domain components
- Ensures relationships are properly handled