#!/usr/bin/env python
# Make sure to run in the project's virtual environment
"""
Test script to verify the updated ThemeEntity functionality.
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
    
    # Test to_dict method
    theme_dict = theme.to_dict()
    print(f"\nTheme Dict:")
    for key, value in theme_dict.items():
        print(f"{key}: {value}")
    
    # Check if 'id' is included properly
    if 'id' in theme_dict:
        print(f"\nVerified: 'id' is in to_dict() output ({theme_dict['id']})")
        print(f"id == entity_id: {theme_dict['id'] == str(theme.entity_id)}")
    else:
        print("\nFAILED: 'id' is NOT in to_dict() output")
    
    print("\nTest passed successfully!")
    
except Exception as e:
    print(f"Error testing ThemeEntity: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)