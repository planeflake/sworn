import pytest
import pytest_asyncio
from uuid import uuid4

from app.game_state.managers.tool_tier_manager import ToolTierManager
from app.game_state.entities.core.tool_tier_pydantic import ToolTierPydantic


class TestToolTierWorkflow:
    """Integration tests for complete tool tier workflows."""
    
    @pytest.fixture
    def sample_theme_id(self):
        return uuid4()
    
    def test_complete_fantasy_progression_workflow(self, sample_theme_id):
        """Test creating and using a complete fantasy tool progression."""
        # Create complete fantasy progression
        tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Fantasy")
        
        # Verify progression completeness
        assert len(tiers) == 6
        tier_names = [tier.tier_name for tier in tiers]
        expected_names = ["Basic", "Iron", "Steel", "Masterwork", "Magical", "Legendary"]
        assert tier_names == expected_names
        
        # Test tool compatibility workflow
        basic_tier = tiers[0]  # Level 1
        steel_tier = tiers[2]  # Level 3
        legendary_tier = tiers[5]  # Level 6
        
        # Basic tier can only harvest basic materials (tier 1)
        assert basic_tier.can_harvest_tier(1) == True
        assert basic_tier.can_harvest_tier(3) == False
        assert basic_tier.can_harvest_tier(6) == False
        
        # Steel tier can harvest up to steel materials (tier 1-3)
        assert steel_tier.can_harvest_tier(1) == True
        assert steel_tier.can_harvest_tier(3) == True
        assert steel_tier.can_harvest_tier(6) == False
        
        # Legendary tier can harvest everything (tier 1-6)
        assert legendary_tier.can_harvest_tier(1) == True
        assert legendary_tier.can_harvest_tier(3) == True
        assert legendary_tier.can_harvest_tier(6) == True
        
        # Test efficiency progression
        base_duration = 60
        basic_duration = basic_tier.get_efficiency_bonus(base_duration)
        steel_duration = steel_tier.get_efficiency_bonus(base_duration)
        legendary_duration = legendary_tier.get_efficiency_bonus(base_duration)
        
        # Higher tiers should be more efficient (shorter duration)
        assert basic_duration > steel_duration > legendary_duration
        assert basic_duration == 60  # 1.0x multiplier
        assert steel_duration == 40  # 1.5x multiplier (60/1.5)
        assert legendary_duration == 12  # 5.0x multiplier (60/5)
    
    def test_multi_theme_comparison_workflow(self):
        """Test creating and comparing multiple theme progressions."""
        fantasy_theme_id = uuid4()
        scifi_theme_id = uuid4()
        
        # Create progressions for different themes
        fantasy_tiers = ToolTierManager.create_theme_progression(fantasy_theme_id, "Fantasy")
        scifi_tiers = ToolTierManager.create_theme_progression(scifi_theme_id, "Sci-Fi")
        
        # Verify both have same structure but different names
        assert len(fantasy_tiers) == len(scifi_tiers) == 6
        
        # Compare tier names by level
        fantasy_by_level = {tier.tier_level: tier.tier_name for tier in fantasy_tiers}
        scifi_by_level = {tier.tier_level: tier.tier_name for tier in scifi_tiers}
        
        # Level 1 comparison
        assert fantasy_by_level[1] == "Basic"
        assert scifi_by_level[1] == "Basic"  # Both start with Basic
        
        # Level 3 comparison - should be different
        assert fantasy_by_level[3] == "Steel"
        assert scifi_by_level[3] == "Plasma"
        
        # Level 5 comparison - very different
        assert fantasy_by_level[5] == "Magical"
        assert scifi_by_level[5] == "Nano"
        
        # Level 6 comparison
        assert fantasy_by_level[6] == "Legendary"
        assert scifi_by_level[6] == "Cosmic"
        
        # Verify efficiency multipliers are the same across themes
        for level in range(1, 7):
            fantasy_tier = next(t for t in fantasy_tiers if t.tier_level == level)
            scifi_tier = next(t for t in scifi_tiers if t.tier_level == level)
            assert fantasy_tier.effectiveness_multiplier == scifi_tier.effectiveness_multiplier
    
    def test_tool_upgrade_progression_workflow(self, sample_theme_id):
        """Test a character's tool upgrade progression workflow."""
        tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Fantasy")
        
        # Simulate character progression through tool tiers
        character_progression = []
        
        for tier in tiers:
            # Character acquires new tool tier
            character_progression.append({
                "tier_level": tier.tier_level,
                "tier_name": tier.tier_name,
                "tech_requirement": tier.required_tech_level,
                "efficiency": tier.effectiveness_multiplier
            })
        
        # Verify progression makes sense
        assert len(character_progression) == 6
        
        # Tech requirements should increase with tier level
        tech_levels = [step["tech_requirement"] for step in character_progression]
        assert tech_levels == [0, 1, 2, 3, 4, 5]  # Each tier requires previous tier's tech
        
        # Efficiency should increase with tier level
        efficiencies = [step["efficiency"] for step in character_progression]
        for i in range(1, len(efficiencies)):
            assert efficiencies[i] > efficiencies[i-1]
    
    def test_material_harvesting_workflow(self, sample_theme_id):
        """Test workflow of harvesting different materials with different tools."""
        tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Post-Apocalyptic")
        
        # Define materials with their tier requirements
        materials = [
            {"name": "Scrap Metal", "required_tier": 1},
            {"name": "Salvaged Steel", "required_tier": 2},
            {"name": "Reinforced Alloy", "required_tier": 3},
            {"name": "Military Grade Composite", "required_tier": 4},
            {"name": "Experimental Material", "required_tier": 5},
            {"name": "Artifact Substance", "required_tier": 6}
        ]
        
        # Test what each tool tier can harvest
        harvesting_matrix = {}
        
        for tier in tiers:
            harvestable = []
            for material in materials:
                if tier.can_harvest_tier(material["required_tier"]):
                    harvestable.append(material["name"])
            harvesting_matrix[tier.tier_name] = harvestable
        
        # Verify progression
        assert len(harvesting_matrix["Scrap"]) == 1  # Only scrap metal
        assert len(harvesting_matrix["Salvaged"]) == 2  # Scrap + salvaged
        assert len(harvesting_matrix["Military"]) == 4  # Everything up to military
        assert len(harvesting_matrix["Artifact"]) == 6  # Everything
        
        # Verify specific capabilities
        assert "Scrap Metal" in harvesting_matrix["Scrap"]
        assert "Artifact Substance" not in harvesting_matrix["Military"]
        assert "Artifact Substance" in harvesting_matrix["Artifact"]
    
    def test_efficiency_calculation_workflow(self, sample_theme_id):
        """Test complete efficiency calculation workflow for different scenarios."""
        tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Fantasy")
        
        # Define different task durations
        task_scenarios = [
            {"name": "Quick Hack", "base_duration": 10},
            {"name": "Data Mining", "base_duration": 60},
            {"name": "System Breach", "base_duration": 300}
        ]
        
        efficiency_results = {}
        
        for scenario in task_scenarios:
            scenario_results = {}
            for tier in tiers:
                duration = tier.get_efficiency_bonus(scenario["base_duration"])
                scenario_results[tier.tier_name] = duration
            efficiency_results[scenario["name"]] = scenario_results
        
        # Debug: Print available tier names
        print("Available tier names:", list(efficiency_results["Quick Hack"].keys()))
        
        # Verify efficiency improvements
        for scenario_name, results in efficiency_results.items():
            # Legendary tools should always be most efficient (fantasy theme)
            if "Legendary" in results and "Basic" in results:
                assert results["Legendary"] <= results["Basic"]
            if "Magical" in results and "Steel" in results:
                assert results["Magical"] <= results["Steel"]
            
            # Verify minimum duration enforcement
            for duration in results.values():
                assert duration >= 5  # Minimum 5 seconds
        
        # Test specific improvements
        quick_hack_basic = efficiency_results["Quick Hack"]["Basic"]
        quick_hack_legendary = efficiency_results["Quick Hack"]["Legendary"]
        
        # Legendary should be much faster than Basic tools
        assert quick_hack_legendary < quick_hack_basic
    
    def test_theme_specific_flavor_workflow(self, sample_theme_id):
        """Test that theme-specific flavor and colors are properly applied."""
        lovecraftian_tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Lovecraftian")
        
        # Verify lovecraftian-specific elements
        tier_names = [tier.tier_name for tier in lovecraftian_tiers]
        assert "Eldritch" in tier_names
        assert "Cursed" in tier_names
        assert "Cosmic" in tier_names
        
        # Verify flavor text contains theme-appropriate words
        all_flavor_text = " ".join(tier.flavor_text for tier in lovecraftian_tiers if tier.flavor_text)
        theme_words = ["worldly", "otherworldly", "blessed", "cursed", "eldritch", "cosmic", "mortal"]
        
        found_theme_words = [word for word in theme_words if word.lower() in all_flavor_text.lower()]
        assert len(found_theme_words) >= 3  # Should find at least 3 theme-appropriate words
        
        # Verify colors are assigned
        for tier in lovecraftian_tiers:
            assert tier.color_hex is not None
            assert tier.color_hex.startswith("#")
            assert len(tier.color_hex) == 7  # Proper hex color format
    
    def test_edge_case_workflow(self, sample_theme_id):
        """Test edge cases and boundary conditions in workflows."""
        tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Fantasy")
        
        # Test with extreme values
        legendary_tier = tiers[5]  # Highest tier
        
        # Test very short duration
        short_duration = legendary_tier.get_efficiency_bonus(1)
        assert short_duration == 5  # Should enforce minimum
        
        # Test very long duration
        long_duration = legendary_tier.get_efficiency_bonus(10000)
        expected = int(10000 / legendary_tier.effectiveness_multiplier)
        assert long_duration == expected
        
        # Test harvest compatibility edge cases
        assert legendary_tier.can_harvest_tier(0) == True  # Should handle tier 0
        assert legendary_tier.can_harvest_tier(100) == False  # Should handle very high tiers
        
        # Test with unknown theme (should fallback to fantasy)
        unknown_tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Unknown Theme")
        fantasy_tiers = ToolTierManager.create_theme_progression(sample_theme_id, "Fantasy")
        
        # Should have same tier names (fallback to fantasy)
        unknown_names = [tier.tier_name for tier in unknown_tiers]
        fantasy_names = [tier.tier_name for tier in fantasy_tiers]
        assert unknown_names == fantasy_names