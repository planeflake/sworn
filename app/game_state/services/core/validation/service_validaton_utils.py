# app/game_state/services/validation/service_validation_utils.py
"""
Simple validation utilities for service layer.
Handles foreign key validation and business rule validation with automatic detection.
"""

from typing import Dict, List, Optional, Tuple, Any, Union, get_type_hints, get_origin, get_args
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class ValidationError(ValueError):
    """Custom exception for validation errors with multiple error support"""

    def __init__(self, errors: Union[str, List[str]]):
        if isinstance(errors, str):
            errors = [errors]
        self.errors = errors
        super().__init__("; ".join(errors))


class ServiceValidationUtils:
    """
    Simple validation utilities for service layer.

    Features:
    - Foreign key validation with concurrent checking
    - Automatic FK detection from Pydantic schemas (no manual mapping needed!)
    - Standard validation patterns for common entities
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._services = {}  # Lazy-loaded service cache

    def _get_service(self, service_name: str):
        """
        Fully automatic service loading using pure convention.
        Supports both directory structures:
        1. app.game_state.services.{service_name}.{service_name}_service.{ServiceName}Service
        2. app.game_state.services.{service_name}_service.{ServiceName}Service

        Examples:
        - "theme" -> theme_service.ThemeService
        - "location_type" -> location_type_service.LocationTypeService
        - "character" -> character_service.CharacterService

        Adding new services requires ZERO configuration changes!
        """
        if service_name not in self._services:
            try:
                # Convert service_name to module and class names using convention
                module_name = f"{service_name}_service"

                # Convert snake_case to PascalCase for class name
                # "location_type" -> "LocationTypeService"
                class_name = ''.join(word.title() for word in service_name.split('_')) + 'Service'

                # Use importlib for more reliable importing
                import importlib

                service_class = None

                # Strategy 1: Try directory structure - services/{service_name}/{service_name}_service.py
                try:
                    full_module_path = f"app.game_state.services.{service_name}.{module_name}"
                    module = importlib.import_module(full_module_path)
                    service_class = getattr(module, class_name)
                    logger.debug(
                        f"Auto-loaded service (dir structure): {service_name} -> {full_module_path}.{class_name}")

                except (ImportError, AttributeError, ModuleNotFoundError):
                    # Strategy 2: Try flat structure - services/{service_name}_service.py
                    try:
                        full_module_path = f"app.game_state.services.{module_name}"
                        module = importlib.import_module(full_module_path)
                        service_class = getattr(module, class_name)
                        logger.debug(
                            f"Auto-loaded service (flat structure): {service_name} -> {full_module_path}.{class_name}")

                    except (ImportError, AttributeError, ModuleNotFoundError) as e:
                        logger.warning(f"Could not auto-load service '{service_name}': {e}")
                        logger.debug(f"Tried both: services.{service_name}.{module_name} and services.{module_name}")
                        return None

                if service_class:
                    # Instantiate and cache the service
                    self._services[service_name] = service_class(self.db)
                else:
                    return None

            except Exception as e:
                logger.warning(f"Unexpected error loading service '{service_name}': {e}")
                return None

        return self._services.get(service_name)

    # ==============================================================================
    # CORE VALIDATION METHODS
    # ==============================================================================

    async def validate_foreign_keys(
            self,
            data: Dict[str, Any],
            validations: Dict[str, Tuple[str, str]]
    ) -> None:
        """
        Validate multiple foreign key references concurrently.

        Args:
            data: Dictionary containing the data to validate
            validations: Dict mapping field_name -> (service_name, entity_display_name)
                        e.g., {"theme_id": ("theme", "Theme")}

        Raises:
            ValidationError: If any foreign keys are invalid

        Example:
            await validator.validate_foreign_keys(location_dict, {
                "theme_id": ("theme", "Theme"),
                "world_id": ("world", "World")
            })
        """

        async def validate_single_fk(field_name: str, service_name: str, entity_name: str) -> Optional[str]:
            """Validate a single foreign key reference using direct database queries"""
            if entity_id := data.get(field_name):
                try:
                    # Use direct database validation instead of services to avoid session conflicts
                    exists = await self._check_entity_exists_direct(entity_id, service_name)
                    if not exists:
                        return f"{entity_name} not found: {entity_id}"
                except Exception as e:
                    logger.error(f"Error validating {entity_name} {entity_id}: {e}")
                    return f"Error validating {entity_name}: {entity_id}"
            return None

        if not validations:
            return

        # Run validations sequentially to avoid session conflicts
        errors = []
        
        for field_name, (service_name, entity_name) in validations.items():
            try:
                result = await validate_single_fk(field_name, service_name, entity_name)
                if result:  # String error message
                    errors.append(result)
            except Exception as e:
                errors.append(f"Validation error: {str(e)}")

        if errors:
            raise ValidationError(errors)

    async def validate_entity_exists(
            self,
            entity_id: UUID,
            service_name: str,
            entity_name: str
    ) -> None:
        """
        Validate a single entity exists using direct database queries.

        Args:
            entity_id: The UUID to validate
            service_name: Name of the service to use for validation
            entity_name: Display name for error messages
        """
        # Use direct database queries instead of services to avoid session conflicts
        exists = await self._check_entity_exists_direct(entity_id, service_name)
        if not exists:
            raise ValidationError([f"{entity_name} not found: {entity_id}"])

    async def _check_entity_exists_direct(self, entity_id: UUID, service_name: str) -> bool:
        """
        Check if entity exists using direct database query to avoid session conflicts.
        """
        from sqlalchemy import select, func
        
        # Map service names to model classes for more reliable queries
        model_mapping = {
            'theme': 'app.db.models.theme.ThemeDB',
            'world': 'app.db.models.world.World', 
            'location_type': 'app.db.models.location_type.LocationType',
            'location_sub_type': 'app.db.models.location_sub_type.LocationSubType',
            'character': 'app.db.models.character.Character',
            'biome': 'app.db.models.biome.Biome',
            'settlement': 'app.db.models.settlement.Settlement',
            'building_blueprint': 'app.db.models.building_blueprint.BuildingBlueprint',
            'building_instance': 'app.db.models.building_instance.BuildingInstance',
            'skill_definition': 'app.db.models.skill_definition.SkillDefinition',
            'tool_tier': 'app.db.models.tool_tier.ToolTier',
            'action_category': 'app.db.models.action_category.ActionCategory',
            'action_template': 'app.db.models.action_template.ActionTemplate',
            'blueprint': 'app.db.models.resources.resource_node_blueprint.ResourceNodeBlueprint',
            'resource_blueprint': 'app.db.models.resources.resource_blueprint.ResourceBlueprint',
            'resource_instance': 'app.db.models.resources.resource_instance.ResourceInstance',
            'resource_node_blueprint': 'app.db.models.resources.resource_node_blueprint.ResourceNodeBlueprint',
            'location': 'app.db.models.location_instance.LocationInstance'
        }
        
        model_path = model_mapping.get(service_name)
        if not model_path:
            logger.warning(f"No model mapping found for service: {service_name}")
            return False
        
        try:
            # Dynamically import the model class
            module_path, class_name = model_path.rsplit('.', 1)
            import importlib
            module = importlib.import_module(module_path)
            model_class = getattr(module, class_name)
            
            # Use SQLAlchemy select with the actual model
            query = select(func.count()).select_from(model_class).where(model_class.id == entity_id)
            result = await self.db.execute(query)
            count = result.scalar()
            exists = count > 0
            logger.debug(f"Direct validation for {service_name} {entity_id} using {model_path}: {exists}")
            return exists
            
        except Exception as e:
            logger.warning(f"Direct validation failed for {service_name} {entity_id}: {e}")
            return False

    # ==============================================================================
    # AUTO-DETECTION METHODS (FULLY AUTOMATIC - NO MAPPINGS NEEDED!)
    # ==============================================================================

    async def validate_schema_foreign_keys(
            self,
            data: Dict[str, Any],
            schema_class: type[BaseModel]
    ) -> None:
        """
        Automatically detect and validate foreign keys from Pydantic model.

        NEW APPROACH:
        - For simple FKs (theme_id, world_id): Auto-derive service name and entity name
        - For polymorphic FKs (parent_id): Use companion type field (parent_type)
        - Zero manual configuration required!

        Args:
            data: Data dictionary to validate
            schema_class: Pydantic model class to extract FK info from
        """
        fk_mappings = self._extract_foreign_keys_from_schema(schema_class, data)

        if fk_mappings:
            await self.validate_foreign_keys(data, fk_mappings)

    def _extract_foreign_keys_from_schema(
            self,
            schema_class: type[BaseModel],
            data: Dict[str, Any]
    ) -> Dict[str, Tuple[str, str]]:
        """
        Extract foreign key fields from Pydantic model annotations.
        Now fully automatic with polymorphic FK support!

        Args:
            schema_class: Pydantic model class
            data: Actual data being validated (needed for polymorphic FKs)

        Returns:
            Dict mapping field_name -> (service_name, entity_display_name)
        """
        fk_mappings = {}

        try:
            # Get field annotations
            type_hints = get_type_hints(schema_class)

            for field_name, field_type in type_hints.items():
                # Check if it's a UUID field ending in '_id'
                if field_name.endswith('_id') and self._is_uuid_type(field_type):

                    # Try to resolve the FK automatically
                    service_name, entity_name = self._resolve_foreign_key(field_name, data)

                    if service_name:  # Only add if we can resolve it
                        fk_mappings[field_name] = (service_name, entity_name)
                        logger.debug(f"Auto-detected FK: {field_name} -> {service_name}.{entity_name}")

        except Exception as e:
            logger.warning(f"Error extracting foreign keys from {schema_class.__name__}: {e}")

        return fk_mappings

    def _resolve_foreign_key(self, field_name: str, data: Dict[str, Any]) -> Tuple[Optional[str], str]:
        """
        Resolve foreign key field to service name and entity name.

        RESOLUTION STRATEGY:
        1. For polymorphic FKs (parent_id): Look for companion type field (parent_type)
        2. For standard FKs (theme_id, world_id): Auto-derive from field name
        3. For compound FKs (location_sub_type_id): Use simplified name (location_subtype)

        Args:
            field_name: FK field name (ending in '_id')
            data: Data dict (for checking type fields)

        Returns:
            Tuple of (service_name, entity_display_name)
        """
        base_name = field_name[:-3]  # Remove '_id'

        # Strategy 1: Check for polymorphic FK with companion type field
        type_field = f"{base_name}_type"
        if type_field in data and data[type_field]:
            # Use the type field value as the service name
            service_name = data[type_field].lower()
            entity_name = data[type_field].title()
            return service_name, entity_name

        # Strategy 2: Auto-derive from field name
        service_name = self._field_to_service_name(base_name)
        entity_name = self._field_to_entity_name(base_name)

        return service_name, entity_name

    @staticmethod
    def _is_uuid_type(field_type) -> bool:
        """Check if field type is UUID or Optional[UUID]"""
        # Handle Optional[UUID] -> Union[UUID, None]
        if get_origin(field_type) is Union:
            args = get_args(field_type)
            return UUID in args

        return field_type is UUID

    @staticmethod
    def _field_to_service_name(base_name: str) -> Optional[str]:
        """
        Convert field base name to service name using conventions.

        SIMPLE CONVENTION RULES:
        1. Direct mapping: theme -> theme, world -> world, location_sub_type -> location_sub_type
        2. Location aliases: current_location/home_location -> location
        3. Default: try the base name as-is (works for all standard naming!)

        Args:
            base_name: Field name without '_id' suffix

        Returns:
            Service name (almost always just the base_name itself!)
        """
        # Handle location aliases
        if base_name in ['current_location', 'home_location']:
            return 'location'

        # Default: Direct mapping works for 99% of cases!
        # theme -> theme, world -> world, location_sub_type -> location_sub_type
        return base_name

    @staticmethod
    def _field_to_entity_name(base_name: str) -> str:
        """Convert field base name to human-readable display name"""
        return base_name.replace('_', ' ').title()

    # ==============================================================================
    # BUSINESS RULE VALIDATION
    # ==============================================================================

    async def validate_parent_child_compatibility(
            self,
            data: Dict[str, Any],
            parent_field: str,
            child_field: str,
            parent_service: str,
            child_service: str,
            parent_display: str,
            child_display: str,
            parent_key_on_child: str = None
    ) -> None:
        """
        Generic validation for parent-child entity compatibility.

        Args:
            data: Data dictionary containing the IDs
            parent_field: Field name for parent ID (e.g., "location_type_id")
            child_field: Field name for child ID (e.g., "location_sub_type_id")
            parent_service: Service name for parent entity
            child_service: Service name for child entity
            parent_display: Display name for parent (error messages)
            child_display: Display name for child (error messages)
            parent_key_on_child: Field name on child entity that references parent
                                (defaults to parent_field if not provided)
        """
        parent_id = data.get(parent_field)
        child_id = data.get(child_field)

        if not parent_id or not child_id:
            return  # Skip if either ID is missing

        if parent_key_on_child is None:
            parent_key_on_child = parent_field

        # Get services
        parent_svc = self._get_service(parent_service)
        child_svc = self._get_service(child_service)

        if not parent_svc or not child_svc:
            logger.warning(f"Services not available for parent-child validation: {parent_service}, {child_service}")
            return

        try:
            # Get both entities - use generic get methods
            parent_entity = await self._get_entity_generic(parent_svc, parent_id)
            child_entity = await self._get_entity_generic(child_svc, child_id)

            if not parent_entity or not child_entity:
                return  # Let FK validation handle missing entities

            # Check compatibility
            child_parent_id = getattr(child_entity, parent_key_on_child, None)
            if child_parent_id != parent_id:
                parent_name = getattr(parent_entity, 'name', str(parent_id))
                child_name = getattr(child_entity, 'name', str(child_id))

                raise ValidationError([
                    f"{child_display} '{child_name}' is not compatible with {parent_display} '{parent_name}'"
                ])

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            logger.error(f"Error validating parent-child compatibility: {e}")
            raise ValidationError([f"Error validating {parent_display}-{child_display} compatibility"])

    async def _get_entity_generic(self, service, entity_id: UUID):
        """
        Try common method names to get an entity from a service.
        Services should standardize on one of these method names.
        """
        # Try common getter method names
        method_names = [
            'get_by_id',  # Most common
            'get',  # Simple
            'get_type',  # LocationTypeService
            'get_subtype_by_id',  # LocationSubTypeService
            'get_character',  # CharacterService
            'get_location',  # LocationService
        ]

        for method_name in method_names:
            if hasattr(service, method_name):
                try:
                    return await getattr(service, method_name)(entity_id)
                except Exception:
                    continue

        # Fallback: try 'exists' if available (less ideal but better than nothing)
        if hasattr(service, 'exists'):
            exists = await service.exists(entity_id)
            return {'id': entity_id} if exists else None

        logger.warning(f"No suitable getter method found on service {type(service).__name__}")
        return None

    async def validate_schema_compatibility_rules(
            self,
            data: Dict[str, Any],
            schema_class: type[BaseModel]
    ) -> None:
        """
        Auto-detect and validate compatibility rules from schema annotations.

        Uses field metadata to define compatibility rules:

        class LocationCreate(BaseModel):
            location_type_id: UUID
            location_sub_type_id: Annotated[UUID, CompatibilityRule(
                parent_field="location_type_id",
                parent_service="location_type",
                child_service="location_sub_type"
            )]
        """
        try:
            type_hints = get_type_hints(schema_class, include_extras=True)

            for field_name, field_type in type_hints.items():
                # Check for compatibility rule annotations
                if hasattr(field_type, '__metadata__'):
                    for annotation in field_type.__metadata__:
                        if hasattr(annotation, 'parent_field'):  # Duck typing for CompatibilityRule
                            await self._apply_compatibility_rule(data, field_name, annotation)

        except Exception as e:
            logger.warning(f"Error checking compatibility rules for {schema_class.__name__}: {e}")

    async def _apply_compatibility_rule(self, data: Dict[str, Any], child_field: str, rule):
        """Apply a single compatibility rule"""
        await self.validate_parent_child_compatibility(
            data=data,
            parent_field=rule.parent_field,
            child_field=child_field,
            parent_service=getattr(rule, 'parent_service', rule.parent_field.replace('_id', '')),
            child_service=getattr(rule, 'child_service', child_field.replace('_id', '')),
            parent_display=getattr(rule, 'parent_display',
                                   rule.parent_field.replace('_id', '').replace('_', ' ').title()),
            child_display=getattr(rule, 'child_display', child_field.replace('_id', '').replace('_', ' ').title()),
            parent_key_on_child=getattr(rule, 'parent_key_on_child', rule.parent_field)
        )


# ==============================================================================
# COMPATIBILITY RULE ANNOTATION
# ==============================================================================

class CompatibilityRule:
    """
    Annotation for defining parent-child compatibility rules on Pydantic fields.

    Example:
        class LocationCreate(BaseModel):
            location_type_id: UUID
            location_sub_type_id: Annotated[UUID, CompatibilityRule(
                parent_field="location_type_id"
            )]
    """

    def __init__(
            self,
            parent_field: str,
            parent_service: str = None,
            child_service: str = None,
            parent_display: str = None,
            child_display: str = None,
            parent_key_on_child: str = None
    ):
        self.parent_field = parent_field
        self.parent_service = parent_service or parent_field.replace('_id', '')
        self.child_service = child_service  # Will be auto-derived if None
        self.parent_display = parent_display or parent_field.replace('_id', '').replace('_', ' ').title()
        self.child_display = child_display  # Will be auto-derived if None
        self.parent_key_on_child = parent_key_on_child or parent_field


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

async def get_validation_utils(db: AsyncSession) -> ServiceValidationUtils:
    """Convenience function to create validation utils instance"""
    return ServiceValidationUtils(db)


# ==============================================================================
# USAGE EXAMPLES
# ==============================================================================

"""
# Example usage in services:

from typing import Annotated

class LocationService(BaseService[...]):
    def __init__(self, db: AsyncSession):
        super().__init__(...)
        self.validator = ServiceValidationUtils(db)

    async def _validate_creation(self, entity_dict, validation_schema=None):
        # PREFERRED: Use auto-detection for FKs
        await self.validator.validate_schema_foreign_keys(entity_dict, LocationCreate)

        # PREFERRED: Use auto-detection for compatibility rules  
        await self.validator.validate_schema_compatibility_rules(entity_dict, LocationCreate)

# Example schema with compatibility rules:

class LocationCreate(BaseModel):
    name: str
    theme_id: UUID                    # Auto-detected FK validation
    world_id: UUID                    # Auto-detected FK validation
    location_type_id: UUID            # Auto-detected FK validation

    # Compatibility rule: location_sub_type must belong to the location_type
    location_sub_type_id: Annotated[UUID, CompatibilityRule(
        parent_field="location_type_id"
    )] = None

    # Polymorphic FK with type field
    parent_id: Optional[UUID] = None
    parent_type: Optional[str] = None  # "location", "region", etc.

# More complex example:
class CharacterCreate(BaseModel):
    name: str
    faction_id: UUID

    # Custom compatibility rule with all options
    rank_id: Annotated[UUID, CompatibilityRule(
        parent_field="faction_id",
        parent_service="faction",
        child_service="rank",
        parent_display="Faction",
        child_display="Rank",
        parent_key_on_child="faction_id"
    )] = None

# Manual usage (if needed):
await validator.validate_parent_child_compatibility(
    data=entity_dict,
    parent_field="location_type_id",
    child_field="location_sub_type_id", 
    parent_service="location_type",
    child_service="location_sub_type",
    parent_display="Location Type",
    child_display="Location Sub Type"
)
"""