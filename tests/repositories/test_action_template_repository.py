import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from sqlalchemy.exc import SQLAlchemyError

from app.game_state.repositories.action_template_repository import ActionTemplateRepository
from app.game_state.entities.action.action_template_pydantic import ActionTemplatePydantic, ActionRequirement
from app.db.models.action_template import ActionTemplate


class TestActionTemplateRepository:
    """Test suite for ActionTemplate repository."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def repository(self, mock_db_session):
        """Create an ActionTemplateRepository instance with mocked session."""
        return ActionTemplateRepository(mock_db_session)
    
    @pytest.fixture
    def sample_category_id(self):
        return uuid4()
    
    @pytest.fixture
    def sample_skill_id(self):
        return uuid4()
    
    @pytest.fixture
    def sample_location_type_id(self):
        return uuid4()
    
    @pytest.fixture
    def sample_template_entity(self, sample_category_id, sample_skill_id):
        """Sample action template entity for testing."""
        return ActionTemplatePydantic(
            entity_id=uuid4(),
            name="Gather Wood",
            category_id=sample_category_id,
            description="Collect wood from trees",
            action_verb="gather",
            requirements=ActionRequirement(
                skill_id=sample_skill_id,
                skill_level=3
            ),
            base_duration_seconds=30,
            difficulty_level=1,
            is_active=True
        )
    
    @pytest.fixture
    def sample_template_model(self, sample_category_id, sample_skill_id):
        """Sample action template model for testing."""
        model = MagicMock(spec=ActionTemplate)
        model.id = uuid4()
        model.name = "Gather Wood"
        model.category_id = sample_category_id
        model.description = "Collect wood from trees"
        model.action_verb = "gather"
        model.requirements = {
            "skill_id": str(sample_skill_id),
            "skill_level": 3,
            "required_tool_tier_id": None,
            "required_item_ids": [],
            "required_location_type_ids": [],
            "stamina_cost": 0
        }
        model.possible_rewards = []
        model.base_duration_seconds = 30
        model.difficulty_level = 1
        model.max_skill_level = None
        model.icon = None
        model.flavor_text = None
        model.display_order = 0
        model.is_repeatable = True
        model.is_active = True
        model.prerequisite_action_ids = []
        model.unlock_world_day = 0
        model.tags = []
        model.meta_data = {}
        return model
    
    @pytest.mark.asyncio
    async def test_get_by_category(self, repository, mock_db_session, sample_category_id, sample_template_model):
        """Test getting action templates by category."""
        # Setup mock
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [sample_template_model]
        mock_db_session.execute.return_value = mock_result
        
        # Mock the model_to_entity conversion
        with patch.object(repository, 'model_to_entity') as mock_convert:
            mock_entity = ActionTemplatePydantic(
                entity_id=sample_template_model.id,
                name=sample_template_model.name,
                category_id=sample_template_model.category_id,
                description=sample_template_model.description,
                action_verb=sample_template_model.action_verb,
                base_duration_seconds=sample_template_model.base_duration_seconds,
                difficulty_level=sample_template_model.difficulty_level
            )
            mock_convert.return_value = mock_entity
            
            # Execute
            result = await repository.get_by_category(sample_category_id)
            
            # Verify
            assert len(result) == 1
            assert result[0].name == "Gather Wood"
            assert result[0].category_id == sample_category_id
            mock_db_session.execute.assert_called_once()
            mock_convert.assert_called_once_with(sample_template_model)
    
    @pytest.mark.asyncio
    async def test_get_templates_requiring_skill(self, repository, mock_db_session, sample_skill_id, sample_template_model):
        """Test getting templates that require a specific skill."""
        # Setup mock to return all templates
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [sample_template_model]
        mock_db_session.execute.return_value = mock_result
        
        # Mock the model_to_entity conversion
        with patch.object(repository, 'model_to_entity') as mock_convert:
            mock_entity = ActionTemplatePydantic(
                entity_id=sample_template_model.id,
                name=sample_template_model.name,
                category_id=sample_template_model.category_id,
                requirements=ActionRequirement(
                    skill_id=sample_skill_id,
                    skill_level=3
                )
            )
            mock_convert.return_value = mock_entity
            
            # Execute
            result = await repository.get_templates_requiring_skill(sample_skill_id)
            
            # Verify
            assert len(result) == 1
            assert result[0].requirements.skill_id == sample_skill_id
            mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_available_for_character_no_requirements(self, repository, mock_db_session, sample_location_type_id, sample_template_model):
        """Test getting available actions for character with no special requirements."""
        # Setup template with no requirements
        sample_template_model.requirements = {
            "skill_id": None,
            "skill_level": 0,
            "required_tool_tier_id": None,
            "required_item_ids": [],
            "required_location_type_ids": [],
            "stamina_cost": 0
        }
        
        # Setup mock
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [sample_template_model]
        mock_db_session.execute.return_value = mock_result
        
        # Mock the model_to_entity conversion
        with patch.object(repository, 'model_to_entity') as mock_convert:
            mock_entity = ActionTemplatePydantic(
                entity_id=sample_template_model.id,
                name="Basic Action",
                category_id=sample_template_model.category_id,
                requirements=ActionRequirement()  # No requirements
            )
            mock_convert.return_value = mock_entity
            
            # Execute
            result = await repository.get_available_for_character(
                location_type_id=sample_location_type_id,
                character_skills={},
                available_tool_tier=None
            )
            
            # Verify - should return the template since no requirements
            assert len(result) == 1
            assert result[0].name == "Basic Action"
    
    @pytest.mark.asyncio
    async def test_get_available_for_character_with_skill_requirements(self, repository, mock_db_session, sample_location_type_id, sample_skill_id, sample_template_model):
        """Test getting available actions with skill requirements."""
        # Setup template with skill requirement
        sample_template_model.requirements = {
            "skill_id": str(sample_skill_id),
            "skill_level": 5,
            "required_tool_tier_id": None,
            "required_item_ids": [],
            "required_location_type_ids": [],
            "stamina_cost": 0
        }
        
        # Setup mock
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [sample_template_model]
        mock_db_session.execute.return_value = mock_result
        
        # Mock the model_to_entity conversion
        with patch.object(repository, 'model_to_entity') as mock_convert:
            mock_entity = ActionTemplatePydantic(
                entity_id=sample_template_model.id,
                name="Skilled Action",
                category_id=sample_template_model.category_id,
                requirements=ActionRequirement(
                    skill_id=sample_skill_id,
                    skill_level=5
                )
            )
            mock_convert.return_value = mock_entity
            
            # Execute with insufficient skill
            result_insufficient = await repository.get_available_for_character(
                location_type_id=sample_location_type_id,
                character_skills={sample_skill_id: 3},  # Only level 3
                available_tool_tier=None
            )
            
            # Execute with sufficient skill
            result_sufficient = await repository.get_available_for_character(
                location_type_id=sample_location_type_id,
                character_skills={sample_skill_id: 7},  # Level 7
                available_tool_tier=None
            )
            
            # Verify
            assert len(result_insufficient) == 0  # Doesn't meet requirement
            assert len(result_sufficient) == 1   # Meets requirement
            assert result_sufficient[0].name == "Skilled Action"
    
    @pytest.mark.asyncio
    async def test_get_available_for_character_with_location_requirements(self, repository, mock_db_session, sample_location_type_id, sample_template_model):
        """Test getting available actions with location requirements."""
        required_location_id = uuid4()
        different_location_id = uuid4()
        
        # Setup template with location requirement
        sample_template_model.requirements = {
            "skill_id": None,
            "skill_level": 0,
            "required_tool_tier_id": None,
            "required_item_ids": [],
            "required_location_type_ids": [str(required_location_id)],
            "stamina_cost": 0
        }
        
        # Setup mock
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [sample_template_model]
        mock_db_session.execute.return_value = mock_result
        
        # Mock the model_to_entity conversion
        with patch.object(repository, 'model_to_entity') as mock_convert:
            mock_entity = ActionTemplatePydantic(
                entity_id=sample_template_model.id,
                name="Location Specific Action",
                category_id=sample_template_model.category_id,
                requirements=ActionRequirement(
                    required_location_type_ids=[required_location_id]
                )
            )
            mock_convert.return_value = mock_entity
            
            # Execute with wrong location
            result_wrong = await repository.get_available_for_character(
                location_type_id=different_location_id,
                character_skills={},
                available_tool_tier=None
            )
            
            # Execute with correct location
            result_correct = await repository.get_available_for_character(
                location_type_id=required_location_id,
                character_skills={},
                available_tool_tier=None
            )
            
            # Verify
            assert len(result_wrong) == 0    # Wrong location
            assert len(result_correct) == 1  # Correct location
    
    @pytest.mark.asyncio
    async def test_can_character_perform_method(self, repository, sample_location_type_id, sample_skill_id):
        """Test the _can_character_perform helper method."""
        # Create template with multiple requirements
        template = ActionTemplatePydantic(
            name="Complex Action",
            category_id=uuid4(),
            requirements=ActionRequirement(
                skill_id=sample_skill_id,
                skill_level=5,
                required_location_type_ids=[sample_location_type_id]
            )
        )
        
        # Test all requirements met
        can_perform_all = repository._can_character_perform(
            template=template,
            location_type_id=sample_location_type_id,
            character_skills={sample_skill_id: 7},
            available_tool_tier=None
        )
        assert can_perform_all == True
        
        # Test location requirement not met
        can_perform_location = repository._can_character_perform(
            template=template,
            location_type_id=uuid4(),  # Different location
            character_skills={sample_skill_id: 7},
            available_tool_tier=None
        )
        assert can_perform_location == False
        
        # Test skill requirement not met
        can_perform_skill = repository._can_character_perform(
            template=template,
            location_type_id=sample_location_type_id,
            character_skills={sample_skill_id: 3},  # Too low
            available_tool_tier=None
        )
        assert can_perform_skill == False
        
        # Test missing skill entirely
        can_perform_no_skill = repository._can_character_perform(
            template=template,
            location_type_id=sample_location_type_id,
            character_skills={},  # No skills
            available_tool_tier=None
        )
        assert can_perform_no_skill == False
    
    @pytest.mark.asyncio
    async def test_repository_inheritance(self, repository):
        """Test that repository properly inherits BaseRepository methods."""
        # The ActionTemplateRepository should have all BaseRepository methods
        assert hasattr(repository, 'create')
        assert hasattr(repository, 'get_by_id')
        assert hasattr(repository, 'get_all')
        assert hasattr(repository, 'update')
        assert hasattr(repository, 'delete')
        assert hasattr(repository, 'model_to_entity')
        assert hasattr(repository, 'entity_to_model')
    
    @pytest.mark.asyncio
    async def test_repository_error_handling(self, repository, mock_db_session, sample_category_id):
        """Test repository error handling."""
        # Setup mock to raise exception
        mock_db_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Execute and verify exception is propagated
        with pytest.raises(SQLAlchemyError):
            await repository.get_by_category(sample_category_id)