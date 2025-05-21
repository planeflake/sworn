#!/usr/bin/env python
# Make sure to run in the project's virtual environment
"""
Test script to verify ThemeRepository functionality with the updated ThemeEntity.
"""
import asyncio
import sys
from uuid import uuid4

# Add the project root to the Python path
sys.path.append("/Users/oliverga/Documents/personal/sworn")

from app.game_state.entities.theme import ThemeEntity
from app.game_state.repositories.theme_repository import ThemeRepository
from app.db.async_session import get_db_session

async def test_repository():
    # Get a database session
    async with get_db_session() as db:
        try:
            # Create a theme repository
            repo = ThemeRepository(db)
            print("Successfully created ThemeRepository")
            
            # Test finding theme by ID
            # Use one of the IDs from the themes table
            test_id = "104275ef-4ae9-4364-86f1-2cbeb886c3ad"
            theme = await repo.find_by_id(test_id)
            
            if theme:
                print(f"\nFound theme by ID:")
                print(f"entity_id: {theme.entity_id}")
                print(f"name: {theme.name}")
                print(f"description: {theme.description}")
                print(f"genre: {theme.genre}")
                print(f"style: {theme.style}")
                
                # Test to_dict method
                theme_dict = theme.to_dict()
                print(f"\nTheme Dict:")
                for key, value in theme_dict.items():
                    print(f"{key}: {value}")
            else:
                print(f"Theme with ID {test_id} not found!")
            
            # Create a new theme entity for testing
            new_theme = ThemeEntity(
                name=f"Test Theme {uuid4()}",
                description="A theme created for testing repository",
                genre="Test",
                style="Automated"
            )
            
            # Save the theme
            saved_theme = await repo.save(new_theme)
            print(f"\nSaved theme:")
            print(f"entity_id: {saved_theme.entity_id}")
            print(f"name: {saved_theme.name}")
            
            # Test that the theme can be retrieved after saving
            retrieved_theme = await repo.find_by_id(saved_theme.entity_id)
            if retrieved_theme:
                print(f"\nSuccessfully retrieved saved theme:")
                print(f"entity_id: {retrieved_theme.entity_id}")
                print(f"name: {retrieved_theme.name}")
            else:
                print(f"Failed to retrieve saved theme!")
            
            # Delete the test theme (cleanup)
            deleted = await repo.delete(saved_theme.entity_id)
            print(f"Deleted theme: {deleted}")
            
            print("\nTest completed successfully!")
            
        except Exception as e:
            print(f"Error testing ThemeRepository: {e}")
            import traceback
            traceback.print_exc()
            return

if __name__ == "__main__":
    asyncio.run(test_repository())