# --- START OF FILE app/game_state/repositories/base_repository.py ---


from typing import Generic, Type, TypeVar, List, Optional, Any, Dict, cast, Union
from sqlalchemy import func, or_, and_, literal_column, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import inspect as sa_inspect
from pydantic import BaseModel, ValidationError
import logging
import inspect

from sqlalchemy.sql.elements import ColumnElement  # For type hinting SQL expressions
from sqlalchemy.orm.attributes import InstrumentedAttribute  # To check if an attribute is a mapped column
from sqlalchemy.sql import expression as sql_expr  # For sqlalchemy.true() and sqlalchemy.false()

# Define type variables
EntityType = TypeVar('EntityType')
ModelType = TypeVar('ModelType')
PrimaryKeyType = TypeVar('PrimaryKeyType')

class BaseRepository(Generic[EntityType, ModelType, PrimaryKeyType]):
    """
    Generic base repository providing common CRUD operations.
    Handles conversion between domain entities and DB models.
    """

    def __init__(self, db: AsyncSession, model_cls: Type[ModelType], entity_cls: Type[EntityType]):
        if not hasattr(model_cls, '__table__') and not inspect.isclass(model_cls):
            raise ValueError(f"{model_cls.__name__} does not appear to be a SQLAlchemy model class.")
        if not inspect.isclass(entity_cls):
            raise ValueError(f"entity_cls '{entity_cls}' must be a class.")

        self.db = db
        self.model_cls = model_cls
        self.entity_cls = entity_cls

        self._pk_attr_names = set()
        self._pk_server_default_names = set()
        self._model_column_keys = set()

        try:
            # Access the table directly - this is more reliable
            table = self.model_cls.__table__

            # Get all column names from the table
            self._model_column_keys = {col.name for col in table.columns}

            # Get primary key information
            for col in table.primary_key.columns:
                self._pk_attr_names.add(col.name)
                if col.server_default is not None:
                    self._pk_server_default_names.add(col.name)

            if not self._pk_attr_names:
                logging.warning(f"No primary key columns found for model {self.model_cls.__name__}.")

        except Exception as e:
            logging.error(f"Failed to determine primary key/column info for {self.model_cls.__name__}: {e}",
                          exc_info=True)

    def _get_pk_info(self) -> tuple[str, InstrumentedAttribute]:
        """Get primary key attribute name and column. Raises if not found."""
        if not self._pk_attr_names:
            raise ValueError(f"Cannot operate: Primary key not defined for model {self.model_cls.__name__}")

        pk_attr_name = next(iter(self._pk_attr_names), None)
        if not pk_attr_name:
            raise ValueError(f"Primary key attribute name could not be determined for {self.model_cls.__name__}")

        pk_col = getattr(self.model_cls, pk_attr_name, None)
        if pk_col is None:
            raise ValueError(f"Primary key attribute '{pk_attr_name}' not found on model {self.model_cls.__name__}")

        if not isinstance(pk_col, InstrumentedAttribute):
            raise ValueError(
                f"Primary key attribute '{pk_attr_name}' on model {self.model_cls.__name__} "
                f"is not a queryable SQLAlchemy mapped attribute (type: {type(pk_col)}). "
            )

        return pk_attr_name, pk_col

    def _validate_field_attribute(self, field_name: str) -> InstrumentedAttribute:
        """Validate that a field exists and is queryable. Returns the field attribute."""
        field_attr = getattr(self.model_cls, field_name, None)
        if field_attr is None:
            raise ValueError(f"Field '{field_name}' does not exist on model {self.model_cls.__name__}.")

        if not isinstance(field_attr, InstrumentedAttribute):
            raise ValueError(
                f"Attribute '{field_name}' on model {self.model_cls.__name__} "
                f"is not a queryable SQLAlchemy mapped attribute (type: {type(field_attr)}). "
                f"It cannot be used directly in a database WHERE clause."
            )

        return field_attr

    @staticmethod
    def _create_safe_where_clause(comparison: Any, context: str = "") -> ColumnElement[bool]:
        """Convert a comparison to a safe SQLAlchemy WHERE clause.
        :param comparison:
        :param context:
        :return:
        """
        if isinstance(comparison, bool):
            logging.warning(
                f"Comparison {context} unexpectedly resulted in a Python boolean ({comparison}). "
                f"Converting to SQL true/false."
            )
            return sql_expr.true() if comparison else sql_expr.false()
        elif hasattr(comparison, 'compile'):
            return cast(ColumnElement[bool], comparison)
        else:
            raise TypeError(
                f"Comparison {context} resulted in an unsupported type: {type(comparison)}."
            )

    async def _execute_db_operation(self, db_obj: ModelType, operation: str) -> ModelType:
        """Execute flush and refresh operations with proper error handling."""
        try:
            logging.debug(f"[{operation}] Flushing session...")
            await self.db.flush()
            logging.debug(f"[{operation}] Flush successful. Refreshing object state...")
            await self.db.refresh(db_obj)
            logging.debug(f"[{operation}] Refresh successful.")
            return db_obj
        except Exception as e:
            failed_obj_state = {k: getattr(db_obj, k, 'N/A') for k in self._model_column_keys}
            logging.error(f"[{operation}] Error during flush/refresh. Object State: {failed_obj_state}, {e}", exc_info=True)
            raise

    async def _convert_to_entity(self, db_obj: ModelType) -> Optional[EntityType]:
        """Convert a database model to a domain entity using Pydantic's model_validate."""
        if db_obj is None:
            return None

        entity_type = cast(Type[EntityType], self.entity_cls)

        try:
            # Use Pydantic model_validate with from_attributes for automatic field mapping
            entity = entity_type.model_validate(db_obj, from_attributes=True)
            logging.debug(f"[_convert_to_entity] Successfully created {entity_type.__name__} entity: {entity}")
            return entity
        except ValidationError as e:
            logging.error(f"[_convert_to_entity] Pydantic validation error for {entity_type.__name__}: {e}")
            logging.error(
                f"[_convert_to_entity] DB object data: {vars(db_obj) if hasattr(db_obj, '__dict__') else 'No __dict__'}")
            raise ValueError(f"Failed to convert {self.model_cls.__name__} to {entity_type.__name__}: {e}") from e
        except Exception as e:
            logging.error(
                f"[_convert_to_entity] Unexpected error during model_validate for {entity_type.__name__}: {e}",
                exc_info=True)
            raise

    # CORE CRUD OPERATIONS

    async def create(self, entity: EntityType) -> EntityType:
        """Create a new entity. Fails if entity already exists."""
        if entity is None:
            raise ValueError("Cannot create None entity.")

        pk_attr_name, *_ = self._get_pk_info()
        pk_value = getattr(entity, pk_attr_name, None)

        # Check if entity already exists
        if pk_value is not None:
            existing = await self.db.get(self.model_cls, pk_value)
            if existing:
                raise ValueError(f"Entity with {pk_attr_name}={pk_value} already exists")

        # Prepare data for INSERT
        model_data = entity.model_dump(include=self._model_column_keys)

        # Create new DB object
        db_obj = self.model_cls(**model_data)
        self.db.add(db_obj)

        # Execute and refresh
        await self._execute_db_operation(db_obj, "Create")

        created_entity = await self._convert_to_entity(db_obj)
        logging.info(f"[Create] Entity created successfully")
        return created_entity

    async def update(self, entity: EntityType) -> EntityType:
        """Update an existing entity. Fails if entity doesn't exist."""
        if entity is None:
            raise ValueError("Cannot update None entity.")

        pk_attr_name, *_ = self._get_pk_info()
        pk_value = getattr(entity, pk_attr_name, None)
        if pk_value is None:
            raise ValueError("Cannot update entity without primary key value")

        # Get existing entity
        existing_db_obj = await self.db.get(self.model_cls, pk_value)
        if not existing_db_obj:
            raise ValueError(f"Entity with {pk_attr_name}={pk_value} not found")

        # Prepare data for UPDATE
        model_data = entity.model_dump(include=self._model_column_keys)

        # Update existing object
        for key, value in model_data.items():
            if key not in self._pk_attr_names:  # Don't update PKs
                try:
                    setattr(existing_db_obj, key, value)
                except AttributeError:
                    logging.warning(f"[Update] Attribute '{key}' not found on DB object, skipping.")

        # Execute and refresh
        await self._execute_db_operation(existing_db_obj, "Update")

        updated_entity = await self._convert_to_entity(existing_db_obj)
        logging.info(f"[Update] Entity updated successfully")
        return updated_entity

    async def save(self, entity: EntityType) -> EntityType:
        """
        Upsert operation: Create if new, update if exists.
        Convenience method that delegates to create() or update().
        """
        if entity is None:
            raise ValueError("Cannot save None entity.")

        pk_attr_name, *_ = self._get_pk_info()
        pk_value = getattr(entity, pk_attr_name, None)

        if pk_value is not None:
            existing = await self.db.get(self.model_cls, pk_value)
            if existing:
                return await self.update(entity)

        return await self.create(entity)

    async def update_entity(self, pk: PrimaryKeyType, update_data: Union[BaseModel, Dict[str, Any]]) -> Optional[
        EntityType]:
        """
        Centralized update method that accepts either a Pydantic model or dictionary.
        Uses Pydantic's model_copy(update=dict) for efficient, type-safe updates.

        Args:
            pk: Primary key of the entity to update
            update_data: Either a Pydantic model (with exclude_unset support) or a dictionary

        Returns:
            Updated entity or None if not found

        Raises:
            ValueError: If update_data contains invalid fields or values
        """
        logging.debug(f"[UpdateEntity] Updating {self.model_cls.__name__} with ID: {pk}")

        # Get existing entity
        existing_entity = await self.find_by_id(pk)
        if not existing_entity:
            logging.warning(f"[UpdateEntity] Entity not found for ID: {pk}")
            return None

        # Convert update_data to dictionary
        if isinstance(update_data, BaseModel):
            update_dict = update_data.model_dump(exclude_unset=True)
        else:
            update_dict = update_data

        # If no fields to update, return existing entity
        if not update_dict:
            logging.debug(f"[UpdateEntity] No fields to update for ID: {pk}")
            return existing_entity

        # Apply updates using model_copy from Pydantic for clean, efficient updates
        logging.debug(f"[UpdateEntity] Applying updates: {list(update_dict.keys())}")
        try:
            updated_entity = existing_entity.model_copy(update=update_dict)
        except Exception as e:
            logging.error(f"[UpdateEntity] Error applying updates using model_copy: {e}", exc_info=True)
            raise ValueError(f"Invalid update data: {e}") from e

        # Save the updated entity
        try:
            saved_entity = await self.save(updated_entity)
            logging.info(f"[UpdateEntity] Successfully updated entity with ID: {pk}")
            return saved_entity
        except Exception as e:
            logging.error(f"[UpdateEntity] Error saving updated entity with ID {pk}: {e}", exc_info=True)
            raise

    # READ OPERATIONS

    async def find_by_id(self, pk: PrimaryKeyType) -> Optional[EntityType]:
        pk_attr_name, *_ = self._get_pk_info()  # Validates PK exists
        logging.debug(f"[FindByID] Looking for {self.model_cls.__name__} with ID: {pk}")

        db_obj = await self.db.get(self.model_cls, pk)
        if db_obj:
            logging.debug(f"[FindByID] Found object in session/DB. Converting to entity.")
            return await self._convert_to_entity(db_obj)
        else:
            logging.debug(f"[FindByID] Object not found for ID: {pk}")
            return None

    async def find_by_id_full(
        self,
        pk: PrimaryKeyType
    ) -> Optional[Dict[str, Any]]:
        pk_attr, _ = self._get_pk_info()
        mapper = sa_inspect(self.model_cls)

        # eager‐load every relationship
        loader_opts = [
            selectinload(getattr(self.model_cls, rel.key))
            for rel in mapper.relationships
        ]
        stmt = (
            select(self.model_cls)
            .options(*loader_opts)
            .filter_by(**{pk_attr: pk})
        )
        result = await self.db.execute(stmt)
        db_obj = result.scalars().one_or_none()
        if not db_obj:
            return None

        # 1) flatten the table columns
        payload: Dict[str, Any] = {
            col.name: getattr(db_obj, col.name)
            for col in self.model_cls.__table__.columns
        }

        # 2) for each relationship
        for rel in mapper.relationships:
            rel_val = getattr(db_obj, rel.key)

            if rel.uselist:
                # collections always become a list (possibly empty)
                payload[rel.key] = [
                    {"id": item.id, "name": item.name}
                    for item in (rel_val or [])
                ]
            else:
                # **scalar**: only nest when not None
                if rel_val is None:
                    payload[rel.key] = None
                else:
                    payload[rel.key] = {
                        "id":   rel_val.id,
                        "name": rel_val.name
                    }

        return payload

    async def get_entity(self, pk: PrimaryKeyType) -> Optional[EntityType]:
        """
        Get the raw domain entity by ID without any schema conversion.
        Use this for internal service-to-service operations that need business logic.
        Alias for find_by_id for clarity.
        """
        return await self.find_by_id(pk)

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[EntityType]:
        logging.info(f"[FindAll] Fetching {self.model_cls.__name__} entities (skip={skip}, limit={limit})")
        stmt = select(self.model_cls).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        logging.debug(f"[FindAll] Found {len(db_objs)} DB objects. Converting to entities.")
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]
        return [entity for entity in entities if entity is not None]

    async def get_all_entities(self, skip: int = 0, limit: int = 100) -> List[EntityType]:
        """
        Get all raw domain entities with pagination.
        Use this when you need business logic access on multiple entities.
        Alias for find_all for clarity.
        """
        return await self.find_all(skip, limit)

    async def exists(self, pk: PrimaryKeyType) -> bool:
        pk_attr_name, pk_col = self._get_pk_info()
        logging.debug(f"[Exists] Checking existence for {self.model_cls.__name__} with ID: {pk}")

        potential_comparison = (pk_col == pk)
        actual_comparison = self._create_safe_where_clause(
            potential_comparison,
            f"for {self.model_cls.__name__}.{pk_attr_name} == {pk!r}"
        )

        exists_subquery = select(literal_column("1")).select_from(self.model_cls).where(actual_comparison).exists()
        stmt = select(exists_subquery)

        result = await self.db.execute(stmt)
        does_exist = result.scalar_one_or_none()

        logging.debug(f"[Exists] Result for ID {pk}: {does_exist}")
        return bool(does_exist)

    async def get_by_field(self, field_name: str, value: Any) -> Optional[EntityType]:
        field_attr = self._validate_field_attribute(field_name)

        potential_sql_filter = (field_attr == value)
        actual_filter = self._create_safe_where_clause(
            potential_sql_filter,
            f"for {self.model_cls.__name__}.{field_name} == {value!r}"
        )

        stmt = select(self.model_cls).where(actual_filter)
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        return await self._convert_to_entity(db_obj) if db_obj else None

    async def find_by_name(self, name: str) -> Optional[EntityType]:
        logging.debug(f"[FindByName] Looking for {self.model_cls.__name__} with name: '{name}'")
        try:
            return await self.get_by_field('name', name)
        except ValueError as e:
            logging.error(f"[FindByName] Error for {self.model_cls.__name__} with name '{name}': {e}")
            # Re-raise with context, or handle if 'name' field specifically is the issue
            if "Field 'name' does not exist" in str(e) or "Attribute 'name' on model" in str(e):
                raise ValueError(
                    f"Cannot find by name: Model {self.model_cls.__name__} problem with 'name' field. Original: {e}")
            raise  # Re-raise other ValueErrors from get_by_field

    async def find_by_name_insensitive(self, name: str) -> Optional[EntityType]:
        logging.debug(
            f"[FindByNameInsensitive] Looking for {self.model_cls.__name__} with name (case-insensitive): '{name}'")

        field_attr = self._validate_field_attribute('name')
        potential_sql_filter = (func.lower(field_attr) == name.lower())
        actual_filter = self._create_safe_where_clause(
            potential_sql_filter,
            f"case-insensitive name comparison for {self.model_cls.__name__}"
        )

        result = await self.db.execute(select(self.model_cls).where(actual_filter))
        db_obj = result.scalar_one_or_none()
        return await self._convert_to_entity(db_obj) if db_obj else None

    async def find_all_by_name(self, name: str, partial_match: bool = True) -> List[EntityType]:
        logging.debug(
            f"[FindAllByName] Looking for {self.model_cls.__name__} with name: '{name}', partial_match={partial_match}")

        field_attr = self._validate_field_attribute('name')

        if partial_match:
            potential_sql_filter = field_attr.ilike(f'%{name}%')
        else:
            potential_sql_filter = (field_attr == name)

        actual_filter = self._create_safe_where_clause(
            potential_sql_filter,
            f"name comparison (partial_match={partial_match}) for {self.model_cls.__name__}"
        )

        stmt = select(self.model_cls).where(actual_filter)
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()

        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]
        logging.debug(f"[FindAllByName] Found {len(entities)} {self.model_cls.__name__} matching name: '{name}'")
        return entities

    async def find_by_field_list(self, field_name: str, values: List[Any]) -> List[EntityType]:
        logging.debug(
            f"[FindByFieldList] Looking for {self.model_cls.__name__} where {field_name} in list of {len(values)} values")

        if not values:
            return []

        field_attr = self._validate_field_attribute(field_name)

        stmt = select(self.model_cls).where(field_attr.in_(values))
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()

        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]
        logging.debug(
            f"[FindByFieldList] Found {len(entities)} {self.model_cls.__name__} with {field_name} in value list")
        return entities

    async def find_by_multiple_fields(self, field_values: Dict[str, Any], match_all: bool = True) -> List[EntityType]:
        logging.debug(
            f"[FindByMultipleFields] Looking for {self.model_cls.__name__} matching {len(field_values)} fields, match_all={match_all}")

        if not field_values:
            return []

        conditions: List[ColumnElement[bool]] = []
        for field_name, value in field_values.items():
            field_attr = self._validate_field_attribute(field_name)
            comparison = (field_attr == value)
            safe_condition = self._create_safe_where_clause(comparison, f"for field {field_name}")
            conditions.append(safe_condition)

        stmt = select(self.model_cls)
        if match_all:
            stmt = stmt.where(and_(*conditions))
        else:
            stmt = stmt.where(or_(*conditions))

        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]

        logging.debug(f"[FindByMultipleFields] Found {len(entities)} matching {self.model_cls.__name__}")
        return entities

    # DELETE OPERATIONS

    async def delete(self, pk: PrimaryKeyType) -> bool:
        self._get_pk_info()  # Validates PK exists
        logging.debug(f"[Delete] Attempting to delete {self.model_cls.__name__} with ID: {pk}")

        db_obj = await self.db.get(self.model_cls, pk)
        if db_obj:
            logging.info(f"[Delete] Found object with ID: {pk}. Proceeding with delete.")
            await self.db.delete(db_obj)
            try:
                await self.db.flush()
                logging.info(f"[Delete] Successfully deleted object with ID: {pk}")
                return True
            except Exception as e:
                logging.error(f"[Delete] Error during flush after delete for ID {pk}: {e}", exc_info=True)
                await self.db.rollback()
                return False
        else:
            logging.warning(f"[Delete] Object not found for deletion with ID: {pk}")
            return False

    # UTILITY OPERATIONS

    async def count_all(self, conditions: Optional[List[ColumnElement[bool]]] = None) -> int:
        logging.debug(f"[CountAll] Counting {self.model_cls.__name__} entities.")
        pk_to_count_attr = None
        if self._pk_attr_names:
            pk_name = next(iter(self._pk_attr_names), None)
            if pk_name:
                pk_to_count_attr = getattr(self.model_cls, pk_name, None)

        if pk_to_count_attr:
            stmt_select = select(func.count(pk_to_count_attr))
        else:
            first_column_name = next(iter(self._model_column_keys), None)
            if first_column_name:
                first_column_attr = getattr(self.model_cls, first_column_name)
                stmt_select = select(func.count(first_column_attr))
            else:
                logging.error(f"Cannot count {self.model_cls.__name__}: no columns found.")
                return 0

        if conditions:
            stmt_select = stmt_select.where(*conditions)

        result = await self.db.execute(stmt_select)
        count = result.scalar_one_or_none() or 0
        logging.debug(f"[CountAll] Total count: {count}")
        return count

    async def find_all_paginated(
            self,
            skip: int = 0,
            limit: int = 100,
            conditions: Optional[List[ColumnElement[bool]]] = None,
            order_by: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        logging.debug(
            f"[FindAllPaginated] Fetching {self.model_cls.__name__} "
            f"(skip={skip}, limit={limit}, conditions={conditions is not None}, order_by={order_by is not None})"
        )

        stmt = select(self.model_cls)
        if conditions:
            stmt = stmt.where(*conditions)
        if order_by:
            stmt = stmt.order_by(*order_by)
        stmt = stmt.offset(skip).limit(limit)

        result_items = await self.db.execute(stmt)
        db_objs = result_items.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]
        valid_entities = [entity for entity in entities if entity is not None]

        total_count = await self.count_all(conditions=conditions)

        logging.debug(f"[FindAllPaginated] Found {len(valid_entities)} items for page, total items: {total_count}")
        return {
            "items": valid_entities,
            "total": total_count,
            "limit": limit,
            "skip": skip,
        }

    # BULK OPERATIONS

    async def bulk_save(self, entities: List[EntityType]) -> List[EntityType]:
        if not entities:
            logging.warning("[BulkSave] Received empty entity list")
            return []

        pk_attr_name, *_ = self._get_pk_info()
        logging.info(f"[BulkSave] Saving {len(entities)} {self.model_cls.__name__} entities")

        new_entities_data = []
        existing_entities_to_update = []

        for entity in entities:
            pk_value = getattr(entity, pk_attr_name, None)

            if pk_value is None:  # For UUID entities, None means new
                model_dict = entity.model_dump(include=self._model_column_keys)
                new_entities_data.append(model_dict)
            else:
                existing_entities_to_update.append(entity)

        saved_entities_list: List[EntityType] = []

        # Process new entities
        if new_entities_data:
            try:
                db_objs_to_insert = []
                for model_dict in new_entities_data:
                    db_obj = self.model_cls(**model_dict)
                    self.db.add(db_obj)
                    db_objs_to_insert.append(db_obj)

                await self.db.flush()

                for db_obj in db_objs_to_insert:
                    await self.db.refresh(db_obj)
                    saved_entity = await self._convert_to_entity(db_obj)
                    if saved_entity:
                        saved_entities_list.append(saved_entity)

                logging.debug(f"[BulkSave] Successfully processed {len(db_objs_to_insert)} new entities.")

            except Exception as e:
                logging.error(f"[BulkSave] Error during bulk insert processing: {e}", exc_info=True)
                await self.db.rollback()
                raise

        # Process existing entities individually
        if existing_entities_to_update:
            try:
                for entity in existing_entities_to_update:
                    saved_entity = await self.save(entity)
                    saved_entities_list.append(saved_entity)

                logging.debug(
                    f"[BulkSave] Successfully saved/updated {len(existing_entities_to_update)} existing entities.")

            except Exception as e:
                logging.error(f"[BulkSave] Error during individual updates: {e}", exc_info=True)
                await self.db.rollback()
                raise

        return saved_entities_list

    async def bulk_delete(self, pks: List[PrimaryKeyType]) -> int:
        """Bulk delete entities by their IDs. Returns the number of entities deleted."""
        if not pks:
            logging.warning("[BulkDelete] Received empty entity ID list")
            return 0

        pk_attr_name, pk_column = self._get_pk_info()
        logging.info(f"[BulkDelete] Deleting {len(pks)} {self.model_cls.__name__} entities")

        try:
            stmt = delete(self.model_cls).where(pk_column.in_(pks))

            result = await self.db.execute(stmt)
            await self.db.flush()

            deleted_count = result.rowcount or 0
            logging.info(f"[BulkDelete] Successfully deleted {deleted_count} entities")
            return deleted_count

        except Exception as e:
            logging.error(f"[BulkDelete] Error during bulk delete: {e}", exc_info=True)
            await self.db.rollback()
            raise

# --- END OF FILE app/game_state/repositories/base_repository.py ---