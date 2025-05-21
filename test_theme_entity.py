#!/usr/bin/env python3
"""
Temporary test script to verify ThemeEntity functionality.
"""
import sys
from uuid import uuid4

# Add the project root to the Python path
sys.path.append("/Users/oliverga/Documents/personal/sworn")

try:
    # Import the ThemeEntity
    from app.game_state.entities.theme import ThemeEntity
    
    print("Successfully imported ThemeEntity")
    
    # Create a ThemeEntity instance
    theme = ThemeEntity(
        name="Test Theme",
        description="A theme for testing",
        genre="Fantasy",
        style="Medieval"
    )
    
    # Print basic properties
    print(f"\nTheme Properties:")
    print(f"entity_id: {theme.entity_id}")
    print(f"name: {theme.name}")
    print(f"description: {theme.description}")
    print(f"genre: {theme.genre}")
    print(f"style: {theme.style}")
    print(f"tags: {theme.tags}")
    print(f"created_at: {theme.created_at}")
    print(f"updated_at: {theme.updated_at}")
    
    # Test to_dict method
    theme_dict = theme.to_dict()
    print(f"\nTheme Dict:")
    for key, value in theme_dict.items():
        print(f"{key}: {value}")
    
    print("\nTest passed successfully!")
    
except Exception as e:
    print(f"Error testing ThemeEntity: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)