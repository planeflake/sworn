#!/usr/bin/env python3
"""
Incremental debug tests - add one step at a time until we find the issue
"""
import asyncio
import sys
import os
from uuid import UUID

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.async_session import DATABASE_URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


async def test_step_1_direct_validation():
    """Step 1: Direct validation utility (we know this works)"""
    print("=== STEP 1: Direct Validation Utility ===")
    
    from app.game_state.services.core.validation.service_validaton_utils import ServiceValidationUtils
    
    theme_id = UUID("b2494b91-f7d1-4c8d-9da2-c628816ed9de")
    world_id = UUID("f467f954-9762-4361-8893-6df42b9d9d7e")
    
    engine = create_async_engine(DATABASE_URL)
    async with AsyncSession(engine) as session:
        validator = ServiceValidationUtils(session)
        
        try:
            await validator.validate_entity_exists(theme_id, "theme", "Theme")
            await validator.validate_entity_exists(world_id, "world", "World")
            print("✓ Step 1 PASSED: Direct validation works")
            return True
        except Exception as e:
            print(f"✗ Step 1 FAILED: {e}")
            return False
        finally:
            await engine.dispose()


async def test_step_2_base_service_validator():
    """Step 2: BaseService with validator (like in API)"""
    print("\n=== STEP 2: BaseService with Validator ===")
    
    from app.game_state.services.core.base_service import BaseService
    from app.game_state.repositories.location.location_repository import LocationRepository
    from app.game_state.entities.geography.location_pydantic import LocationEntityPydantic
    from app.api.schemas.location.location_schema import LocationResponse
    
    theme_id = UUID("b2494b91-f7d1-4c8d-9da2-c628816ed9de")
    world_id = UUID("f467f954-9762-4361-8893-6df42b9d9d7e")
    
    engine = create_async_engine(DATABASE_URL)
    async with AsyncSession(engine) as session:
        # Create a BaseService instance similar to how LocationService does
        repository = LocationRepository(session)
        base_service = BaseService(
            db=session,
            repository=repository,
            entity_class=LocationEntityPydantic,
            response_class=LocationResponse
        )
        
        try:
            # Test the validator directly (same as in BaseService)
            await base_service.validator.validate_entity_exists(theme_id, "theme", "Theme")
            await base_service.validator.validate_entity_exists(world_id, "world", "World")
            print("✓ Step 2 PASSED: BaseService validator works")
            return True
        except Exception as e:
            print(f"✗ Step 2 FAILED: {e}")
            return False
        finally:
            await engine.dispose()


async def test_step_3_validate_foreign_keys():
    """Step 3: Use the validate_foreign_keys method like the API does"""
    print("\n=== STEP 3: validate_foreign_keys Method ===")
    
    from app.game_state.services.core.base_service import BaseService
    from app.game_state.repositories.location.location_repository import LocationRepository
    from app.game_state.entities.geography.location_pydantic import LocationEntityPydantic
    from app.api.schemas.location.location_schema import LocationResponse
    
    theme_id = UUID("b2494b91-f7d1-4c8d-9da2-c628816ed9de")
    world_id = UUID("f467f954-9762-4361-8893-6df42b9d9d7e")
    location_type_id = UUID("f1df65be-0db7-40d9-952f-3f8ff3b803c1")
    
    # Create test data like the API does
    test_data = {
        "name": "Test Location",
        "theme_id": theme_id,
        "world_id": world_id,
        "location_type_id": location_type_id
    }
    
    engine = create_async_engine(DATABASE_URL)
    async with AsyncSession(engine) as session:
        repository = LocationRepository(session)
        base_service = BaseService(
            db=session,
            repository=repository,
            entity_class=LocationEntityPydantic,
            response_class=LocationResponse
        )
        
        try:
            # Test the validate_foreign_keys method directly
            validations = {
                "theme_id": ("theme", "Theme"),
                "world_id": ("world", "World"),
                "location_type_id": ("location_type", "Location Type")
            }
            await base_service.validator.validate_foreign_keys(test_data, validations)
            print("✓ Step 3 PASSED: validate_foreign_keys works")
            return True
        except Exception as e:
            print(f"✗ Step 3 FAILED: {e}")
            return False
        finally:
            await engine.dispose()


async def test_step_4_location_service_instance():
    """Step 4: Use actual LocationService instance"""
    print("\n=== STEP 4: LocationService Instance ===")
    
    from app.game_state.services.geography.location_service import LocationService
    
    theme_id = UUID("b2494b91-f7d1-4c8d-9da2-c628816ed9de")
    world_id = UUID("f467f954-9762-4361-8893-6df42b9d9d7e")
    location_type_id = UUID("f1df65be-0db7-40d9-952f-3f8ff3b803c1")
    
    test_data = {
        "name": "Test Location", 
        "theme_id": theme_id,
        "world_id": world_id,
        "location_type_id": location_type_id
    }
    
    engine = create_async_engine(DATABASE_URL)
    async with AsyncSession(engine) as session:
        location_service = LocationService(session)
        
        try:
            # Test the validation step from LocationService
            await location_service.validator.validate_foreign_keys(test_data, {
                "theme_id": ("theme", "Theme"),
                "world_id": ("world", "World"), 
                "location_type_id": ("location_type", "Location Type")
            })
            print("✓ Step 4 PASSED: LocationService validation works")
            return True
        except Exception as e:
            print(f"✗ Step 4 FAILED: {e}")
            return False
        finally:
            await engine.dispose()


async def test_step_5_schema_validation():
    """Step 5: Use validate_schema_foreign_keys like the API does"""
    print("\n=== STEP 5: Schema-based Foreign Key Validation ===")
    
    from app.game_state.services.geography.location_service import LocationService
    from app.api.schemas.location.location_schema import LocationCreate
    
    theme_id = UUID("b2494b91-f7d1-4c8d-9da2-c628816ed9de")
    world_id = UUID("f467f954-9762-4361-8893-6df42b9d9d7e")
    location_type_id = UUID("f1df65be-0db7-40d9-952f-3f8ff3b803c1")
    
    test_data = {
        "name": "Test Location",
        "theme_id": theme_id,
        "world_id": world_id,
        "location_type_id": location_type_id
    }
    
    engine = create_async_engine(DATABASE_URL)
    async with AsyncSession(engine) as session:
        location_service = LocationService(session)
        
        try:
            # Test the schema-based validation like BaseService does
            await location_service.validator.validate_schema_foreign_keys(test_data, LocationCreate)
            print("✓ Step 5 PASSED: Schema-based validation works")
            return True
        except Exception as e:
            print(f"✗ Step 5 FAILED: {e}")
            return False
        finally:
            await engine.dispose()


async def test_step_6_full_create_entity():
    """Step 6: Full create_entity call like the API does"""
    print("\n=== STEP 6: Full create_entity Call ===")
    
    from app.game_state.services.geography.location_service import LocationService
    from app.api.schemas.location.location_schema import LocationCreate
    
    theme_id = UUID("b2494b91-f7d1-4c8d-9da2-c628816ed9de")
    world_id = UUID("f467f954-9762-4361-8893-6df42b9d9d7e")
    location_type_id = UUID("f1df65be-0db7-40d9-952f-3f8ff3b803c1")
    
    # Create the exact same data structure the API uses
    create_data = {
        "name": "Test Location Step 6",
        "theme_id": theme_id,
        "world_id": world_id,
        "location_type_id": location_type_id
    }
    
    engine = create_async_engine(DATABASE_URL)
    async with AsyncSession(engine) as session:
        location_service = LocationService(session)
        
        try:
            # Test the full create_entity method like the API does
            result = await location_service.create_entity(
                entity_data=create_data,
                validation_schema=LocationCreate
            )
            print("✓ Step 6 PASSED: Full create_entity works")
            print(f"  Created location: {result.name} (ID: {result.id})")
            return True
        except Exception as e:
            print(f"✗ Step 6 FAILED: {e}")
            return False
        finally:
            await engine.dispose()


async def test_step_7_fastapi_session():
    """Step 7: Use FastAPI session dependency like the real API"""
    print("\n=== STEP 7: FastAPI Session Dependency ===")
    
    from app.db.async_session import get_db_session
    from app.game_state.services.geography.location_service import LocationService
    from app.api.schemas.location.location_schema import LocationCreate
    
    theme_id = UUID("b2494b91-f7d1-4c8d-9da2-c628816ed9de")
    world_id = UUID("f467f954-9762-4361-8893-6df42b9d9d7e")
    location_type_id = UUID("f1df65be-0db7-40d9-952f-3f8ff3b803c1")
    
    create_data = {
        "name": "Test Location Step 7",
        "theme_id": theme_id,
        "world_id": world_id,
        "location_type_id": location_type_id
    }
    
    try:
        # Use the same session creation as FastAPI
        async for session in get_db_session():
            location_service = LocationService(session)
            
            try:
                result = await location_service.create_entity(
                    entity_data=create_data,
                    validation_schema=LocationCreate
                )
                print("✓ Step 7 PASSED: FastAPI session dependency works")
                print(f"  Created location: {result.name} (ID: {result.id})")
                return True
            except Exception as e:
                print(f"✗ Step 7 FAILED: {e}")
                return False
            finally:
                break  # Only take first session from generator
    except Exception as e:
        print(f"✗ Step 7 FAILED during session creation: {e}")
        return False


async def main():
    """Run all incremental tests"""
    print("=== INCREMENTAL DEBUG TESTS ===")
    print("Running tests step by step until we find the issue...\n")
    
    tests = [
        test_step_1_direct_validation,
        test_step_2_base_service_validator,
        test_step_3_validate_foreign_keys,
        test_step_4_location_service_instance,
        test_step_5_schema_validation,
        test_step_6_full_create_entity,
        test_step_7_fastapi_session,
    ]
    
    for i, test in enumerate(tests, 1):
        try:
            success = await test()
            if not success:
                print(f"\n🔍 ISSUE FOUND AT STEP {i}: {test.__name__}")
                print("This is where the validation starts failing!")
                break
        except Exception as e:
            print(f"\n💥 EXCEPTION AT STEP {i}: {test.__name__}")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            break
    else:
        print("\n🤔 All steps passed - the issue might be in API routing or request handling")


if __name__ == "__main__":
    asyncio.run(main())