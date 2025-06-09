#!/usr/bin/env python3
"""
Utility script to import biome data from JSON file into the database.
This script can be run directly or imported as a module.

IMPORTANT: Run this script AFTER running migrations with 'alembic upgrade head'.
The migration creates the biomes table structure but doesn't populate it,
to avoid issues with UUID generation in migrations.

Usage:
    python utils/import_biomes.py
"""

import asyncio
import json
import logging
import os
import sys
from typing import List, Dict, Any, Optional
import uuid

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.async_session import get_db_session
from app.game_state.managers.biome_manager import BiomeManager
from app.game_state.repositories.biome_repository import BiomeRepository

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to biomes data file
BIOMES_DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "09_biomes.json")

async def import_biomes() -> None:
    """
    Import biomes from the data file into the database.
    """
    logger.info("Starting biome import...")
    
    # Read biomes data from JSON file
    try:
        with open(BIOMES_DATA_FILE, 'r') as f:
            biomes_data = json.load(f)
        logger.info(f"Loaded {len(biomes_data)} biomes from {BIOMES_DATA_FILE}")
    except FileNotFoundError:
        logger.error(f"Biomes data file not found at {BIOMES_DATA_FILE}")
        return
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in biomes data file at {BIOMES_DATA_FILE}")
        return
    
    # Create DB session
    async with get_db_session() as session:
        # Create repository
        repository = BiomeRepository(db=session)
        manager = BiomeManager()
        
        # Import each biome
        for biome_data in biomes_data:
            try:
                # Check if biome already exists with this biome_id
                existing_biome = await repository.find_by_biome_id(biome_data["biome_id"])
                
                if existing_biome:
                    logger.info(f"Biome with ID '{biome_data['biome_id']}' already exists. Skipping.")
                    continue
                
                # Create a new biome entity
                biome_entity = manager.create_transient_biome(
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
                
                # Save the biome to the database
                saved_biome = await repository.save(biome_entity)
                await session.commit()
                logger.info(f"Imported biome: {saved_biome.name} (ID: {saved_biome.entity_id})")
                
            except Exception as e:
                logger.error(f"Error importing biome '{biome_data.get('name', 'unknown')}': {str(e)}")
    
    logger.info("Biome import completed")

def run_import():
    """Run the import as a standalone script."""
    asyncio.run(import_biomes())

if __name__ == "__main__":
    run_import()