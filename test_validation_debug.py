#!/usr/bin/env python3
"""
Isolated test for validation function debugging
"""
import asyncio
import sys
import os
from uuid import UUID

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.async_session import DATABASE_URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.game_state.services.core.validation.service_validaton_utils import ServiceValidationUtils


async def test_validation_direct():
    """Test the validation function directly"""
    
    # Known good IDs from the database
    theme_id = UUID("b2494b91-f7d1-4c8d-9da2-c628816ed9de")  # Fantasy Medieval
    world_id = UUID("f467f954-9762-4361-8893-6df42b9d9d7e")  # Seed World
    location_type_id = UUID("f1df65be-0db7-40d9-952f-3f8ff3b803c1")  # Settlement
    location_sub_type_id = UUID("46b1a1d8-d88f-4386-8c05-dbd565236fe4")  # Village
    
    # Create database session
    engine = create_async_engine(DATABASE_URL)
    
    async with AsyncSession(engine) as session:
        # Create validation utility
        validator = ServiceValidationUtils(session)
        
        print("Testing validation function directly...")
        
        # Test each entity individually
        test_cases = [
            (theme_id, "theme", "Theme"),
            (world_id, "world", "World"),
            (location_type_id, "location_type", "Location Type"),
            (location_sub_type_id, "location_sub_type", "Location Sub Type")
        ]
        
        for entity_id, service_name, entity_name in test_cases:
            print(f"\n--- Testing {entity_name} ({service_name}) ---")
            print(f"ID: {entity_id}")
            
            try:
                # Test the direct check method
                exists = await validator._check_entity_exists_direct(entity_id, service_name)
                print(f"Direct check result: {exists}")
                
                # Test the full validation method
                await validator.validate_entity_exists(entity_id, service_name, entity_name)
                print(f"Full validation: PASSED")
                
            except Exception as e:
                print(f"Validation failed: {e}")
                print(f"Error type: {type(e).__name__}")
    
    await engine.dispose()


async def test_model_imports():
    """Test if we can import the model classes correctly"""
    print("\n=== Testing Model Imports ===")
    
    model_mapping = {
        'theme': 'app.db.models.theme.ThemeDB',
        'world': 'app.db.models.world.World', 
        'location_type': 'app.db.models.location_type.LocationType',
        'location_sub_type': 'app.db.models.location_sub_type.LocationSubType',
    }
    
    for service_name, model_path in model_mapping.items():
        try:
            print(f"\nTesting import for {service_name}: {model_path}")
            
            module_path, class_name = model_path.rsplit('.', 1)
            import importlib
            module = importlib.import_module(module_path)
            model_class = getattr(module, class_name)
            
            print(f"✓ Successfully imported {class_name}")
            print(f"  Table name: {getattr(model_class, '__tablename__', 'Not found')}")
            print(f"  Has id field: {hasattr(model_class, 'id')}")
            
        except Exception as e:
            print(f"✗ Failed to import {model_path}: {e}")


async def test_raw_db_query():
    """Test raw database queries to verify data exists"""
    print("\n=== Testing Raw Database Queries ===")
    
    engine = create_async_engine(DATABASE_URL)
    
    async with AsyncSession(engine) as session:
        # Test raw queries for each table
        test_queries = [
            ("themes", "b2494b91-f7d1-4c8d-9da2-c628816ed9de"),
            ("worlds", "f467f954-9762-4361-8893-6df42b9d9d7e"),
            ("location_types", "f1df65be-0db7-40d9-952f-3f8ff3b803c1"),
            ("location_sub_types", "46b1a1d8-d88f-4386-8c05-dbd565236fe4"),
        ]
        
        from sqlalchemy import text
        
        for table_name, test_id in test_queries:
            try:
                print(f"\nTesting table: {table_name}")
                
                # Count total records
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                result = await session.execute(count_query)
                total_count = result.scalar()
                print(f"  Total records: {total_count}")
                
                # Check if specific ID exists
                exists_query = text(f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE id = :test_id)")
                result = await session.execute(exists_query, {"test_id": test_id})
                exists = result.scalar()
                print(f"  ID {test_id} exists: {exists}")
                
                if not exists:
                    # Show a few sample IDs
                    sample_query = text(f"SELECT id FROM {table_name} LIMIT 3")
                    result = await session.execute(sample_query)
                    sample_ids = [str(row[0]) for row in result.fetchall()]
                    print(f"  Sample IDs: {sample_ids}")
                
            except Exception as e:
                print(f"  Error querying {table_name}: {e}")
    
    await engine.dispose()


async def main():
    """Run all tests"""
    print("=== VALIDATION DEBUG TESTS ===")
    
    try:
        await test_model_imports()
        await test_raw_db_query()
        await test_validation_direct()
        
    except Exception as e:
        print(f"\nFatal error in tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())