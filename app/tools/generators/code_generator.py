"""
Code Generator Module

Generates domain entity code from SQLAlchemy model analysis.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Set up Jinja2 environment
def create_jinja_env(template_dir: Optional[str] = None) -> Environment:
    """Create and configure Jinja2 environment."""
    if template_dir is None:
        # Use default templates directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(current_dir, 'templates')
    
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    
    # Add custom filters
    env.filters['snake_case'] = lambda s: s.replace('-', '_').replace(' ', '_').lower()
    env.filters['camel_case'] = lambda s: ''.join(word.capitalize() for word in s.split('_'))
    
    return env

def determine_imports(model_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Determine necessary imports for the generated entity."""
    imports = {
        'standard': ['from dataclasses import dataclass, field'],
        'typing': ['from typing import Optional, List, Dict, Any'],
        'project': ['from app.game_state.entities.base import BaseEntity'],
    }
    
    # Add UUID import if needed
    if any(f['uuid_type'] for f in model_data['fields']):
        imports['standard'].append('from uuid import UUID')
    
    # Add datetime import if needed
    if any(f['type'] == 'datetime' for f in model_data['fields']):
        imports['standard'].append('from datetime import datetime')
    
    return imports

def generate_entity(model_data: Dict[str, Any], config: Any) -> str:
    """Generate a domain entity class from model data."""
    env = create_jinja_env()
    template = env.get_template('entity.py.j2')
    
    # Prepare template context
    context = {
        'entity_name': model_data['entity_name'],
        'entity_name_readable': model_data['entity_name_readable'],
        'fields': model_data['fields'],
        'required_fields': model_data['required_fields'],
        'optional_fields': model_data['optional_fields'],
        'relationships': model_data['relationships'],
        'imports': determine_imports(model_data),
    }
    
    # Render the template
    output = template.render(**context)
    
    # Create output directory if it doesn't exist
    entity_dir = os.path.join(config.output_dir, 'entities')
    os.makedirs(entity_dir, exist_ok=True)
    
    # Write output to file
    entity_file_name = f"{model_data['entity_name_snake']}_entity.py"
    output_path = os.path.join(entity_dir, entity_file_name)
    
    with open(output_path, 'w') as f:
        f.write(output)
    
    return output_path

def generate_repository(model_data: Dict[str, Any], config: Any) -> str:
    """Generate a repository class from model data."""
    env = create_jinja_env()
    template = env.get_template('repository.py.j2')
    
    # Use the model_file from the model_data
    
    # Prepare template context
    context = {
        'entity_name': model_data['entity_name'],
        'model_name': model_data['model_name'],
        'model_file': model_data['model_file'],
        'entity_file': model_data['entity_file'],
        'entity_name_readable': model_data['entity_name_readable'],
        'fields': model_data['fields'],
        'relationships': model_data['relationships'],
    }
    
    # Render the template
    output = template.render(**context)
    
    # Create output directory if it doesn't exist
    repo_dir = os.path.join(config.output_dir, 'repositories')
    os.makedirs(repo_dir, exist_ok=True)
    
    # Write output to file
    repo_file_name = f"{model_data['entity_name_snake']}_repository.py"
    output_path = os.path.join(repo_dir, repo_file_name)
    
    with open(output_path, 'w') as f:
        f.write(output)
    
    return output_path

def generate_manager(model_data: Dict[str, Any], config: Any) -> str:
    """Generate a manager class from model data."""
    env = create_jinja_env()
    template = env.get_template('manager.py.j2')
    
    # Prepare template context
    context = {
        'entity_name': model_data['entity_name'],
        'entity_name_snake': model_data['entity_name_snake'],
        'entity_name_snake_plural': model_data['entity_name_snake_plural'],
        'entity_name_readable': model_data['entity_name_readable'],
        'entity_file': model_data['entity_file'],
        'repository_file': model_data['repository_file'],
        'fields': model_data['fields'],
        'required_fields': model_data['required_fields'],
    }
    
    # Render the template
    output = template.render(**context)
    
    # Create output directory if it doesn't exist
    manager_dir = os.path.join(config.output_dir, 'managers')
    os.makedirs(manager_dir, exist_ok=True)
    
    # Write output to file
    manager_file_name = f"{model_data['entity_name_snake']}_manager.py"
    output_path = os.path.join(manager_dir, manager_file_name)
    
    with open(output_path, 'w') as f:
        f.write(output)
    
    return output_path

def generate_service(model_data: Dict[str, Any], config: Any) -> str:
    """Generate a service class from model data."""
    env = create_jinja_env()
    template = env.get_template('service.py.j2')
    
    # Prepare template context
    context = {
        'entity_name': model_data['entity_name'],
        'entity_name_snake': model_data['entity_name_snake'],
        'entity_name_snake_plural': model_data['entity_name_snake_plural'],
        'entity_name_readable': model_data['entity_name_readable'],
        'entity_file': model_data['entity_file'],
        'manager_file': model_data['manager_file'],
        'fields': model_data['fields'],
    }
    
    # Render the template
    output = template.render(**context)
    
    # Create output directory if it doesn't exist
    service_dir = os.path.join(config.output_dir, 'services')
    os.makedirs(service_dir, exist_ok=True)
    
    # Write output to file
    service_file_name = f"{model_data['entity_name_snake']}_service.py"
    output_path = os.path.join(service_dir, service_file_name)
    
    with open(output_path, 'w') as f:
        f.write(output)
    
    return output_path

def generate_api_schema(model_data: Dict[str, Any], config: Any) -> str:
    """Generate API schema classes from model data."""
    env = create_jinja_env()
    template = env.get_template('api_schema.py.j2')
    
    # Prepare template context
    context = {
        'entity_name': model_data['entity_name'],
        'entity_name_readable': model_data['entity_name_readable'],
        'fields': model_data['fields'],
        'required_fields': model_data['required_fields'],
        'optional_fields': model_data['optional_fields'],
        'relationships': model_data['relationships'],
    }
    
    # Render the template
    output = template.render(**context)
    
    # Create output directory if it doesn't exist
    schema_dir = os.path.join(config.output_dir, 'schemas')
    os.makedirs(schema_dir, exist_ok=True)
    
    # Write output to file
    schema_file_name = f"{model_data['entity_name_snake']}_schema.py"
    output_path = os.path.join(schema_dir, schema_file_name)
    
    with open(output_path, 'w') as f:
        f.write(output)
    
    return output_path

def generate_api_routes(model_data: Dict[str, Any], config: Any) -> str:
    """Generate API routes from model data."""
    env = create_jinja_env()
    template = env.get_template('api_routes.py.j2')
    
    # Prepare template context
    context = {
        'entity_name': model_data['entity_name'],
        'entity_name_snake': model_data['entity_name_snake'],
        'entity_name_snake_plural': model_data['entity_name_snake_plural'],
        'entity_name_readable': model_data['entity_name_readable'],
        'table_name': model_data['table_name'],
        'schema_file': model_data['schema_file'],
        'service_file': model_data['service_file'],
        'repository_file': model_data['repository_file'],
        'manager_file': model_data['manager_file'],
        'api_route_prefix': model_data.get('api_route_prefix', model_data['entity_name_snake_plural']),
        'api_tag': model_data.get('api_tag', model_data['entity_name']),
        'fields': model_data['fields'],
        'search_fields': [f for f in model_data['fields'] if not f['primary_key']],
    }
    
    # Render the template
    output = template.render(**context)
    
    # Create output directory if it doesn't exist
    routes_dir = os.path.join(config.output_dir, 'routes')
    os.makedirs(routes_dir, exist_ok=True)
    
    # Write output to file
    routes_file_name = f"{model_data['entity_name_snake']}_routes.py"
    output_path = os.path.join(routes_dir, routes_file_name)
    
    with open(output_path, 'w') as f:
        f.write(output)
    
    return output_path

def generate_code(model_data: Dict[str, Any], config: Any) -> List[str]:
    """Generate all domain components for a model."""
    generated_files = []
    
    try:
        # Create main output directory
        os.makedirs(config.output_dir, exist_ok=True)
        
        # Generate components based on configuration
        if config.is_component_enabled('entity'):
            generated_files.append(generate_entity(model_data, config))
            
        if config.is_component_enabled('repository'):
            generated_files.append(generate_repository(model_data, config))
            
        if config.is_component_enabled('manager'):
            generated_files.append(generate_manager(model_data, config))
            
        if config.is_component_enabled('service'):
            generated_files.append(generate_service(model_data, config))
            
        if config.is_component_enabled('api_schema'):
            generated_files.append(generate_api_schema(model_data, config))
            
        if config.is_component_enabled('api_routes'):
            generated_files.append(generate_api_routes(model_data, config))
            
        # Generate tests if enabled
        if config.create_test_files:
            # TODO: Implement test file generation
            pass
        
        return generated_files
    except Exception as e:
        logging.error(f"Error generating files: {e}")
        raise