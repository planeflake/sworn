# START OF FILE app/game_state/repositories/base_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import class_mapper, attributes # Import attributes
from sqlalchemy.orm.exc import UnmappedColumnError # Import for check
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
        """Initializes the BaseRepository."""
        if not hasattr(model_cls, '__table__') and not inspect.isclass(model_cls):
            raise ValueError(f"{model_cls.__name__} does not appear to be a SQLAlchemy model class.")
        if not inspect.isclass(entity_cls):
             raise ValueError(f"entity_cls '{entity_cls}' must be a class.")

        self.db = db
        self.model_cls = model_cls
        self.entity_cls = entity_cls

        # Pre-calculate PK names and which ones use server_default
        self._pk_attr_names = set()
        self._pk_server_default_names = set()
        self._model_column_keys = set()
        try:
            mapper = class_mapper(self.model_cls)
            self._model_column_keys = {prop.key for prop in mapper.column_attrs} # Only column keys
            for col in mapper.primary_key:
                self._pk_attr_names.add(col.key)
                if col.server_default is not None:
                    self._pk_server_default_names.add(col.key)
            if not self._pk_attr_names:
                 logging.warning(f"No primary key columns found for model {self.model_cls.__name__}.")
        except Exception as e:
            logging.error(f"Failed to determine primary key/column info for {self.model_cls.__name__}: {e}", exc_info=True)
            # Handle case where inspection fails

    async def _entity_to_model_dict(self, entity: EntityType, is_new: bool = False) -> Dict[str, Any]:
        """
        Converts domain entity to a dictionary suitable for SQLAlchemy model instantiation or update.
        Filters keys to match model columns.
        Removes server-defaulted PKs for new entities.
        """
        if entity is None:
            logging.error("Received None entity for conversion to model dict.")
            raise ValueError("Cannot convert None entity to dict.")

        # 1. Get data from the entity
        if dataclasses.is_dataclass(entity):
            entity_data = dataclasses.asdict(entity)
        # elif isinstance(entity, pydantic.BaseModel): # Add if needed
        #     entity_data = entity.model_dump()
        else:
            try:
                entity_data = vars(entity).copy()
            except TypeError:
                raise TypeError(f"Cannot convert entity of type {type(entity)} to dict.")

        logging.debug(f"[_entity_to_model_dict] Original entity data keys: {list(entity_data.keys())}")

        # 2. Filter data to include only keys that are actual columns in the model
        model_data = {
            key: value for key, value in entity_data.items()
            if key in self._model_column_keys # Ensure key corresponds to a mapped column
        }
        logging.debug(f"[_entity_to_model_dict] Filtered model data keys: {list(model_data.keys())}")


        # 3. If it's a new entity being inserted, remove any PK fields that rely on server_default
        #    This prevents overriding the database generation mechanism.
        if is_new:
            keys_to_remove = set()
            for pk_name in self._pk_server_default_names:
                if pk_name in model_data:
                    keys_to_remove.add(pk_name)
                    # Optional: Check if the value was None anyway? If it had a value, log a warning?
                    # if model_data[pk_name] is not None:
                    #    logging.warning(f"[_entity_to_model_dict] Entity provided value for server-default PK '{pk_name}' during insert. Ignoring entity value.")

            if keys_to_remove:
                 logging.debug(f"[_entity_to_model_dict] Removing server-default PKs for insert: {keys_to_remove}")
                 for key in keys_to_remove:
                     model_data.pop(key, None)

        logging.debug(f"[_entity_to_model_dict] Final model dict keys for SQLAlchemy: {list(model_data.keys())}")
        return model_data

    # _convert_to_entity remains largely the same as the previous version
    # Make sure it correctly extracts data from db_obj and populates the entity_cls
    async def _convert_to_entity(self, db_obj: ModelType) -> Optional[EntityType]:
        """Converts a DB model instance to a domain entity instance."""
        if db_obj is None:
            return None

        mapper = class_mapper(self.model_cls)
        db_data = {}
        # Iterate through all mapped properties (columns, relationships, etc.)
        # Use mapper.attrs to get all properties keys (includes columns, relationships)
        for prop in mapper.attrs:
            prop_key = prop.key # The Python attribute name
            if hasattr(db_obj, prop_key):
                try:
                    # Use getattr_static for potentially unloaded relationships? Or just simple getattr.
                    # Be cautious with relationships - might trigger lazy loading.
                    # Only include if entity expects it.
                    value = getattr(db_obj, prop_key, None)
                    db_data[prop_key] = value
                except Exception as e:
                    logging.warning(f"[_convert_to_entity] Error accessing attribute '{prop_key}' on {self.model_cls.__name__}: {e}")
                    db_data[prop_key] = None
            # else: log missing attribute if needed

        # Prepare arguments for the domain entity's constructor
        entity_args = db_data.copy()

        # Filter arguments based on the entity's constructor (__init__ or dataclass fields)
        constructor_args = {}
        required_entity_fields = set() # Store fields the entity constructor *needs*

        try:
            if dataclasses.is_dataclass(self.entity_cls):
                entity_fields = dataclasses.fields(self.entity_cls)
                constructor_field_names = {f.name for f in entity_fields if f.init}
                required_entity_fields = {f.name for f in entity_fields if f.init and f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING}
                constructor_args = {k: v for k, v in entity_args.items() if k in constructor_field_names}

            # Add Pydantic V2 handling if needed
            # elif hasattr(self.entity_cls, 'model_fields'): # Pydantic v2 check
            #     # ... similar logic ...
            else: # Fallback for regular classes
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
            constructor_args = entity_args # Fallback, less safe
            constructor_field_names = set(entity_args.keys()) # Estimate

        # Check if all required fields are present
        missing_required = required_entity_fields - set(constructor_args.keys())
        if missing_required:
             logging.error(f"Cannot instantiate entity {self.entity_cls.__name__}: Missing required fields from DB data: {missing_required}. Available data keys: {list(entity_args.keys())}")
             # Decide whether to raise or return None
             raise TypeError(f"Missing required data to create entity {self.entity_cls.__name__}: {missing_required}")
             # return None

        # logging.debug(f"[_convert_to_entity] DB data extracted keys: {list(db_data.keys())}")
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


# START OF FILE app/game_state/repositories/base_repository.py
# (Keep imports, __init__, _entity_to_model_dict, _convert_to_entity, find_by_id, find_all, delete, exists as they were)
# Only replace the save method below

    async def save(self, entity: EntityType) -> EntityType:
        """
        Saves (inserts or updates) a domain entity to the database.
        Correctly handles entities with client-side generated PKs by checking DB existence first.
        """
        logging.info(f"[Save Method Entry] Received entity: {entity}")
        if entity is None:
            logging.error("[Save Method Entry] Received None entity! Raising error.")
            raise ValueError("Cannot save None entity.")
        if entity is None:
            raise ValueError("Cannot save None entity.")

        # Get the primary key value and name from the entity
        pk_value = None
        pk_attr_name = None
        if self._pk_attr_names:
            # Assuming single PK for simplicity
            pk_attr_name = next(iter(self._pk_attr_names))
            pk_value = getattr(entity, pk_attr_name, None)

        existing_db_obj = None
        if pk_value is not None:
            # If entity has a PK, check if it actually exists in the DB
            logging.debug(f"[Save] Entity has PK {pk_value}. Checking database existence.")
            existing_db_obj = await self.db.get(self.model_cls, pk_value)
            if existing_db_obj:
                logging.debug(f"[Save] Object with PK {pk_value} found in DB. Proceeding with UPDATE.")
            else:
                logging.debug(f"[Save] Object with PK {pk_value} NOT found in DB. Proceeding with INSERT (using entity's PK).")
        else:
            # If entity has no PK, it's definitely new
            logging.debug("[Save] Entity has no PK. Proceeding with INSERT (expecting server default PK).")

        # Determine if we are truly inserting a new record or updating an existing one
        is_new_insert = existing_db_obj is None

        logging.info(f"[Save] Entity value JUST BEFORE calling _entity_to_model_dict: {entity}")
        # Check type as well
        logging.info(f"[Save] Entity type JUST BEFORE calling _entity_to_model_dict: {type(entity)}")

        # Convert entity to dict.
        # For new inserts, remove server-defaulted PKs.
        # For updates OR inserts with client-provided PK, keep the PK in the dict.
        model_data = await self._entity_to_model_dict(entity, is_new=is_new_insert and pk_attr_name in self._pk_server_default_names)

        if is_new_insert:
            # --- Insert Logic ---
            logging.debug("[Save] Performing INSERT.")
            # Create a new model instance using the prepared dict
            # This dict will contain the client-generated PK if it wasn't server-defaulted
            db_obj = self.model_cls(**model_data)
            self.db.add(db_obj)
            merged_db_obj = db_obj # The object added is the one we'll refresh
            logging.debug(f"[Save] Added new {self.model_cls.__name__} instance to session (PK likely provided by entity: {pk_value}).")
        else:
            # --- Update Logic ---
            # We already fetched existing_db_obj
            db_obj = existing_db_obj
            logging.debug(f"[Save] Performing UPDATE for PK: {pk_value}.")
            logging.debug(f"[Save] Updating attributes on existing object.")
            # Update the existing object's attributes from the model_data dict
            for key, value in model_data.items():
                # Skip setting the PK again during update
                if key not in self._pk_attr_names:
                    try:
                        current_value = getattr(db_obj, key, None)
                        # Optional: only set if value changed
                        # if current_value != value:
                        #     setattr(db_obj, key, value)
                        setattr(db_obj, key, value)
                    except AttributeError:
                        logging.warning(f"[Save] Attribute '{key}' not found on existing DB object during update, skipping.")

            merged_db_obj = db_obj # The updated object is the one we'll refresh

        # --- Flush and Refresh ---
        try:
            logging.info("[Save] Flushing session...")
            await self.db.flush() # Persist changes (INSERT or UPDATE)
            logging.info(f"[Save] Flush successful. Refreshing object state...")
            # Refresh the object to get any DB-generated values (like timestamps, or the ID if it *was* server-defaulted)
            await self.db.refresh(merged_db_obj)
            logging.info(f"[Save] Refresh successful.")
        except Exception as e:
            # Log the specific object state if flush fails
            failed_obj_state = {k: getattr(merged_db_obj, k, 'N/A') for k in self._model_column_keys}
            logging.error(f"[Save] Error during flush/refresh. Object State: {failed_obj_state}", exc_info=True)
            raise # Re-raise the exception

        # --- Convert back to Entity ---
        logging.debug(f"[Save] Converting refreshed DB object back to entity...")
        entity_to_return = await self._convert_to_entity(merged_db_obj)
        if entity_to_return is None:
             # This could happen if _convert_to_entity fails
             raise RuntimeError("Failed to convert refreshed DB object back to entity.")

        final_pk_value = getattr(entity_to_return, pk_attr_name, 'N/A') if pk_attr_name else 'N/A'
        logging.info(f"[Save] Entity saved/updated successfully (Final PK: {final_pk_value}).")
        return entity_to_return


    async def find_by_id(self, entity_id: PrimaryKeyType) -> Optional[EntityType]:
        """Finds an entity by its primary key using db.get()."""
        if not self._pk_attr_names:
             raise ValueError(f"Cannot find_by_id: Primary key not defined for model {self.model_cls.__name__}")
        # Add check/handling for composite keys if entity_id is not a single value matching len(self._pk_attr_names)

        logging.debug(f"[FindByID] Looking for {self.model_cls.__name__} with ID: {entity_id}")
        db_obj = await self.db.get(self.model_cls, entity_id) # db.get handles single/tuple PKs

        if db_obj:
            logging.debug(f"[FindByID] Found object in session/DB. Converting to entity.")
            return await self._convert_to_entity(db_obj)
        else:
            logging.debug(f"[FindByID] Object not found for ID: {entity_id}")
            return None

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[EntityType]:
        """Retrieves a list of entities with pagination."""
        logging.debug(f"[FindAll] Fetching {self.model_cls.__name__} entities (skip={skip}, limit={limit})")
        stmt = select(self.model_cls).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        logging.debug(f"[FindAll] Found {len(db_objs)} DB objects. Converting to entities.")
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs]
        return [entity for entity in entities if entity is not None]


    async def delete(self, entity_id: PrimaryKeyType) -> bool:
        """Deletes an entity by its primary key."""
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
                 return False # Indicate delete failed
        else:
            logging.warning(f"[Delete] Object not found for deletion with ID: {entity_id}")
            return False

    async def exists(self, entity_id: PrimaryKeyType) -> bool:
        """Checks if an entity exists by its primary key using a lightweight query."""
        if not self._pk_attr_names:
             raise ValueError(f"Cannot check existence: Primary key not defined for model {self.model_cls.__name__}")

        logging.debug(f"[Exists] Checking existence for {self.model_cls.__name__} with ID: {entity_id}")
        pk_attr_name = next(iter(self._pk_attr_names)) # Assuming single PK
        pk_col = getattr(self.model_cls, pk_attr_name)

        stmt = select(pk_col).where(pk_col == entity_id).limit(1)
        exists_stmt = select(stmt.exists())

        result = await self.db.execute(exists_stmt)
        does_exist = result.scalar_one_or_none()
        logging.debug(f"[Exists] Result for ID {entity_id}: {does_exist}")
        return bool(does_exist)


# END OF FILE app/game_state/repositories/base_repository.py