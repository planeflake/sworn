"""
Test the resource structure directly to verify the implementation.
"""

import unittest
from uuid import uuid4

from app.db.models.resources.resource_blueprint import ResourceBlueprint
from app.db.models.resources.resource_node import ResourceNode
from app.game_state.enums.shared import RarityEnum

class TestResourceStructure(unittest.TestCase):
    def test_resource_blueprint(self):
        """Test creating a ResourceBlueprint"""
        resource = ResourceBlueprint(
            name="Wood",
            description="Common building material",
            rarity=RarityEnum.COMMON
        )

        self.assertEqual(resource.name, "Wood")
        self.assertEqual(resource.description, "Common building material")
        self.assertEqual(resource.rarity, RarityEnum.COMMON)
        self.assertEqual(resource.rarity.value, "Common")

    def test_resource_node(self):
        """Test creating a ResourceNode"""
        location_id = uuid4()
        node = ResourceNode(
            name="Oak Tree",
            description="A sturdy oak tree containing wood resources",
            location_id=location_id,
        )

        self.assertEqual(node.name, "Oak Tree")
        self.assertEqual(node.description, "A sturdy oak tree containing wood resources")
        self.assertEqual(node.location_id, location_id)

if __name__ == "__main__":
    unittest.main()