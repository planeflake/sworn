# --- START OF FILE app/game_state/repositories/base_repository.py ---

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import class_mapper
from sqlalchemy import func, or_, and_, literal_column
from typing import Generic, Type, TypeVar, List, Optional, Any, Dict, cast
from uuid import UUID
import dataclasses
from dataclasses import fields, is_dataclass
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
            mapper = class_mapper(self.model_cls)
            self._model_column_keys = {prop.key for prop in mapper.column_attrs}
            for col in mapper.primary_key:
                self._pk_attr_names.add(col.key)
                if col.server_default is not None:
                    self._pk_server_default_names.add(col.key)
            if not self._pk_attr_names:
                logging.warning(f"No primary key columns found for model {self.model_cls.__name__}.")
        except Exception as e:
            logging.error(f"Failed to determine primary key/column info for {self.model_cls.__name__}: {e}",
                          exc_info=True)

    async def _entity_to_model_dict(self, entity: EntityType, is_new: bool = False) -> Dict[str, Any]:
        if entity is None:
            logging.error("Received None entity for conversion to model dict.")
            raise ValueError("Cannot convert None entity to dict.")

        # Ensure entity is dataclass for 'asdict', or use vars
        entity_for_dict = cast(Any, entity)

        if dataclasses.is_dataclass(entity_for_dict):
            entity_data = dataclasses.asdict(entity_for_dict)
        else:
            try:
                entity_data = vars(entity_for_dict).copy()
            except TypeError:
                raise TypeError(f"Cannot convert entity of type {type(entity_for_dict)} to dict.")

        logging.debug(f"[_entity_to_model_dict] Original entity data keys: {list(entity_data.keys())}")

        # Handle entity_id -> id mapping BEFORE filtering
        if 'entity_id' in entity_data and 'id' in self._model_column_keys and 'id' not in entity_data:
            entity_data['id'] = entity_data.pop('entity_id')

        model_data = {
            key: value for key, value in entity_data.items()
            if key in self._model_column_keys
        }
        logging.debug(f"[_entity_to_model_dict] Filtered model data keys: {list(model_data.keys())}")

        for key, value in model_data.items():
            if isinstance(value, dict) and value:
                has_uuid_keys = any(isinstance(k, UUID) for k in value.keys())
                if has_uuid_keys:
                    logging.debug(f"[_entity_to_model_dict] Converting UUID keys to strings in field '{key}'")
                    model_data[key] = {str(k): v for k, v in value.items()}

        if is_new:
            keys_to_remove = set()
            for pk_name in self._pk_server_default_names:
                if pk_name in model_data:
                    keys_to_remove.add(pk_name)
            if keys_to_remove:
                logging.debug(f"[_entity_to_model_dict] Removing server-default PKs for insert: {keys_to_remove}")
                for key in keys_to_remove:
                    model_data.pop(key, None)

        logging.debug(f"[_entity_to_model_dict] Final model dict keys for SQLAlchemy: {list(model_data.keys())}")
        return model_data

    async def _convert_to_entity(self, db_obj: ModelType) -> Optional[EntityType]:
        if db_obj is None:
            return None

        entity_type = cast(Type[EntityType], self.entity_cls)

        if is_dataclass(entity_type):  # Runtime check if it's a dataclass
            pass  # No assertion needed here, inspect.is_dataclass handles it

        mapper = class_mapper(self.model_cls)
        db_data = {}

        for prop in mapper.column_attrs:
            prop_key = prop.key
            if prop_key in db_obj.__dict__:
                try:
                    db_data[prop_key] = db_obj.__dict__[prop_key]
                except Exception as e:
                    logging.warning(
                        f"[_convert_to_entity] Error accessing attribute '{prop_key}' directly on {self.model_cls.__name__}: {e}")
                    db_data[prop_key] = None
            else:
                # Prevents accidental lazy-load of expired attribute
                db_data[prop_key] = None

        # Safely handle relationships to avoid async/greenlet issues with lazy loading
        for prop in mapper.relationships:
            prop_key = prop.key
            # Instead of using hasattr which can trigger lazy loading, check if relationship is already loaded
            # This avoids the "greenlet_spawn has not been called" error in async contexts
            if db_obj.__dict__.get(prop_key) is not None:
                try:
                    # Only access if it's already loaded (we know it is from the check above)
                    value = getattr(db_obj, prop_key, None)
                    db_data[prop_key] = value
                except Exception as e:
                    logging.warning(
                        f"[_convert_to_entity] Error accessing relationship '{prop_key}' on {self.model_cls.__name__}: {e}")
                    db_data[prop_key] = None
            else:
                # Default to None or empty list depending on relationship type
                db_data[prop_key] = [] if prop.uselist else None

        entity_args = db_data.copy()
        required_entity_fields = set()

        if 'id' in entity_args and 'entity_id' not in entity_args:
            entity_args['entity_id'] = entity_args['id']

        for key, value in entity_args.items():
            if isinstance(value, dict) and value:
                candidate_uuid_strings = [
                    k for k in value.keys()
                    if isinstance(k, str) and '-' in k and len(k) >= 32  # Basic UUID string check
                ]

                if candidate_uuid_strings:
                    try:
                        # Attempt to convert all string keys if any look like UUIDs
                        uuid_dict = {}
                        conversion_successful = True
                        for k_str, v_item in value.items():
                            if isinstance(k_str, str) and '-' in k_str and len(k_str) >= 32:
                                try:
                                    uuid_dict[UUID(k_str)] = v_item
                                except ValueError:
                                    uuid_dict[k_str] = v_item  # Keep original if not a valid UUID
                                    conversion_successful = False  # Mark if any key fails
                            else:
                                uuid_dict[k_str] = v_item  # Keep non-string or non-UUID-like keys

                        entity_args[key] = uuid_dict
                        if conversion_successful and candidate_uuid_strings:  # Log only if something was actually converted
                            logging.debug(f"[_convert_to_entity] Converted some string keys to UUIDs in field '{key}'")
                        elif not conversion_successful and candidate_uuid_strings:
                            logging.debug(
                                f"[_convert_to_entity] Attempted UUID key conversion in '{key}', some failed or were not UUIDs.")

                    except Exception as e_conv:  # Catch broader errors during dict manipulation
                        logging.warning(
                            f"[_convert_to_entity] Error during UUID key conversion for field '{key}': {e_conv}")
                        pass  # Keep original if complex error

        try:
            if is_dataclass(entity_type):
                entity_fields = fields(entity_type)
                constructor_field_names = {f.name for f in entity_fields if f.init}
                required_entity_fields = {
                    f.name for f in entity_fields
                    if f.init and f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING
                }
                constructor_args = {k: v for k, v in entity_args.items() if k in constructor_field_names}
            else:  # For non-dataclass entities
                init_sig = inspect.signature(entity_type.__init__)
                init_params = init_sig.parameters
                constructor_field_names = {p for p in init_params if p != 'self'}
                required_entity_fields = {
                    p.name for p in init_params.values()
                    if
                    p.name != 'self' and p.default is inspect.Parameter.empty and p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
                }
                constructor_args = {k: v for k, v in entity_args.items() if k in constructor_field_names}
        except Exception as e:
            logging.error(f"Error inspecting entity class {entity_type.__name__}: {e}", exc_info=True)
            constructor_args = entity_args

        missing_required = required_entity_fields - set(constructor_args.keys())
        if missing_required:
            logging.error(
                f"Cannot instantiate entity {entity_type.__name__}: Missing required fields from DB data: {missing_required}. Available data keys: {list(entity_args.keys())}")
            raise TypeError(f"Missing required data to create entity {entity_type.__name__}: {missing_required}")

        logging.debug(
            f"[_convert_to_entity] Constructor args for {entity_type.__name__} keys: {list(constructor_args.keys())}")

        try:
            entity = entity_type(**constructor_args)
            return entity
        except TypeError as e:
            logging.error(
                f"TypeError instantiating entity {entity_type.__name__}. Check constructor arguments vs provided.",
                exc_info=True)
            logging.error(f"  Provided args keys: {list(constructor_args.keys())}")
            logging.error(f"  Required args (estimated): {required_entity_fields}")
            raise TypeError(
                f"Failed to instantiate entity {entity_type.__name__} (Mismatched arguments - see logs): {e}") from e
        except Exception as e:
            logging.error(f"Unexpected error during entity instantiation for {entity_type.__name__}: {e}",
                          exc_info=True)
            raise

    async def save(self, entity: EntityType) -> EntityType:
        logging.info(f"[Save Method Entry] Received entity: {entity}")
        if entity is None:
            logging.error("[Save Method Entry] Received None entity! Raising error.")
            raise ValueError("Cannot save None entity.")

        pk_value = None
        pk_attr_name = None
        if self._pk_attr_names:
            pk_attr_name = next(iter(self._pk_attr_names), None)  # Added default None
            if pk_attr_name:
                pk_value = getattr(entity, pk_attr_name, None)

        existing_db_obj = None
        if pk_value is not None:
            logging.debug(f"[Save] Entity has PK {pk_value}. Checking database existence.")
            existing_db_obj = await self.db.get(self.model_cls, pk_value)
            if existing_db_obj:
                logging.debug(f"[Save] Object with PK {pk_value} found in DB. Proceeding with UPDATE.")
            else:
                logging.debug(
                    f"[Save] Object with PK {pk_value} NOT found in DB. Proceeding with INSERT (using entity's PK).")
        else:
            logging.debug(
                "[Save] Entity has no PK (or PK attribute not found). Proceeding with INSERT (expecting server default PK).")

        is_new_insert = existing_db_obj is None

        is_server_default_pk = pk_attr_name in self._pk_server_default_names if pk_attr_name else False
        model_data = await self._entity_to_model_dict(entity, is_new=is_new_insert and is_server_default_pk)

        if is_new_insert:
            logging.debug("[Save] Performing INSERT.")
            db_obj = self.model_cls(**model_data)
            self.db.add(db_obj)
            merged_db_obj = db_obj
            logging.debug(
                f"[Save] Added new {self.model_cls.__name__} instance to session (PK likely provided by entity or to be server-generated).")
        else:
            db_obj = existing_db_obj
            if db_obj is None:  # Should not happen if is_new_insert is False, but as a safeguard
                raise RuntimeError(f"Save logic error: existing_db_obj is None during an update for PK {pk_value}")
            logging.debug(f"[Save] Performing UPDATE for PK: {pk_value}.")
            logging.debug(f"[Save] Updating attributes on existing object.")
            for key, value in model_data.items():
                if key not in self._pk_attr_names:  # Don't try to update PKs
                    try:
                        setattr(db_obj, key, value)
                    except AttributeError:
                        logging.warning(
                            f"[Save] Attribute '{key}' not found on existing DB object during update, skipping.")
            merged_db_obj = db_obj

        try:
            logging.info("[Save] Flushing session...")
            await self.db.flush()
            logging.info(f"[Save] Flush successful. Refreshing object state...")
            await self.db.refresh(merged_db_obj)
            logging.info(f"[Save] Refresh successful.")
        except Exception as e:
            failed_obj_state = {k: getattr(merged_db_obj, k, 'N/A') for k in self._model_column_keys}
            logging.error(f"[Save] Error during flush/refresh. Object State: {failed_obj_state, e}", exc_info=True)
            raise

        logging.debug(f"[Save] Converting refreshed DB object back to entity...")
        entity_to_return = await self._convert_to_entity(merged_db_obj)
        if entity_to_return is None:
            raise RuntimeError("Failed to convert refreshed DB object back to entity after save.")

        final_pk_value = getattr(entity_to_return, pk_attr_name, 'N/A') if pk_attr_name else 'N/A'
        logging.info(f"[Save] Entity saved/updated successfully (Final PK: {final_pk_value}).")
        return entity_to_return

    async def find_by_id(self, entity_id: PrimaryKeyType) -> Optional[EntityType]:
        if not self._pk_attr_names:
            raise ValueError(f"Cannot find_by_id: Primary key not defined for model {self.model_cls.__name__}")
        logging.debug(f"[FindByID] Looking for {self.model_cls.__name__} with ID: {entity_id}")
        db_obj = await self.db.get(self.model_cls, entity_id)
        if db_obj:
            logging.debug(f"[FindByID] Found object in session/DB. Converting to entity.")
            return await self._convert_to_entity(db_obj)
        else:
            logging.debug(f"[FindByID] Object not found for ID: {entity_id}")
            return None

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[EntityType]:
        logging.debug(f"[FindAll] Fetching {self.model_cls.__name__} entities (skip={skip}, limit={limit})")
        stmt = select(self.model_cls).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        logging.debug(f"[FindAll] Found {len(db_objs)} DB objects. Converting to entities.")
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]
        return [entity for entity in entities if entity is not None]  # Ensure only non-None entities

    async def delete(self, entity_id: PrimaryKeyType) -> bool:
        if not self._pk_attr_names:
            raise ValueError(f"Cannot delete: Primary key not defined for model {self.model_cls.__name__}")
        logging.debug(f"[Delete] Attempting to delete {self.model_cls.__name__} with ID: {entity_id}")
        db_obj = await self.db.get(self.model_cls, entity_id)
        if db_obj:
            logging.info(f"[Delete] Found object with ID: {entity_id}. Proceeding with delete.")
            await self.db.delete(db_obj)
            try:
                await self.db.flush()
                logging.info(f"[Delete] Successfully deleted object with ID: {entity_id}")
                return True
            except Exception as e:
                logging.error(f"[Delete] Error during flush after delete for ID {entity_id}: {e}", exc_info=True)
                await self.db.rollback()  # Rollback on error during flush
                return False
        else:
            logging.warning(f"[Delete] Object not found for deletion with ID: {entity_id}")
            return False

    async def exists(self, entity_id: PrimaryKeyType) -> bool:
        if not self._pk_attr_names:
            raise ValueError(f"Cannot check existence: Primary key not defined for model {self.model_cls.__name__}")

        logging.debug(f"[Exists] Checking existence for {self.model_cls.__name__} with ID: {entity_id}")

        # Ensure pk_attr_name is valid and pk_col is an InstrumentedAttribute
        pk_attr_name = next(iter(self._pk_attr_names), None)
        if not pk_attr_name:  # Should be caught by the first check, but defensive
            raise ValueError(f"Primary key attribute name could not be determined for {self.model_cls.__name__}")

        pk_col = getattr(self.model_cls, pk_attr_name, None)
        if pk_col is None:  # Should not happen if _pk_attr_names is populated correctly
            raise ValueError(f"Primary key attribute '{pk_attr_name}' not found on model {self.model_cls.__name__}")

        if not isinstance(pk_col, InstrumentedAttribute):
            raise ValueError(
                f"Primary key attribute '{pk_attr_name}' on model {self.model_cls.__name__} "
                f"is not a queryable SQLAlchemy mapped attribute (type: {type(pk_col)}). "
                f"Cannot use for existence check."
            )

        # Now, create the comparison expression and ensure it's a SQL expression
        potential_comparison = (pk_col == entity_id)
        actual_comparison_for_where: ColumnElement[bool]

        if isinstance(potential_comparison, bool):
            logging.warning(
                f"PK comparison in exists() for {self.model_cls.__name__}.{pk_attr_name} == {entity_id!r} "
                f"unexpectedly resulted in a Python boolean ({potential_comparison}). "
                f"Converting to SQL true/false. This might indicate an issue."
            )
            actual_comparison_for_where = sql_expr.true() if potential_comparison else sql_expr.false()
        elif hasattr(potential_comparison, 'compile'):  # Duck-typing for SQLAlchemy clause elements
            actual_comparison_for_where = cast(ColumnElement[bool], potential_comparison)
        else:
            raise TypeError(
                f"The PK comparison in exists() for {self.model_cls.__name__}.{pk_attr_name} == {entity_id!r} "
                f"resulted in an unsupported type: {type(potential_comparison)}."
            )

        # Create EXISTS subquery using the validated comparison
        # Option 1: Using .exists() method on a select statement
        exists_subquery = select(literal_column("1")).select_from(self.model_cls).where(
            actual_comparison_for_where).exists()

        # Wrap in SELECT to get scalar boolean
        stmt = select(exists_subquery)

        # Option 2: Using sqlalchemy.exists() function (more explicit sometimes)
        # from sqlalchemy import exists as sql_exists_func # alias if 'exists' is already a method name
        # exists_clause = sql_exists_func(select(literal_column("1")).select_from(self.model_cls).where(actual_comparison_for_where))
        # stmt = select(exists_clause)

        result = await self.db.execute(stmt)
        does_exist = result.scalar_one_or_none()

        logging.debug(f"[Exists] Result for ID {entity_id}: {does_exist}")
        return bool(does_exist)  # Ensure it's a Python bool if scalar_one_or_none() returns None

    async def get_by_field(self, field_name: str, value: Any) -> Optional[EntityType]:
        field_attr = getattr(self.model_cls, field_name, None)
        if field_attr is None:
            raise ValueError(f"Field '{field_name}' does not exist on model {self.model_cls.__name__}.")

        if not isinstance(field_attr, InstrumentedAttribute):
            raise ValueError(
                f"Attribute '{field_name}' on model {self.model_cls.__name__} "
                f"is not a queryable SQLAlchemy mapped attribute (type: {type(field_attr)}). "
                f"It cannot be used directly in a database WHERE clause."
            )

        potential_sql_filter = (field_attr == value)
        actual_filter_for_where_clause: ColumnElement[bool]

        if isinstance(potential_sql_filter, bool):
            logging.warning(
                f"Comparison for {self.model_cls.__name__}.{field_name} == {value!r} "
                f"unexpectedly resulted in a Python boolean ({potential_sql_filter}). "
                f"Converting to SQL true/false."
            )
            actual_filter_for_where_clause = sql_expr.true() if potential_sql_filter else sql_expr.false()
        elif hasattr(potential_sql_filter, 'compile'):
            actual_filter_for_where_clause = cast(ColumnElement[bool], potential_sql_filter)
        else:
            raise TypeError(
                f"The comparison for {self.model_cls.__name__}.{field_name} == {value!r} "
                f"resulted in an unsupported type: {type(potential_sql_filter)}."
            )

        stmt = select(self.model_cls).where(actual_filter_for_where_clause)
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
        field_attr = getattr(self.model_cls, 'name', None)
        if field_attr is None:
            raise ValueError(f"Cannot find by name: {self.model_cls.__name__} does not have a 'name' field.")

        if not isinstance(field_attr, InstrumentedAttribute):
            raise ValueError(
                f"Attribute 'name' on model {self.model_cls.__name__} "
                f"is not a queryable SQLAlchemy mapped attribute. Found type: {type(field_attr)}."
            )

        potential_sql_filter = (func.lower(field_attr) == name.lower())
        actual_filter_for_where_clause: ColumnElement[bool]

        if isinstance(potential_sql_filter, bool):
            logging.warning(
                f"Case-insensitive name comparison for {self.model_cls.__name__} "
                f"unexpectedly resulted in a Python boolean ({potential_sql_filter}). "
                f"Converting to SQL true/false."
            )
            actual_filter_for_where_clause = sql_expr.true() if potential_sql_filter else sql_expr.false()
        elif hasattr(potential_sql_filter, 'compile'):
            actual_filter_for_where_clause = cast(ColumnElement[bool], potential_sql_filter)
        else:
            raise TypeError(
                f"Case-insensitive name comparison for {self.model_cls.__name__} "
                f"resulted in an unsupported type: {type(potential_sql_filter)}."
            )

        result = await self.db.execute(
            select(self.model_cls).where(actual_filter_for_where_clause)
        )
        db_obj = result.scalar_one_or_none()
        return await self._convert_to_entity(db_obj) if db_obj else None

    async def find_all_by_name(self, name: str, partial_match: bool = True) -> List[EntityType]:
        logging.debug(
            f"[FindAllByName] Looking for {self.model_cls.__name__} with name: '{name}', partial_match={partial_match}")
        field_attr = getattr(self.model_cls, 'name', None)
        if field_attr is None:
            raise ValueError(f"Cannot find by name: {self.model_cls.__name__} does not have a 'name' field.")

        if not isinstance(field_attr, InstrumentedAttribute):
            raise ValueError(
                f"Attribute 'name' on model {self.model_cls.__name__} "
                f"is not a queryable SQLAlchemy mapped attribute. Found type: {type(field_attr)}."
            )

        potential_sql_filter: Any

        if partial_match:
            potential_sql_filter = field_attr.ilike(f'%{name}%')
        else:
            potential_sql_filter = (field_attr == name)

        actual_filter_for_where_clause: ColumnElement[bool]

        if isinstance(potential_sql_filter, bool):
            logging.warning(
                f"Name comparison (partial_match={partial_match}) for {self.model_cls.__name__} "
                f"unexpectedly resulted in a Python boolean ({potential_sql_filter}). "
                f"Converting to SQL true/false."
            )
            actual_filter_for_where_clause = sql_expr.true() if potential_sql_filter else sql_expr.false()
        elif hasattr(potential_sql_filter, 'compile'):
            actual_filter_for_where_clause = cast(ColumnElement[bool], potential_sql_filter)
        else:
            raise TypeError(
                f"Name comparison (partial_match={partial_match}) for {self.model_cls.__name__} "
                f"resulted in an unsupported type: {type(potential_sql_filter)}."
            )

        stmt = select(self.model_cls).where(actual_filter_for_where_clause)

        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()

        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]
        # The list comprehension already filters out None entities implicitly if _convert_to_entity returns None

        logging.debug(f"[FindAllByName] Found {len(entities)} {self.model_cls.__name__} matching name: '{name}'")
        return entities

    async def find_by_field_list(self, field_name: str, values: List[Any]) -> List[EntityType]:
        logging.debug(
            f"[FindByFieldList] Looking for {self.model_cls.__name__} where {field_name} in list of {len(values)} values")
        field_attr = getattr(self.model_cls, field_name, None)
        if field_attr is None:
            raise ValueError(f"Field '{field_name}' does not exist on model {self.model_cls.__name__}.")

        if not isinstance(field_attr, InstrumentedAttribute):
            raise ValueError(
                f"Attribute '{field_name}' on model {self.model_cls.__name__} "
                f"is not a queryable SQLAlchemy mapped attribute. Found type: {type(field_attr)}."
            )

        if not values:
            return []

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

        conditions: List[ColumnElement[bool]] = []  # Ensure conditions are SQLAlchemy expressions
        for field_name, value in field_values.items():
            field_attr = getattr(self.model_cls, field_name, None)
            if field_attr is None:
                raise ValueError(f"Field '{field_name}' does not exist on model {self.model_cls.__name__}.")

            if not isinstance(field_attr, InstrumentedAttribute):
                raise ValueError(
                    f"Attribute '{field_name}' on model {self.model_cls.__name__} "
                    f"is not a queryable SQLAlchemy mapped attribute. Found type: {type(field_attr)}."
                )

            comparison = (field_attr == value)
            if isinstance(comparison, bool):  # Handle unexpected Python bool
                logging.warning(f"Comparison for {field_name} resulted in Python bool. Converting.")
                conditions.append(sql_expr.true() if comparison else sql_expr.false())
            elif hasattr(comparison, 'compile'):
                conditions.append(cast(ColumnElement[bool], comparison))
            else:
                raise TypeError(f"Comparison for {field_name} yielded unsupported type {type(comparison)}")

        if not conditions:  # Should not happen if field_values is not empty, but safeguard
            return []

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
                return 0  # Or select(func.count(literal_column("*"))) if truly no columns

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
            stmt = stmt.order_by(*order_by)  # order_by should be list of ColumnElement/UnaryExpression
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

    async def bulk_save(self, entities: List[EntityType]) -> List[EntityType]:
        if not entities:
            logging.warning("[BulkSave] Received empty entity list")
            return []

        logging.info(f"[BulkSave] Saving {len(entities)} {self.model_cls.__name__} entities")

        pk_attr_name = None
        if self._pk_attr_names:
            pk_attr_name = next(iter(self._pk_attr_names), None)

        if pk_attr_name is None:
            logging.error(f"[BulkSave] Cannot determine primary key for {self.model_cls.__name__}")
            raise ValueError(f"Cannot bulk save: Primary key not defined for model {self.model_cls.__name__}")

        new_entities_data = []  # Store dicts for bulk insert
        existing_entities_to_update = []  # Store entities for individual update

        for entity in entities:
            pk_value = getattr(entity, pk_attr_name, None)
            # Consider new if PK is None OR if the PK is server-default (even if a value is present, it might be a placeholder)
            is_server_default_pk = pk_attr_name in self._pk_server_default_names

            if pk_value is None or is_server_default_pk:
                model_dict = await self._entity_to_model_dict(entity, is_new=True)
                new_entities_data.append(model_dict)
            else:
                # Check if it actually exists in DB before deciding it's an "update"
                # This might be too slow for large bulk operations.
                # Alternative: rely on the PK value solely.
                # For now, let's keep it simpler: if PK exists, assume update via individual save.
                existing_entities_to_update.append(entity)

        logging.debug(
            f"[BulkSave] Processing {len(new_entities_data)} for insert, {len(existing_entities_to_update)} for update/individual save")

        saved_entities_list: List[EntityType] = []

        # Process new entities with bulk insert (if supported and desired)
        # SQLAlchemy 2.0 ORM bulk_insert_mappings doesn't return objects directly in the same way add/flush does.
        # For simplicity and to get refreshed objects, let's add and flush.
        if new_entities_data:
            try:
                db_objs_to_insert = []
                for model_dict in new_entities_data:
                    db_obj = self.model_cls(**model_dict)
                    self.db.add(db_obj)
                    db_objs_to_insert.append(db_obj)

                await self.db.flush()  # Flush to get IDs and defaults

                for db_obj in db_objs_to_insert:
                    await self.db.refresh(db_obj)  # Ensure it's fully populated
                    saved_entity = await self._convert_to_entity(db_obj)
                    if saved_entity:
                        saved_entities_list.append(saved_entity)

                logging.debug(f"[BulkSave] Successfully processed {len(db_objs_to_insert)} new entities via add/flush.")

            except Exception as e:
                logging.error(f"[BulkSave] Error during bulk insert processing: {e}", exc_info=True)
                await self.db.rollback()
                raise

        # Process existing entities individually (this uses the regular save method)
        if existing_entities_to_update:
            try:
                for entity in existing_entities_to_update:
                    # The regular save method handles existing object updates and refresh.
                    saved_entity = await self.save(entity)
                    saved_entities_list.append(saved_entity)

                logging.debug(
                    f"[BulkSave] Successfully saved/updated {len(existing_entities_to_update)} existing entities individually.")

            except Exception as e:
                logging.error(f"[BulkSave] Error during individual updates in bulk operation: {e}", exc_info=True)
                await self.db.rollback()  # Rollback if any individual save fails
                raise

        return saved_entities_list

    async def bulk_delete(self, entity_ids: List[PrimaryKeyType]) -> int:
        """
        Bulk delete entities by their IDs.
        Returns the number of entities deleted.
        """
        if not entity_ids:
            logging.warning("[BulkDelete] Received empty entity ID list")
            return 0

        if not self._pk_attr_names:
            raise ValueError(f"Cannot bulk delete: Primary key not defined for model {self.model_cls.__name__}")

        logging.info(f"[BulkDelete] Deleting {len(entity_ids)} {self.model_cls.__name__} entities")

        pk_attr_name = next(iter(self._pk_attr_names), None)
        if not pk_attr_name:
            raise ValueError(f"Cannot determine primary key for {self.model_cls.__name__}")

        pk_column = getattr(self.model_cls, pk_attr_name, None)
        if pk_column is None:
            raise ValueError(f"Primary key column '{pk_attr_name}' not found on model {self.model_cls.__name__}")

        try:
            # Use SQLAlchemy's delete with WHERE IN clause
            from sqlalchemy import delete
            stmt = delete(self.model_cls).where(pk_column.in_(entity_ids))
            
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