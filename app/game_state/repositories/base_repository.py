# --- START OF FILE app/game_state/repositories/base_repository.py ---

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import class_mapper, attributes
from sqlalchemy.orm.exc import UnmappedColumnError
from sqlalchemy import func # <<< Import func for count
from typing import Generic, Type, TypeVar, List, Optional, Any, Dict
from uuid import UUID
import dataclasses
import logging
import inspect

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
        # ... (your existing __init__ code - looks good) ...
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
            logging.error(f"Failed to determine primary key/column info for {self.model_cls.__name__}: {e}", exc_info=True)


    async def _entity_to_model_dict(self, entity: EntityType, is_new: bool = False) -> Dict[str, Any]:
        # ... (your existing _entity_to_model_dict code - looks good) ...
        if entity is None:
            logging.error("Received None entity for conversion to model dict.")
            raise ValueError("Cannot convert None entity to dict.")

        if dataclasses.is_dataclass(entity):
            entity_data = dataclasses.asdict(entity)
        else:
            try:
                entity_data = vars(entity).copy()
            except TypeError:
                raise TypeError(f"Cannot convert entity of type {type(entity)} to dict.")

        logging.debug(f"[_entity_to_model_dict] Original entity data keys: {list(entity_data.keys())}")

        model_data = {
            key: value for key, value in entity_data.items()
            if key in self._model_column_keys
        }
        logging.debug(f"[_entity_to_model_dict] Filtered model data keys: {list(model_data.keys())}")

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
        # ... (your existing _convert_to_entity code - looks good) ...
        if db_obj is None:
            return None

        mapper = class_mapper(self.model_cls)
        db_data = {}
        for prop in mapper.attrs:
            prop_key = prop.key
            if hasattr(db_obj, prop_key):
                try:
                    value = getattr(db_obj, prop_key, None)
                    db_data[prop_key] = value
                except Exception as e:
                    logging.warning(f"[_convert_to_entity] Error accessing attribute '{prop_key}' on {self.model_cls.__name__}: {e}")
                    db_data[prop_key] = None

        entity_args = db_data.copy()
        constructor_args = {}
        required_entity_fields = set()

        try:
            if dataclasses.is_dataclass(self.entity_cls):
                entity_fields = dataclasses.fields(self.entity_cls)
                constructor_field_names = {f.name for f in entity_fields if f.init}
                required_entity_fields = {f.name for f in entity_fields if f.init and f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING}
                constructor_args = {k: v for k, v in entity_args.items() if k in constructor_field_names}
            else:
                init_sig = inspect.signature(self.entity_cls.__init__)
                init_params = init_sig.parameters
                constructor_field_names = {p for p in init_params if p != 'self'}
                required_entity_fields = {
                    p.name for p in init_params.values()
                    if p.name != 'self' and p.default is inspect.Parameter.empty and p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
                }
                constructor_args = {k: v for k, v in entity_args.items() if k in constructor_field_names}
        except Exception as e:
            logging.error(f"Error inspecting entity class {self.entity_cls.__name__}: {e}", exc_info=True)
            constructor_args = entity_args
            constructor_field_names = set(entity_args.keys())

        missing_required = required_entity_fields - set(constructor_args.keys())
        if missing_required:
             logging.error(f"Cannot instantiate entity {self.entity_cls.__name__}: Missing required fields from DB data: {missing_required}. Available data keys: {list(entity_args.keys())}")
             raise TypeError(f"Missing required data to create entity {self.entity_cls.__name__}: {missing_required}")

        logging.debug(f"[_convert_to_entity] Constructor args for {self.entity_cls.__name__} keys: {list(constructor_args.keys())}")
        try:
            entity = self.entity_cls(**constructor_args)
            return entity
        except TypeError as e:
            logging.error(f"TypeError instantiating entity {self.entity_cls.__name__}. Check constructor arguments vs provided.", exc_info=True)
            logging.error(f"  Provided args keys: {list(constructor_args.keys())}")
            logging.error(f"  Required args (estimated): {required_entity_fields}")
            raise TypeError(f"Failed to instantiate entity {self.entity_cls.__name__} (Mismatched arguments - see logs): {e}") from e
        except Exception as e:
             logging.error(f"Unexpected error during entity instantiation for {self.entity_cls.__name__}", exc_info=True)
             raise

    async def save(self, entity: EntityType) -> EntityType:
        # ... (your existing save code - looks good) ...
        logging.info(f"[Save Method Entry] Received entity: {entity}")
        if entity is None:
            logging.error("[Save Method Entry] Received None entity! Raising error.")
            raise ValueError("Cannot save None entity.")

        pk_value = None
        pk_attr_name = None
        if self._pk_attr_names:
            pk_attr_name = next(iter(self._pk_attr_names))
            pk_value = getattr(entity, pk_attr_name, None)

        existing_db_obj = None
        if pk_value is not None:
            logging.debug(f"[Save] Entity has PK {pk_value}. Checking database existence.")
            existing_db_obj = await self.db.get(self.model_cls, pk_value)
            if existing_db_obj:
                logging.debug(f"[Save] Object with PK {pk_value} found in DB. Proceeding with UPDATE.")
            else:
                logging.debug(f"[Save] Object with PK {pk_value} NOT found in DB. Proceeding with INSERT (using entity's PK).")
        else:
            logging.debug("[Save] Entity has no PK. Proceeding with INSERT (expecting server default PK).")

        is_new_insert = existing_db_obj is None
        logging.info(f"[Save] Entity value JUST BEFORE calling _entity_to_model_dict: {entity}")
        logging.info(f"[Save] Entity type JUST BEFORE calling _entity_to_model_dict: {type(entity)}")

        model_data = await self._entity_to_model_dict(entity, is_new=is_new_insert and pk_attr_name in self._pk_server_default_names)

        if is_new_insert:
            logging.debug("[Save] Performing INSERT.")
            db_obj = self.model_cls(**model_data)
            self.db.add(db_obj)
            merged_db_obj = db_obj
            logging.debug(f"[Save] Added new {self.model_cls.__name__} instance to session (PK likely provided by entity: {pk_value}).")
        else:
            db_obj = existing_db_obj
            logging.debug(f"[Save] Performing UPDATE for PK: {pk_value}.")
            logging.debug(f"[Save] Updating attributes on existing object.")
            for key, value in model_data.items():
                if key not in self._pk_attr_names:
                    try:
                        setattr(db_obj, key, value)
                    except AttributeError:
                        logging.warning(f"[Save] Attribute '{key}' not found on existing DB object during update, skipping.")
            merged_db_obj = db_obj

        try:
            logging.info("[Save] Flushing session...")
            await self.db.flush()
            logging.info(f"[Save] Flush successful. Refreshing object state...")
            await self.db.refresh(merged_db_obj)
            logging.info(f"[Save] Refresh successful.")
        except Exception as e:
            failed_obj_state = {k: getattr(merged_db_obj, k, 'N/A') for k in self._model_column_keys}
            logging.error(f"[Save] Error during flush/refresh. Object State: {failed_obj_state}", exc_info=True)
            raise

        logging.debug(f"[Save] Converting refreshed DB object back to entity...")
        entity_to_return = await self._convert_to_entity(merged_db_obj)
        if entity_to_return is None:
             raise RuntimeError("Failed to convert refreshed DB object back to entity.")

        final_pk_value = getattr(entity_to_return, pk_attr_name, 'N/A') if pk_attr_name else 'N/A'
        logging.info(f"[Save] Entity saved/updated successfully (Final PK: {final_pk_value}).")
        return entity_to_return

    async def find_by_id(self, entity_id: PrimaryKeyType) -> Optional[EntityType]:
        # ... (your existing find_by_id code - looks good) ...
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
        # ... (your existing find_all code - looks good) ...
        logging.debug(f"[FindAll] Fetching {self.model_cls.__name__} entities (skip={skip}, limit={limit})")
        stmt = select(self.model_cls).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        logging.debug(f"[FindAll] Found {len(db_objs)} DB objects. Converting to entities.")
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs]
        return [entity for entity in entities if entity is not None]

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
                 return False
        else:
            logging.warning(f"[Delete] Object not found for deletion with ID: {entity_id}")
            return False

    async def exists(self, entity_id: PrimaryKeyType) -> bool:
        if not self._pk_attr_names:
             raise ValueError(f"Cannot check existence: Primary key not defined for model {self.model_cls.__name__}")
        logging.debug(f"[Exists] Checking existence for {self.model_cls.__name__} with ID: {entity_id}")
        pk_attr_name = next(iter(self._pk_attr_names))
        pk_col = getattr(self.model_cls, pk_attr_name)
        stmt = select(pk_col).where(pk_col == entity_id).limit(1)
        exists_stmt = select(stmt.exists())
        result = await self.db.execute(exists_stmt)
        does_exist = result.scalar_one_or_none()
        logging.debug(f"[Exists] Result for ID {entity_id}: {does_exist}")
        return bool(does_exist)

    async def get_by_field(self, field_name: str, value: Any) -> Optional[EntityType]:
        # ... (your existing get_by_field code - looks good) ...
        field = getattr(self.model_cls, field_name, None)
        if field is None:
            raise ValueError(f"Field '{field_name}' does not exist on model {self.model_cls.__name__}.")
        result = await self.db.execute(select(self.model_cls).where(field == value))
        db_obj = result.scalar_one_or_none()
        return await self._convert_to_entity(db_obj) if db_obj else None

    async def count_all(self, conditions: Optional[List[Any]] = None) -> int:
        """
        Counts all entities in the table, optionally applying filter conditions.
        'conditions' should be a list of SQLAlchemy filter expressions
        (e.g., [self.model_cls.name == "Test", self.model_cls.category == "A"]).
        """
        logging.debug(f"[CountAll] Counting {self.model_cls.__name__} entities.")
        # Use func.count() over the primary key for efficiency if available
        # If no specific PK to count, func.count() on any non-nullable column or '*' (via literal_column) works
        # For simplicity, counting the first primary key column if defined.
        if self._pk_attr_names:
            pk_to_count = getattr(self.model_cls, next(iter(self._pk_attr_names)))
            stmt = select(func.count(pk_to_count))
        else:
            # Fallback if no PK defined (less common for mapped models)
            # This might require a literal column if your DB doesn't like func.count() alone
            # For example, using a literal column: from sqlalchemy import literal_column
            # stmt = select(func.count(literal_column("*")))
            # Or count a known, always present column:
            # For now, assuming there's at least one column; this might need adjustment.
            # A robust fallback might be to count the model class itself if the DB supports it,
            # but func.count on a PK is standard.
            first_column = next(iter(self._model_column_keys), None)
            if first_column:
                 stmt = select(func.count(getattr(self.model_cls, first_column)))
            else: # Highly unlikely to have no columns
                 logging.error(f"Cannot count {self.model_cls.__name__}: no columns found.")
                 return 0


        if conditions:
            stmt = stmt.where(*conditions)

        result = await self.db.execute(stmt)
        count = result.scalar_one_or_none() or 0
        logging.debug(f"[CountAll] Total count: {count}")
        return count

    async def find_all_paginated(
        self,
        skip: int = 0,
        limit: int = 100,
        conditions: Optional[List[Any]] = None, # For filtering
        order_by: Optional[List[Any]] = None   # For sorting, e.g. [self.model_cls.name.asc()]
    ) -> Dict[str, Any]: # Returns a dict matching PaginatedResponse structure
        """
        Retrieves a paginated list of entities and the total count,
        optionally applying filters and ordering.
        """
        logging.debug(
            f"[FindAllPaginated] Fetching {self.model_cls.__name__} "
            f"(skip={skip}, limit={limit}, conditions={conditions is not None}, order_by={order_by is not None})"
        )

        # Query for items
        stmt = select(self.model_cls)
        if conditions:
            stmt = stmt.where(*conditions)
        if order_by:
            stmt = stmt.order_by(*order_by)
        stmt = stmt.offset(skip).limit(limit)

        result_items = await self.db.execute(stmt)
        db_objs = result_items.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs]
        valid_entities = [entity for entity in entities if entity is not None]

        # Get total count matching the conditions (before pagination)
        total_count = await self.count_all(conditions=conditions)

        logging.debug(f"[FindAllPaginated] Found {len(valid_entities)} items for page, total items: {total_count}")
        return {
            "items": valid_entities,
            "total": total_count,
            "limit": limit,
            "skip": skip,
        }

# --- END OF FILE app/game_state/repositories/base_repository.py ---