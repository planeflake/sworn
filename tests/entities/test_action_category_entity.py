import pytest
from uuid import uuid4
from app.game_state.entities.action.action_category_pydantic import ActionCategoryPydantic


class TestActionCategoryEntity:
    """Test suite for ActionCategory entity business logic."""
    
    def test_action_category_creation(self):
        """Test basic action category creation."""
        category = ActionCategoryPydantic(
            name="Gathering",
            description="Actions related to resource collection",
            icon="🌳",
            display_order=1
        )
        
        assert category.name == "Gathering"
        assert category.description == "Actions related to resource collection"
        assert category.icon == "🌳"
        assert category.display_order == 1
        assert category.parent_category_id is None  # Default
        assert category.is_active == True  # Default
        assert category.child_categories == []  # Default
    
    def test_action_category_with_parent(self):
        """Test action category with parent relationship."""
        parent_id = uuid4()
        
        category = ActionCategoryPydantic(
            name="Woodcutting",
            parent_category_id=parent_id,
            description="Cutting and harvesting wood",
            display_order=1
        )
        
        assert category.name == "Woodcutting"
        assert category.parent_category_id == parent_id
        assert category.description == "Cutting and harvesting wood"
        assert not category.is_root_category()
    
    def test_root_category_detection(self):
        """Test root category detection."""
        root_category = ActionCategoryPydantic(
            name="Gathering",
            description="Top-level gathering actions"
        )
        
        child_category = ActionCategoryPydantic(
            name="Mining",
            parent_category_id=uuid4(),
            description="Extracting minerals"
        )
        
        assert root_category.is_root_category() == True
        assert child_category.is_root_category() == False
    
    def test_category_hierarchy_display(self):
        """Test category hierarchy path display."""
        root_category = ActionCategoryPydantic(
            name="Crafting",
            description="Creating items and tools"
        )
        
        child_category = ActionCategoryPydantic(
            name="Blacksmithing",
            parent_category_id=uuid4(),
            description="Working with metal"
        )
        
        # Root category should show just its name
        assert root_category.get_full_path() == "Crafting"
        
        # Child category shows simplified path (real implementation would traverse hierarchy)
        assert "Blacksmithing" in child_category.get_full_path()
        assert ">" in child_category.get_full_path()
    
    def test_category_with_children(self):
        """Test category with child categories."""
        child1 = ActionCategoryPydantic(
            name="Mining",
            description="Extracting ores"
        )
        
        child2 = ActionCategoryPydantic(
            name="Logging",
            description="Cutting trees"
        )
        
        parent = ActionCategoryPydantic(
            name="Gathering",
            description="Resource collection",
            child_categories=[child1, child2]
        )
        
        assert len(parent.child_categories) == 2
        assert parent.child_categories[0].name == "Mining"
        assert parent.child_categories[1].name == "Logging"
    
    def test_category_ordering(self):
        """Test category display ordering."""
        category1 = ActionCategoryPydantic(
            name="Primary Actions",
            display_order=1
        )
        
        category2 = ActionCategoryPydantic(
            name="Secondary Actions",
            display_order=2
        )
        
        category3 = ActionCategoryPydantic(
            name="Advanced Actions",
            display_order=10
        )
        
        # Verify ordering values
        assert category1.display_order < category2.display_order
        assert category2.display_order < category3.display_order
    
    def test_category_activation_state(self):
        """Test category active/inactive states."""
        active_category = ActionCategoryPydantic(
            name="Combat",
            is_active=True
        )
        
        inactive_category = ActionCategoryPydantic(
            name="Deprecated Actions",
            is_active=False
        )
        
        assert active_category.is_active == True
        assert inactive_category.is_active == False
    
    def test_category_custom_separator(self):
        """Test category path with custom separator."""
        category = ActionCategoryPydantic(
            name="Smithing",
            parent_category_id=uuid4()
        )
        
        # Test different separators
        path_arrow = category.get_full_path(" > ")
        path_slash = category.get_full_path(" / ")
        path_dot = category.get_full_path(".")
        
        assert " > " in path_arrow
        assert " / " in path_slash
        assert "." in path_dot
    
    def test_category_defaults(self):
        """Test category default values."""
        minimal_category = ActionCategoryPydantic(
            name="Test Category"
        )
        
        # Check all defaults are set properly
        assert minimal_category.name == "Test Category"
        assert minimal_category.parent_category_id is None
        assert minimal_category.description == ""
        assert minimal_category.icon is None
        assert minimal_category.display_order == 0
        assert minimal_category.is_active == True
        assert minimal_category.child_categories == []
    
    def test_category_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Empty description
        category1 = ActionCategoryPydantic(
            name="Empty Description",
            description=""
        )
        assert category1.description == ""
        
        # Negative display order
        category2 = ActionCategoryPydantic(
            name="Negative Order",
            display_order=-1
        )
        assert category2.display_order == -1
        
        # Very long name
        long_name = "A" * 255
        category3 = ActionCategoryPydantic(
            name=long_name
        )
        assert category3.name == long_name