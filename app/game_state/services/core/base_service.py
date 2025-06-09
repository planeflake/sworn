# app/game_state/services/base_service.py

"""
Simple base service providing standardized create functionality.
Focuses on core patterns without over-engineering.
"""

from typing import Generic, TypeVar, Type, Dict, Any
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import logging

from app.game_state.services.core.validation.service_validaton_utils import ServiceValidationUtils, ValidationError

# Type variables
EntityType = TypeVar('EntityType', bound=BaseModel)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
ResponseType = TypeVar('ResponseType', bound=BaseModel)

logger = logging.getLogger(__name__)


class BaseService(Generic[EntityType, CreateSchemaType, ResponseType]):
    """
    Simple base service providing standardized create functionality.

    Features:
    - Standardized create with validation
    - Foreign key validation
    - Hook methods for customization
    - Consistent error handling
    """

    def __init__(
            self,
            db: AsyncSession,
            repository: Any,
            entity_class: Type[EntityType],
            response_class: Type[ResponseType]
    ):
        self.db = db
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)
        self.validator = ServiceValidationUtils(db)

        # Type classes
        self._entity_class = entity_class
        self._response_class = response_class

    async def create_entity(
            self,
            entity_data: CreateSchemaType,
            validation_schema: Type[BaseModel] = None
    ) -> ResponseType:
        """
        Standardized entity creation with validation.

        Args:
            entity_data: Pydantic schema with entity data
            validation_schema: Schema to auto-detect FK validations from
        """
        entity_name = self._entity_class.__name__
        self.logger.info(f"Creating {entity_name}")

        try:
            # Convert to dict for processing
            entity_dict = entity_data #.model_dump()

            # Validation phase
            await self._validate_creation(entity_dict, validation_schema)

            # Pre-creation processing (hook for customization)
            await self._pre_create_processing(entity_dict, entity_data)

            # Generate ID if not provided
            if 'id' not in entity_dict or entity_dict['id'] is None:
                entity_dict['id'] = uuid4()

            # Convert to entity and create
            entity = self._entity_class.model_validate(entity_dict)
            created_entity = await self.repository.create(entity)

            # Post-creation processing (hook for customization)
            await self._post_create_processing(created_entity, entity_data)

            # Convert to response format
            response = self._response_class.model_validate(created_entity.model_dump())

            self.logger.info(f"Successfully created {entity_name} {created_entity.id}")
            return response

        except ValidationError as e:
            self.logger.warning(f"Validation failed during {entity_name} creation: {e}")
            raise ValueError(f"Validation failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error creating {entity_name}: {e}", exc_info=True)
            raise

    # ==============================================================================
    # HOOK METHODS (Override in child services as needed)
    # ==============================================================================

    async def find_all(self) -> EntityType:
        """Override for entity retrieval"""
        logging.info(f"[location_service]-Finding all entities")
        locations = await self.repository.find_all()
        logging.info(f"[location_service]-Found all entities")
        return locations

    async def find_by_id(self, entity_id: UUID) -> EntityType:
        """Override for entity retrieval by ID"""
        logging.info(f"[location_service]-Finding entity by ID {entity_id}")
        locations = await self.repository.find_by_id(entity_id)
        logging.info(f"[location_service]-Found entity by ID {entity_id}")
        return locations

    async def find_by_id_full(self, entity_id: UUID) -> EntityType:
        """Override for entity retrieval by ID with full details"""
        logging.info(f"[location_service]-Finding entity by ID {entity_id} with full details")
        locations = await self.repository.find_by_id_full(entity_id)
        logging.info(f"[location_service]-Found entity by ID {entity_id} with full details")
        return locations

    async def _validate_creation(
            self,
            entity_dict: Dict[str, Any],
            validation_schema: Type[BaseModel] = None
    ):
        """
        Override for entity-specific creation validation.
        Base implementation does automatic FK validation.
        """
        # Auto-detect and validate foreign keys from schema
        if validation_schema:
            await self.validator.validate_schema_foreign_keys(entity_dict, validation_schema)

    async def _pre_create_processing(self, entity_dict: Dict[str, Any], original_data: CreateSchemaType):
        """Override for pre-creation processing (e.g., setting defaults, transformations)"""
        pass

    async def _post_create_processing(self, created_entity: EntityType, original_data: CreateSchemaType):
        """Override for post-creation processing (e.g., related entity creation, notifications)"""
        pass

    async def exists(self, entity_id: UUID) -> bool:
        """Check if an entity exists by ID."""
        return await self.repository.exists(entity_id)
