import pytest
from uuid import uuid4
from app.game_state.entities.core.tool_tier_pydantic import ToolTierPydantic


class TestToolTierEntity:
    """Test suite for ToolTier entity business logic."""
    
    def test_tool_tier_creation(self):
        """Test basic tool tier creation."""
        theme_id = uuid4()
        tier = ToolTierPydantic(
            name="Steel Tools",
            theme_id=theme_id,
            tier_name="Steel",
            tier_level=3,
            effectiveness_multiplier=1.5,
            description="High-quality steel tools"
        )
        
        assert tier.name == "Steel Tools"
        assert tier.theme_id == theme_id
        assert tier.tier_name == "Steel"
        assert tier.tier_level == 3
        assert tier.effectiveness_multiplier == 1.5
        assert tier.description == "High-quality steel tools"
        assert tier.required_tech_level == 0  # Default
        assert tier.required_materials == []  # Default
    
    def test_can_harvest_tier_logic(self):
        """Test tool tier harvest compatibility checking."""
        tier = ToolTierPydantic(
            name="Steel Tools",
            theme_id=uuid4(),
            tier_name="Steel",
            tier_level=3,
            effectiveness_multiplier=1.5
        )
        
        # Can harvest equal or lower tier requirements
        assert tier.can_harvest_tier(1) == True  # Basic requirement
        assert tier.can_harvest_tier(2) == True  # Iron requirement  
        assert tier.can_harvest_tier(3) == True  # Steel requirement
        
        # Cannot harvest higher tier requirements
        assert tier.can_harvest_tier(4) == False  # Masterwork requirement
        assert tier.can_harvest_tier(5) == False  # Magical requirement
        assert tier.can_harvest_tier(6) == False  # Legendary requirement
    
    def test_efficiency_bonus_calculation(self):
        """Test tool efficiency calculations."""
        basic_tier = ToolTierPydantic(
            name="Basic Tools",
            theme_id=uuid4(),
            tier_name="Basic",
            tier_level=1,
            effectiveness_multiplier=1.0
        )
        
        magical_tier = ToolTierPydantic(
            name="Magical Tools",
            theme_id=uuid4(),
            tier_name="Magical",
            tier_level=5,
            effectiveness_multiplier=3.0
        )
        
        base_duration = 60
        
        # Basic tier provides no bonus
        basic_duration = basic_tier.get_efficiency_bonus(base_duration)
        assert basic_duration == 60
        
        # Magical tier provides 3x efficiency (60/3 = 20)
        magical_duration = magical_tier.get_efficiency_bonus(base_duration)
        assert magical_duration == 20
        
        # Test minimum duration enforcement
        short_duration = basic_tier.get_efficiency_bonus(3)
        assert short_duration == 5  # Minimum 5 seconds
    
    def test_tier_level_checking(self):
        """Test tier level utility methods."""
        basic_tier = ToolTierPydantic(
            name="Basic Tools",
            theme_id=uuid4(),
            tier_name="Basic",
            tier_level=1,
            effectiveness_multiplier=1.0
        )
        
        legendary_tier = ToolTierPydantic(
            name="Legendary Tools",
            theme_id=uuid4(),
            tier_name="Legendary",
            tier_level=6,
            effectiveness_multiplier=5.0
        )
        
        # Basic tier checks
        assert basic_tier.is_basic_tier() == True
        assert basic_tier.is_max_tier() == False
        
        # Legendary tier checks
        assert legendary_tier.is_basic_tier() == False
        assert legendary_tier.is_max_tier() == True
    
    def test_tool_tier_with_materials(self):
        """Test tool tier with material requirements."""
        steel_resource_id = uuid4()
        coal_resource_id = uuid4()
        
        tier = ToolTierPydantic(
            name="Steel Tools",
            theme_id=uuid4(),
            tier_name="Steel",
            tier_level=3,
            effectiveness_multiplier=1.5,
            required_tech_level=2,
            required_materials=[steel_resource_id, coal_resource_id]
        )
        
        assert tier.required_tech_level == 2
        assert len(tier.required_materials) == 2
        assert steel_resource_id in tier.required_materials
        assert coal_resource_id in tier.required_materials
    
    def test_tool_tier_with_theming(self):
        """Test tool tier with theme-specific attributes."""
        tier = ToolTierPydantic(
            name="Eldritch Tools",
            theme_id=uuid4(),
            tier_name="Eldritch",
            tier_level=5,
            effectiveness_multiplier=3.0,
            flavor_text="Touched by otherworldly power beyond understanding",
            color_hex="#4B0082",
            icon="🌌"
        )
        
        assert tier.flavor_text == "Touched by otherworldly power beyond understanding"
        assert tier.color_hex == "#4B0082"
        assert tier.icon == "🌌"
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        tier = ToolTierPydantic(
            name="Test Tier",
            theme_id=uuid4(),
            tier_name="Test",
            tier_level=1,
            effectiveness_multiplier=0.5  # Very inefficient tool
        )
        
        # Test with very low efficiency
        base_duration = 10
        result = tier.get_efficiency_bonus(base_duration)
        assert result == 20  # 10 / 0.5 = 20
        
        # Test harvest checking with edge values
        assert tier.can_harvest_tier(0) == True  # Can always harvest tier 0
        assert tier.can_harvest_tier(-1) == True  # Negative values should work
        
    def test_tool_tier_defaults(self):
        """Test that tool tier has proper defaults."""
        minimal_tier = ToolTierPydantic(
            theme_id=uuid4(),
            tier_name="Minimal",
            tier_level=1
        )
        
        # Check all defaults are set properly
        assert minimal_tier.name == "Unnamed Entity"  # From BaseEntityPydantic
        assert minimal_tier.tier_name == "Minimal"
        assert minimal_tier.tier_level == 1
        assert minimal_tier.effectiveness_multiplier == 1.0
        assert minimal_tier.description == ""
        assert minimal_tier.icon is None
        assert minimal_tier.required_tech_level == 0
        assert minimal_tier.required_materials == []
        assert minimal_tier.flavor_text is None
        assert minimal_tier.color_hex is None