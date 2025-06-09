# --- START OF FILE app/game_state/services/biome_service.py ---
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, List, Dict, Any
import logging

# Import Repository, Manager and Domain Entity
from app.game_state.repositories.biome_repository import BiomeRepository
from app.game_state.managers.biome_manager import BiomeManager
from app.game_state.entities.geography.biome_pydantic import BiomeEntityPydantic

# Import API schemas
from app.api.schemas.shared import PaginatedResponse
from app.api.schemas.biome_schema import BiomeRead, BiomeCreate, BiomeUpdate

class BiomeService:
    """
    Service for managing biomes.
    Handles the connection between API routes, domain logic, and data access.
    """
    
    def __init__(self, db: AsyncSession):
        """Initializes the BiomeService with a database session."""
        self.db = db
        self.repository = BiomeRepository(db=self.db)
        self.manager = BiomeManager()
        logging.debug("BiomeService initialized with BiomeRepository and BiomeManager.")

    async def get_all_biomes_paginated(self, skip: int, limit: int) -> PaginatedResponse[BiomeRead]:
        """
        Retrieves a paginated list of biomes.
        
        Args:
            skip: Number of items to skip (for pagination)
            limit: Maximum number of items to return
            
        Returns:
            A paginated response with BiomeRead schemas
        """
        # Call the repository's paginated find method
        paginated_repo_result = await self.repository.find_all_paginated(
            skip=skip,
            limit=limit,
            order_by=[self.repository.model_cls.name.asc()]
        )
        
        # Convert domain entities in "items" to read schemas
        read_schema_items = [BiomeRead.model_validate(biome.model_dump()) for biome in paginated_repo_result["items"]]

        # Construct and return the PaginatedResponse Pydantic model
        return PaginatedResponse[BiomeRead](
            items=read_schema_items,
            total=paginated_repo_result["total"],
            limit=paginated_repo_result["limit"],
            skip=paginated_repo_result["skip"],
        )
    
    async def get_biome_by_id(self, biome_uuid: UUID) -> Optional[BiomeRead]:
        """
        Get a biome by UUID and return as API schema.
        
        Args:
            biome_uuid: The UUID of the biome to retrieve
            
        Returns:
            BiomeRead schema or None if not found
        """
        logging.debug(f"[BiomeService] Getting biome by UUID: {biome_uuid}")
        try:
            entity = await self.repository.find_by_id(biome_uuid)
            if entity:
                return BiomeRead.model_validate(entity.to_dict())
            else:
                return None
        except Exception as e:
            logging.error(f"[BiomeService] Error getting biome by UUID {biome_uuid}: {e}")
            return None

    async def exists(self, biome_uuid: UUID) -> bool:
        """
        Check if a biome exists by UUID.
        
        Args:
            biome_uuid: The UUID to check
            
        Returns:
            True if the biome exists, False otherwise
        """
        logging.debug(f"[BiomeService] Checking existence for biome UUID: {biome_uuid}")
        try:
            return await self.repository.exists(biome_uuid)
        except Exception as e:
            logging.error(f"[BiomeService] Error checking existence for biome {biome_uuid}: {e}", exc_info=True)
            return False
    
    async def get_biome_entity(self, biome_uuid: UUID) -> Optional[BiomeEntityPydantic]:
        """
        Get a biome domain entity by UUID.
        
        Args:
            biome_uuid: The UUID of the biome to retrieve
            
        Returns:
            BiomeEntityPydantic instance or None if not found
        """
        logging.debug(f"[BiomeService] Getting biome entity by UUID: {biome_uuid}")
        try:
            return await self.repository.find_by_id(biome_uuid)
        except Exception as e:
            logging.error(f"[BiomeService] Error getting biome entity by UUID {biome_uuid}: {e}", exc_info=True)
            return None
    
    async def create_biome(self, biome_data: BiomeCreate) -> Optional[BiomeRead]:
        """
        Creates a new biome from API data.
        
        Args:
            biome_data: BiomeCreate schema with the biome data
            
        Returns:
            BiomeRead schema for the created biome or raises an error
        """
        logging.info(f"[BiomeService] Creating biome with string ID: '{biome_data.biome_id}'")
        
        # Database unique constraint will handle duplicate biome_id prevention
        
        # Create transient entity using manager
        try:
            # Convert Pydantic model to dict for unpacking
            create_data_dict = biome_data.model_dump(exclude={"id"})
            
            # Use manager to create entity
            entity_id = biome_data.id if hasattr(biome_data, "id") and biome_data.id else None
            biome_entity = self.manager.create_transient_biome(
                entity_id=entity_id,
                **create_data_dict
            )
            
            logging.debug(f"[BiomeService] Created transient biome entity: {biome_entity}")
        except Exception as e:
            logging.error(f"[BiomeService] Error creating transient biome entity: {e}", exc_info=True)
            raise ValueError(f"Could not create biome: {e}")
        
        # Save using repository
        try:
            saved_entity = await self.repository.save(biome_entity)
            await self.db.commit()
            logging.info(f"[BiomeService] Biome '{saved_entity.name}' created successfully with UUID: {saved_entity.entity_id}")
            
            # Convert to API schema
            return BiomeRead.model_validate(saved_entity.to_dict())
        except Exception as e:
            logging.exception(f"[BiomeService] Error saving new biome '{biome_data.name}': {e}")
            raise
    
    async def update_biome(self, biome_uuid: UUID, update_data: BiomeUpdate) -> Optional[BiomeRead]:
        """
        Updates an existing biome.
        
        Args:
            biome_uuid: UUID of the biome to update
            update_data: BiomeUpdate schema with fields to update
            
        Returns:
            Updated BiomeRead schema or None if biome not found
        """
        logging.info(f"[BiomeService] Updating biome with UUID: {biome_uuid}")
        
        # Use centralized update method from base repository
        try:
            updated_entity = await self.repository.update_entity(biome_uuid, update_data)
            if updated_entity:
                await self.db.commit()
                logging.info(f"[BiomeService] Biome {biome_uuid} updated successfully")
                return BiomeRead.model_validate(updated_entity.to_dict())
            else:
                logging.warning(f"[BiomeService] Biome with UUID {biome_uuid} not found for update.")
                return None
        except Exception as e:
            logging.error(f"[BiomeService] Error updating biome {biome_uuid}: {e}", exc_info=True)
            raise
    
    async def delete_biome(self, biome_uuid: UUID) -> bool:
        """
        Deletes a biome by UUID.
        
        Args:
            biome_uuid: UUID of the biome to delete
            
        Returns:
            True if the biome was deleted, False otherwise
        """
        logging.info(f"[BiomeService] Deleting biome with UUID: {biome_uuid}")
        
        # Check if biome exists
        if not await self.repository.exists(biome_uuid):
            logging.warning(f"[BiomeService] Biome with UUID {biome_uuid} not found for deletion.")
            return False
        
        # Delete using repository
        try:
            result = await self.repository.delete(biome_uuid)
            if result:
                logging.info(f"[BiomeService] Biome {biome_uuid} deleted successfully")
            else:
                logging.warning(f"[BiomeService] Failed to delete biome {biome_uuid}")
            return result
        except Exception as e:
            logging.error(f"[BiomeService] Error deleting biome {biome_uuid}: {e}", exc_info=True)
            return False

    async def bulk_import_biomes(
            self,
            biomes_data: List[Dict[str, Any]],
            skip_existing: bool = True
    ) -> Dict[str, int]:
        """
        Bulk import biomes from raw data (for scripts/migrations).

        Args:
            biomes_data: List of dictionaries with biome data
            skip_existing: Whether to skip biomes that already exist

        Returns:
            Dictionary with import statistics
        """
        logging.info(f"🚀 Starting bulk import of {len(biomes_data)} biomes...")

        imported_count = 0
        skipped_count = 0
        failed_count = 0
        failed_biomes = []
        biome_id = None

        try:
            for biome_data in biomes_data:
                try:
                    biome_id = biome_data["biome_id"]

                    # Note: Database unique constraint will handle duplicate prevention
                    # If skip_existing is True, we'll catch constraint violations below

                    # Create biome entity using manager
                    biome_entity = self.manager.create_transient_biome(
                        biome_id=biome_data["biome_id"],
                        name=biome_data["name"],
                        display_name=biome_data["display_name"],
                        description=biome_data.get("description"),
                        base_movement_modifier=biome_data.get("base_movement_modifier", 1.0),
                        danger_level_base=biome_data.get("danger_level_base", 1),
                        resource_types=biome_data.get("resource_types", {}),
                        color_hex=biome_data.get("color_hex"),
                        icon_path=biome_data.get("icon_path")
                    )

                    # Save (flush only - we'll commit at the end)
                    saved_biome = await self.repository.save(biome_entity)
                    logging.info(f"✅ Prepared biome: {saved_biome.name} (ID: {saved_biome.entity_id})")
                    imported_count += 1

                except Exception as e:
                    # Check if it's a unique constraint violation (duplicate biome_id)
                    if "unique constraint" in str(e).lower() or "duplicate" in str(e).lower():
                        if skip_existing:
                            logging.info(f"⏭️  Biome '{biome_id}' already exists. Skipping.")
                            skipped_count += 1
                            continue
                        else:
                            logging.error(f"❌ Biome '{biome_id}' already exists and skip_existing=False")
                            failed_biomes.append({
                                'name': biome_data.get('name', 'unknown'),
                                'biome_id': biome_data.get('biome_id', 'unknown'),
                                'error': f"Biome ID '{biome_id}' already exists"
                            })
                            failed_count += 1
                            continue
                    else:
                        logging.error(f"❌ Failed to process biome '{biome_data.get('name', 'unknown')}': {e}")
                        failed_biomes.append({
                            'name': biome_data.get('name', 'unknown'),
                            'biome_id': biome_data.get('biome_id', 'unknown'),
                            'error': str(e)
                        })
                        failed_count += 1
                        continue

            # Commit all changes at once (THIS IS THE KEY PART!)
            if imported_count > 0:
                logging.info(f"💾 Committing transaction with {imported_count} new biomes...")
                await self.db.commit()
                logging.info(f"🎉 Bulk import committed successfully!")
            else:
                logging.info("ℹ️  No new biomes to commit.")

            # Return summary
            summary = {
                'imported': imported_count,
                'skipped': skipped_count,
                'failed': failed_count,
                'total_processed': len(biomes_data)
            }

            if failed_biomes:
                logging.warning(f"⚠️  {failed_count} biomes failed to import: {failed_biomes}")

            logging.info(f"📊 Import Summary: {summary}")
            return summary

        except Exception as e:
            logging.error(f"❌ Bulk import transaction failed: {e}")
            await self.db.rollback()
            raise

    async def get_biomes_by_danger_level(self, danger_level: int) -> List[BiomeRead]:
        """
        Gets all biomes with a specific danger level.
        
        Args:
            danger_level: The danger level to filter by (1-5)
            
        Returns:
            List of biomes matching the danger level
        """
        logging.debug(f"[BiomeService] Getting biomes with danger level: {danger_level}")
        try:
            # Use repository to find biomes
            entities = await self.repository.find_by_danger_level(danger_level)
            
            # Convert to API schemas
            read_schemas = []
            for entity in entities:
                schema = BiomeRead.model_validate(entity.to_dict())
                if schema:
                    read_schemas.append(schema)
            
            return read_schemas
        except Exception as e:
            logging.error(f"[BiomeService] Error getting biomes by danger level {danger_level}: {e}", exc_info=True)
            return []
    
    async def get_biomes_by_movement_range(self, min_modifier: float, max_modifier: float) -> List[BiomeRead]:
        """
        Gets biomes within a specific movement modifier range.
        
        Args:
            min_modifier: Minimum movement modifier
            max_modifier: Maximum movement modifier
            
        Returns:
            List of biomes within the movement modifier range
        """
        logging.debug(f"[BiomeService] Getting biomes with movement modifier between {min_modifier} and {max_modifier}")
        try:
            # Use repository to find biomes
            entities = await self.repository.find_by_movement_modifier(min_modifier, max_modifier)
            
            # Convert to API schemas
            read_schemas = []
            for entity in entities:
                schema = BiomeRead.model_validate(entity.to_dict())
                if schema:
                    read_schemas.append(schema)
            
            return read_schemas
        except Exception as e:
            logging.error(f"[BiomeService] Error getting biomes by movement range: {e}", exc_info=True)
            return []

# --- END OF FILE app/game_state/services/biome_service.py ---