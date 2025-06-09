import pytest
from uuid import uuid4
from app.game_state.entities.action.action_template_pydantic import (
    ActionTemplatePydantic,
    ActionRequirement,
    ActionReward
)


class TestActionTemplateEntity:
    """Test suite for ActionTemplate entity business logic."""
    
    @pytest.fixture
    def sample_category_id(self):
        return uuid4()
    
    @pytest.fixture
    def sample_skill_id(self):
        return uuid4()
    
    @pytest.fixture
    def sample_tool_tier_id(self):
        return uuid4()
    
    @pytest.fixture
    def sample_location_type_id(self):
        return uuid4()
    
    @pytest.fixture
    def sample_resource_id(self):
        return uuid4()
    
    def test_action_requirement_creation(self, sample_skill_id, sample_tool_tier_id, sample_location_type_id):
        """Test ActionRequirement creation."""
        requirement = ActionRequirement(
            skill_id=sample_skill_id,
            skill_level=5,
            required_tool_tier_id=sample_tool_tier_id,
            required_location_type_ids=[sample_location_type_id],
            stamina_cost=10
        )
        
        assert requirement.skill_id == sample_skill_id
        assert requirement.skill_level == 5
        assert requirement.required_tool_tier_id == sample_tool_tier_id
        assert requirement.required_location_type_ids == [sample_location_type_id]
        assert requirement.stamina_cost == 10
        assert requirement.required_item_ids == []  # Default
    
    def test_action_reward_creation(self, sample_resource_id):
        """Test ActionReward creation."""
        reward = ActionReward(
            resource_id=sample_resource_id,
            quantity_min=1,
            quantity_max=3,
            drop_chance=0.8,
            experience_points=25
        )
        
        assert reward.resource_id == sample_resource_id
        assert reward.quantity_min == 1
        assert reward.quantity_max == 3
        assert reward.drop_chance == 0.8
        assert reward.experience_points == 25
        assert reward.item_id is None  # Default
    
    def test_action_template_basic_creation(self, sample_category_id):
        """Test basic ActionTemplate creation."""
        template = ActionTemplatePydantic(
            name="Gather Wood",
            category_id=sample_category_id,
            description="Collect wood from trees",
            action_verb="gather",
            base_duration_seconds=30,
            difficulty_level=1
        )
        
        assert template.name == "Gather Wood"
        assert template.category_id == sample_category_id
        assert template.description == "Collect wood from trees"
        assert template.action_verb == "gather"
        assert template.base_duration_seconds == 30
        assert template.difficulty_level == 1
        assert template.is_repeatable == True  # Default
        assert template.is_active == True  # Default
    
    def test_action_template_with_requirements(self, sample_category_id, sample_skill_id, sample_tool_tier_id):
        """Test ActionTemplate with requirements."""
        requirement = ActionRequirement(
            skill_id=sample_skill_id,
            skill_level=3,
            required_tool_tier_id=sample_tool_tier_id,
            stamina_cost=5
        )
        
        template = ActionTemplatePydantic(
            name="Cut Steel",
            category_id=sample_category_id,
            requirements=requirement,
            base_duration_seconds=60,
            difficulty_level=3
        )
        
        assert template.requirements.skill_id == sample_skill_id
        assert template.requirements.skill_level == 3
        assert template.requirements.required_tool_tier_id == sample_tool_tier_id
        assert template.requirements.stamina_cost == 5
    
    def test_action_template_with_rewards(self, sample_category_id, sample_resource_id):
        """Test ActionTemplate with rewards."""
        reward = ActionReward(
            resource_id=sample_resource_id,
            quantity_min=2,
            quantity_max=5,
            drop_chance=1.0,
            experience_points=15
        )
        
        template = ActionTemplatePydantic(
            name="Mine Iron",
            category_id=sample_category_id,
            possible_rewards=[reward],
            base_duration_seconds=45
        )
        
        assert len(template.possible_rewards) == 1
        assert template.possible_rewards[0].resource_id == sample_resource_id
        assert template.possible_rewards[0].quantity_min == 2
        assert template.possible_rewards[0].quantity_max == 5
        assert template.possible_rewards[0].drop_chance == 1.0
    
    def test_get_effective_duration_with_skill_bonus(self, sample_category_id):
        """Test duration calculation with skill level bonus."""
        template = ActionTemplatePydantic(
            name="Craft Item",
            category_id=sample_category_id,
            base_duration_seconds=100,
            requirements=ActionRequirement(skill_level=5)
        )
        
        # Character with skill level 5 (meets requirement)
        duration_met = template.get_effective_duration(character_skill_level=5)
        assert duration_met == 100  # No bonus for meeting requirement
        
        # Character with skill level 10 (5 levels above requirement)
        duration_bonus = template.get_effective_duration(character_skill_level=10)
        # 5 levels * 0.05 = 0.25 (25% reduction)
        expected_duration = int(100 * (1 - 0.25))  # 75 seconds
        assert duration_bonus == expected_duration
        
        # Character with skill level 15 (10 levels above requirement)
        duration_max_bonus = template.get_effective_duration(character_skill_level=15)
        # 10 levels * 0.05 = 0.5, but max reduction is 50%
        expected_duration = int(100 * (1 - 0.5))  # 50 seconds
        assert duration_max_bonus == expected_duration
    
    def test_get_effective_duration_with_tool_bonus(self, sample_category_id):
        """Test duration calculation with tool effectiveness."""
        template = ActionTemplatePydantic(
            name="Harvest Resource",
            category_id=sample_category_id,
            base_duration_seconds=60,
            requirements=ActionRequirement(skill_level=0)  # No skill requirement to isolate tool testing
        )
        
        # Basic tool (1.0x effectiveness)
        duration_basic = template.get_effective_duration(
            character_skill_level=0,  # Same as requirement to avoid skill bonus
            tool_effectiveness_multiplier=1.0
        )
        assert duration_basic == 60
        
        # Steel tool (1.5x effectiveness)
        duration_steel = template.get_effective_duration(
            character_skill_level=0,  # Same as requirement to avoid skill bonus
            tool_effectiveness_multiplier=1.5
        )
        assert duration_steel == 40  # 60 / 1.5
        
        # Magical tool (3.0x effectiveness)
        duration_magical = template.get_effective_duration(
            character_skill_level=0,  # Same as requirement to avoid skill bonus
            tool_effectiveness_multiplier=3.0
        )
        assert duration_magical == 20  # 60 / 3.0
    
    def test_get_effective_duration_minimum_enforcement(self, sample_category_id):
        """Test that duration has a minimum of 5 seconds."""
        template = ActionTemplatePydantic(
            name="Quick Action",
            category_id=sample_category_id,
            base_duration_seconds=10,
            requirements=ActionRequirement(skill_level=0)  # No skill requirement
        )
        
        # With extreme tool effectiveness, should still be minimum 5 seconds
        duration = template.get_effective_duration(
            character_skill_level=0,  # Match requirement to avoid skill bonus
            tool_effectiveness_multiplier=10.0
        )
        assert duration == 5  # Minimum enforced
    
    def test_can_perform_skill_requirement(self, sample_category_id, sample_skill_id):
        """Test action performance based on skill requirements."""
        template = ActionTemplatePydantic(
            name="Advanced Crafting",
            category_id=sample_category_id,
            requirements=ActionRequirement(
                skill_id=sample_skill_id,
                skill_level=10
            )
        )
        
        # Character with insufficient skill
        can_perform_low = template.can_perform(character_skill_level=5)
        assert can_perform_low == False
        
        # Character with exact skill requirement
        can_perform_exact = template.can_perform(character_skill_level=10)
        assert can_perform_exact == True
        
        # Character with higher skill
        can_perform_high = template.can_perform(character_skill_level=15)
        assert can_perform_high == True
    
    def test_can_perform_tool_tier_requirement(self, sample_category_id):
        """Test action performance based on tool tier requirements."""
        template = ActionTemplatePydantic(
            name="Steel Working",
            category_id=sample_category_id,
            requirements=ActionRequirement(skill_level=1)  # Low skill requirement
        )
        
        # Character with insufficient tool tier
        can_perform_low = template.can_perform(
            character_skill_level=5,
            available_tool_tier_level=2,
            required_tool_tier_level=3
        )
        assert can_perform_low == False
        
        # Character with exact tool tier requirement
        can_perform_exact = template.can_perform(
            character_skill_level=5,
            available_tool_tier_level=3,
            required_tool_tier_level=3
        )
        assert can_perform_exact == True
        
        # Character with higher tool tier
        can_perform_high = template.can_perform(
            character_skill_level=5,
            available_tool_tier_level=5,
            required_tool_tier_level=3
        )
        assert can_perform_high == True
    
    def test_can_perform_no_requirements(self, sample_category_id):
        """Test action performance with no special requirements."""
        template = ActionTemplatePydantic(
            name="Basic Gathering",
            category_id=sample_category_id,
            requirements=ActionRequirement()  # No requirements
        )
        
        # Any character should be able to perform
        assert template.can_perform(character_skill_level=1) == True
        assert template.can_perform(character_skill_level=0) == True
    
    def test_action_template_unlocking(self, sample_category_id):
        """Test action template unlocking mechanisms."""
        prerequisite_id = uuid4()
        
        template = ActionTemplatePydantic(
            name="Advanced Technique",
            category_id=sample_category_id,
            prerequisite_action_ids=[prerequisite_id],
            unlock_world_day=10,
            max_skill_level=50
        )
        
        assert len(template.prerequisite_action_ids) == 1
        assert template.prerequisite_action_ids[0] == prerequisite_id
        assert template.unlock_world_day == 10
        assert template.max_skill_level == 50
    
    def test_action_template_ui_attributes(self, sample_category_id):
        """Test action template UI and display attributes."""
        template = ActionTemplatePydantic(
            name="Mystical Ritual",
            category_id=sample_category_id,
            icon="🔮",
            flavor_text="Channel mystical energies",
            display_order=5,
            is_repeatable=False
        )
        
        assert template.icon == "🔮"
        assert template.flavor_text == "Channel mystical energies"
        assert template.display_order == 5
        assert template.is_repeatable == False
    
    def test_action_template_defaults(self, sample_category_id):
        """Test action template default values."""
        minimal_template = ActionTemplatePydantic(
            name="Minimal Action",
            category_id=sample_category_id
        )
        
        # Check all defaults
        assert minimal_template.description == ""
        assert minimal_template.action_verb == "perform"
        assert isinstance(minimal_template.requirements, ActionRequirement)
        assert minimal_template.possible_rewards == []
        assert minimal_template.base_duration_seconds == 60
        assert minimal_template.difficulty_level == 1
        assert minimal_template.max_skill_level is None
        assert minimal_template.icon is None
        assert minimal_template.flavor_text is None
        assert minimal_template.display_order == 0
        assert minimal_template.is_repeatable == True
        assert minimal_template.is_active == True
        assert minimal_template.prerequisite_action_ids == []
        assert minimal_template.unlock_world_day == 0