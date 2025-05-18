"""
Configuration Module for Domain Entity Generator

Provides configuration options and default settings for the generator.
"""

from typing import Dict, Any, List, Optional, Set, Union
from dataclasses import dataclass, field
import os
from pathlib import Path

@dataclass
class GeneratorConfig:
    """Configuration for domain entity generator."""
    
    # Model information
    model_class_name: str
    model_module: Optional[str] = None
    
    # Output locations
    output_dir: str = os.path.join(os.getcwd(), "app/game_state")
    template_dir: Optional[str] = None  # Default uses built-in templates
    
    # Component generation flags
    generate_entity: bool = True
    generate_repository: bool = True
    generate_manager: bool = True
    generate_service: bool = True
    generate_api_schema: bool = True
    generate_api_routes: bool = True
    
    # Naming conventions
    entity_suffix: str = "Entity"
    repository_suffix: str = "Repository"
    manager_suffix: str = "Manager"
    service_suffix: str = "Service"
    
    # Import paths - adjust these to match your project structure
    entity_import_path: str = "app.game_state.entities"
    repository_import_path: str = "app.game_state.repositories"
    manager_import_path: str = "app.game_state.managers"
    service_import_path: str = "app.game_state.services"
    api_schema_import_path: str = "app.api.schemas"
    api_routes_import_path: str = "app.api.routes"
    
    # Type overrides - specify custom type mappings
    type_overrides: Dict[str, str] = field(default_factory=dict)
    
    # Relationship handling
    include_relationships: bool = True
    lazy_load_relationships: bool = True
    
    # File options
    create_test_files: bool = False
    force_overwrite: bool = False
    
    # API options
    api_route_prefix: Optional[str] = None
    api_tag: Optional[str] = None
    
    def __post_init__(self):
        """Validate the configuration after initialization."""
        # Ensure output_dir is an absolute path
        if not os.path.isabs(self.output_dir):
            self.output_dir = os.path.abspath(self.output_dir)
            
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    def is_component_enabled(self, component_name: str) -> bool:
        """Check if a specific component is enabled."""
        component_map = {
            "entity": self.generate_entity,
            "repository": self.generate_repository,
            "manager": self.generate_manager,
            "service": self.generate_service,
            "api_schema": self.generate_api_schema,
            "api_routes": self.generate_api_routes
        }
        return component_map.get(component_name.lower(), False)
    
    def get_output_path(self, component_name: str, model_name: str) -> str:
        """Get the output path for a specific component."""
        component_dir = {
            "entity": "entities",
            "repository": "repositories",
            "manager": "managers",
            "service": "services",
            "api_schema": "schemas",
            "api_routes": "routes",
        }.get(component_name.lower(), "")
        
        return f"{self.output_dir}/{component_dir}/{model_name.lower()}.py"

# There is no default configuration as model_class_name is required