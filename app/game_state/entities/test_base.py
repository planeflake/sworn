#!/usr/bin/env python3
"""
Test script to verify that the BaseEntityPydantic class is working correctly.
"""

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

def test_base_entity():
    """Test that we can create a BaseEntityPydantic instance."""
    entity = BaseEntityPydantic(name="Test Entity")
    print(f"Created entity: {entity}")
    print(f"Entity dict: {entity.to_dict()}")
    return entity

if __name__ == "__main__":
    print("Testing BaseEntityPydantic...")
    test_base_entity()
    print("Test completed!")