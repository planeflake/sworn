import pytest
from uuid import uuid4
from app.game_state.managers.tool_tier_manager import ToolTierManager
from app.game_state.entities.core.tool_tier_pydantic import ToolTierPydantic


class TestToolTierManager:
    """Test suite for ToolTier manager."""
    
    @pytest.fixture
    def sample_theme_id(self):
        """Sample theme ID for testing."""
        return uuid4()
    
    def test_create_tool_tier_basic(self, sample_theme_id):
        """Test basic tool tier creation."""
        tier = ToolTierManager.create_tool_tier(
            name="Steel Tools",
            theme_id=sample_theme_id,
            tier_name="Steel",
            tier_level=3,
            effectiveness_multiplier=1.5,
            description="High-quality steel tools"
        )
        
        assert isinstance(tier, ToolTierPydantic)
        assert tier.name == "Steel Tools"
        assert tier.theme_id == sample_theme_id
        assert tier.tier_name == "Steel"
        assert tier.tier_level == 3
        assert tier.effectiveness_multiplier == 1.5
        assert tier.description == "High-quality steel tools"
        assert tier.required_tech_level == 0  # Default
        assert tier.required_materials == []  # Default
    
    def test_create_tool_tier_with_all_options(self, sample_theme_id):
        """Test tool tier creation with all optional parameters."""
        material1_id = uuid4()
        material2_id = uuid4()
        custom_id = uuid4()
        
        tier = ToolTierManager.create_tool_tier(
            name="Magical Tools",
            theme_id=sample_theme_id,
            tier_name="Magical",
            tier_level=5,
            effectiveness_multiplier=3.0,
            description="Enchanted mystical tools",
            icon="✨",
            required_tech_level=4,
            required_materials=[material1_id, material2_id],
            flavor_text="Touched by ancient magic",
            color_hex="#9370DB",
            entity_id=custom_id
        )
        
        assert tier.entity_id == custom_id
        assert tier.name == "Magical Tools"
        assert tier.icon == "✨"
        assert tier.required_tech_level == 4
        assert tier.required_materials == [material1_id, material2_id]
        assert tier.flavor_text == "Touched by ancient magic"
        assert tier.color_hex == "#9370DB"
    
    def test_create_theme_progression_fantasy(self, sample_theme_id):
        """Test creating fantasy theme progression."""
        tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Fantasy")
        
        assert len(tiers) == 6
        
        # Check tier progression
        tier_names = [tier.tier_name for tier in tiers]
        expected_names = ["Basic", "Iron", "Steel", "Masterwork", "Magical", "Legendary"]
        assert tier_names == expected_names
        
        # Check tier levels are sequential
        tier_levels = [tier.tier_level for tier in tiers]
        assert tier_levels == [1, 2, 3, 4, 5, 6]
        
        # Check effectiveness multipliers increase
        multipliers = [tier.effectiveness_multiplier for tier in tiers]
        expected_multipliers = [1.0, 1.2, 1.5, 2.0, 3.0, 5.0]
        assert multipliers == expected_multipliers
        
        # Check all have same theme
        for tier in tiers:
            assert tier.theme_id == sample_theme_id
    
    def test_create_theme_progression_sci_fi(self, sample_theme_id):
        """Test creating sci-fi theme progression."""
        tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Sci-Fi")
        
        assert len(tiers) == 6
        
        tier_names = [tier.tier_name for tier in tiers]
        expected_names = ["Basic", "Alloy", "Plasma", "Quantum", "Nano", "Cosmic"]
        assert tier_names == expected_names
        
        # Check sci-fi specific colors
        assert tiers[2].color_hex == "#FF6347"  # Plasma should be red-ish
        assert tiers[3].color_hex == "#40E0D0"  # Quantum should be cyan-ish
    
    def test_create_theme_progression_post_apocalyptic(self, sample_theme_id):
        """Test creating post-apocalyptic theme progression."""
        tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Post-Apocalyptic")
        
        assert len(tiers) == 6
        
        tier_names = [tier.tier_name for tier in tiers]
        expected_names = ["Scrap", "Salvaged", "Reinforced", "Military", "Experimental", "Artifact"]
        assert tier_names == expected_names
        
        # Check post-apocalyptic flavor
        assert "debris" in tiers[0].flavor_text.lower()
        assert "pre-war" in tiers[3].flavor_text.lower()
    
    def test_create_theme_progression_lovecraftian(self, sample_theme_id):
        """Test creating lovecraftian theme progression."""
        tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Lovecraftian")
        
        assert len(tiers) == 6
        
        tier_names = [tier.tier_name for tier in tiers]
        expected_names = ["Mundane", "Crafted", "Blessed", "Cursed", "Eldritch", "Cosmic"]
        assert tier_names == expected_names
        
        # Check lovecraftian flavor
        assert "worldly" in tiers[0].flavor_text.lower()
        assert "eldritch" in tiers[4].flavor_text.lower() or "otherworldly" in tiers[4].flavor_text.lower()
    
    def test_create_theme_progression_unknown_theme(self, sample_theme_id):
        """Test creating progression for unknown theme falls back to fantasy."""
        tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Unknown Theme")
        
        assert len(tiers) == 6
        
        # Should fall back to fantasy progression
        tier_names = [tier.tier_name for tier in tiers]
        expected_names = ["Basic", "Iron", "Steel", "Masterwork", "Magical", "Legendary"]
        assert tier_names == expected_names
    
    def test_create_theme_progression_case_insensitive(self, sample_theme_id):
        """Test that theme name matching is case insensitive."""
        tiers_lower = ToolTierManager.create_theme_progression(sample_theme_id, "sci-fi")
        tiers_upper = ToolTierManager.create_theme_progression(sample_theme_id, "SCI-FI")
        tiers_mixed = ToolTierManager.create_theme_progression(sample_theme_id, "Sci-Fi")
        
        # All should produce same tier names
        names_lower = [tier.tier_name for tier in tiers_lower]
        names_upper = [tier.tier_name for tier in tiers_upper]
        names_mixed = [tier.tier_name for tier in tiers_mixed]
        
        assert names_lower == names_upper == names_mixed
        assert names_lower == ["Basic", "Alloy", "Plasma", "Quantum", "Nano", "Cosmic"]
    
    def test_calculate_harvest_compatibility(self):
        """Test static harvest compatibility method."""
        # Tool tier 3 can harvest tier 1, 2, 3 materials
        assert ToolTierManager.calculate_harvest_compatibility(3, 1) == True
        assert ToolTierManager.calculate_harvest_compatibility(3, 2) == True
        assert ToolTierManager.calculate_harvest_compatibility(3, 3) == True
        
        # Tool tier 3 cannot harvest tier 4+ materials
        assert ToolTierManager.calculate_harvest_compatibility(3, 4) == False
        assert ToolTierManager.calculate_harvest_compatibility(3, 5) == False
        assert ToolTierManager.calculate_harvest_compatibility(3, 6) == False
        
        # Edge cases
        assert ToolTierManager.calculate_harvest_compatibility(1, 1) == True
        assert ToolTierManager.calculate_harvest_compatibility(6, 6) == True
        assert ToolTierManager.calculate_harvest_compatibility(6, 1) == True
    
    def test_get_efficiency_multiplier(self):
        """Test static efficiency multiplier method."""
        assert ToolTierManager.get_efficiency_multiplier(1) == 1.0
        assert ToolTierManager.get_efficiency_multiplier(2) == 1.2
        assert ToolTierManager.get_efficiency_multiplier(3) == 1.5
        assert ToolTierManager.get_efficiency_multiplier(4) == 2.0
        assert ToolTierManager.get_efficiency_multiplier(5) == 3.0
        assert ToolTierManager.get_efficiency_multiplier(6) == 5.0
        
        # Test unknown tier returns default
        assert ToolTierManager.get_efficiency_multiplier(7) == 1.0
        assert ToolTierManager.get_efficiency_multiplier(0) == 1.0
    
    def test_tech_level_progression(self, sample_theme_id):
        """Test that tech levels progress correctly."""
        tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Fantasy")
        
        # Tech level should be tier_level - 1
        for tier in tiers:
            expected_tech_level = tier.tier_level - 1
            assert tier.required_tech_level == expected_tech_level
    
    def test_color_consistency(self, sample_theme_id):
        """Test that color schemes are consistently applied."""
        fantasy_tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Fantasy")
        
        # Each tier should have a color
        for tier in fantasy_tiers:
            assert tier.color_hex is not None
            assert tier.color_hex.startswith("#")
            assert len(tier.color_hex) == 7  # #RRGGBB format
    
    def test_flavor_text_exists(self, sample_theme_id):
        """Test that all tiers have flavor text."""
        tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Fantasy")
        
        for tier in tiers:
            assert tier.flavor_text is not None
            assert len(tier.flavor_text) > 0