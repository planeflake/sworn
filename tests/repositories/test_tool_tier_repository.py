import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from app.game_state.repositories.tool_tier_repository import ToolTierRepository
from app.game_state.entities.core.tool_tier_pydantic import ToolTierPydantic
from app.db.models.tool_tier import ToolTier


class TestToolTierRepository:
    """Test suite for ToolTier repository."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def repository(self, mock_db_session):
        """Create a ToolTierRepository instance with mocked session."""
        return ToolTierRepository(mock_db_session)
    
    @pytest.fixture
    def sample_theme_id(self):
        """Sample theme ID for testing."""
        return uuid4()
    
    @pytest.fixture
    def sample_tool_tier_entity(self, sample_theme_id):
        """Sample tool tier entity for testing."""
        return ToolTierPydantic(
            entity_id=uuid4(),
            name="Steel Tools",
            theme_id=sample_theme_id,
            tier_name="Steel",
            tier_level=3,
            effectiveness_multiplier=1.5,
            description="High-quality steel tools"
        )
    
    @pytest.fixture
    def sample_tool_tier_model(self, sample_theme_id):
        """Sample tool tier model for testing."""
        model = MagicMock(spec=ToolTier)
        model.id = uuid4()
        model.name = "Steel Tools"
        model.theme_id = sample_theme_id
        model.tier_name = "Steel"
        model.tier_level = 3
        model.effectiveness_multiplier = 1.5
        model.description = "High-quality steel tools"
        model.icon = None
        model.required_tech_level = 0
        model.required_materials = []
        model.flavor_text = None
        model.color_hex = None
        model.tags = []
        model.meta_data = {}
        return model
    
    @pytest.mark.asyncio
    async def test_get_by_theme(self, repository, mock_db_session, sample_theme_id, sample_tool_tier_model):
        """Test getting tool tiers by theme."""
        # Setup mock
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_tool_tier_model]
        
        mock_result = AsyncMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        # Mock the model_to_entity conversion
        with patch.object(repository, '_convert_to_entity') as mock_convert:
            mock_entity = ToolTierPydantic(
                entity_id=sample_tool_tier_model.id,
                name=sample_tool_tier_model.name,
                theme_id=sample_tool_tier_model.theme_id,
                tier_name=sample_tool_tier_model.tier_name,
                tier_level=sample_tool_tier_model.tier_level,
                effectiveness_multiplier=sample_tool_tier_model.effectiveness_multiplier
            )
            mock_convert.return_value = mock_entity
            
            # Execute
            result = await repository.get_by_theme(sample_theme_id)
            
            # Verify
            assert len(result) == 1
            assert result[0].theme_id == sample_theme_id
            assert result[0].tier_name == "Steel"
            mock_db_session.execute.assert_called_once()
            mock_convert.assert_called_once_with(sample_tool_tier_model)
    
    @pytest.mark.asyncio
    async def test_get_by_theme_and_level(self, repository, mock_db_session, sample_theme_id, sample_tool_tier_model):
        """Test getting specific tool tier by theme and level."""
        # Setup mock
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = sample_tool_tier_model
        mock_db_session.execute.return_value = mock_result
        
        # Mock the model_to_entity conversion
        with patch.object(repository, '_convert_to_entity') as mock_convert:
            mock_entity = ToolTierPydantic(
                entity_id=sample_tool_tier_model.id,
                name=sample_tool_tier_model.name,
                theme_id=sample_tool_tier_model.theme_id,
                tier_name=sample_tool_tier_model.tier_name,
                tier_level=sample_tool_tier_model.tier_level,
                effectiveness_multiplier=sample_tool_tier_model.effectiveness_multiplier
            )
            mock_convert.return_value = mock_entity
            
            # Execute
            result = await repository.get_by_theme_and_level(sample_theme_id, 3)
            
            # Verify
            assert result is not None
            assert result.tier_level == 3
            assert result.theme_id == sample_theme_id
            mock_db_session.execute.assert_called_once()
            mock_convert.assert_called_once_with(sample_tool_tier_model)
    
    @pytest.mark.asyncio
    async def test_get_by_theme_and_level_not_found(self, repository, mock_db_session, sample_theme_id):
        """Test getting tool tier when none exists."""
        # Setup mock to return None
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Execute
        result = await repository.get_by_theme_and_level(sample_theme_id, 99)
        
        # Verify
        assert result is None
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_progression_for_theme(self, repository, sample_theme_id):
        """Test getting complete progression for theme."""
        # Mock the get_by_theme method since get_progression_for_theme calls it
        with patch.object(repository, 'get_by_theme') as mock_get_by_theme:
            mock_tiers = [
                ToolTierPydantic(
                    entity_id=uuid4(),
                    name="Basic Tools",
                    theme_id=sample_theme_id,
                    tier_name="Basic",
                    tier_level=1,
                    effectiveness_multiplier=1.0
                ),
                ToolTierPydantic(
                    entity_id=uuid4(),
                    name="Steel Tools",
                    theme_id=sample_theme_id,
                    tier_name="Steel",
                    tier_level=3,
                    effectiveness_multiplier=1.5
                )
            ]
            mock_get_by_theme.return_value = mock_tiers
            
            # Execute
            result = await repository.get_progression_for_theme(sample_theme_id)
            
            # Verify
            assert len(result) == 2
            assert result[0].tier_level == 1
            assert result[1].tier_level == 3
            mock_get_by_theme.assert_called_once_with(sample_theme_id)
    
    @pytest.mark.asyncio
    async def test_get_max_tier_for_theme(self, repository, mock_db_session, sample_theme_id, sample_tool_tier_model):
        """Test getting highest tier for theme."""
        # Setup mock for highest tier
        sample_tool_tier_model.tier_level = 6
        sample_tool_tier_model.tier_name = "Legendary"
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = sample_tool_tier_model
        mock_db_session.execute.return_value = mock_result
        
        # Mock the model_to_entity conversion
        with patch.object(repository, '_convert_to_entity') as mock_convert:
            mock_entity = ToolTierPydantic(
                entity_id=sample_tool_tier_model.id,
                name=sample_tool_tier_model.name,
                theme_id=sample_tool_tier_model.theme_id,
                tier_name="Legendary",
                tier_level=6,
                effectiveness_multiplier=sample_tool_tier_model.effectiveness_multiplier
            )
            mock_convert.return_value = mock_entity
            
            # Execute
            result = await repository.get_max_tier_for_theme(sample_theme_id)
            
            # Verify
            assert result is not None
            assert result.tier_level == 6
            assert result.tier_name == "Legendary"
            mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_basic_tier_for_theme(self, repository, sample_theme_id):
        """Test getting basic tier for theme."""
        # Mock the get_by_theme_and_level method
        with patch.object(repository, 'get_by_theme_and_level') as mock_get:
            mock_basic_tier = ToolTierPydantic(
                entity_id=uuid4(),
                name="Basic Tools",
                theme_id=sample_theme_id,
                tier_name="Basic",
                tier_level=1,
                effectiveness_multiplier=1.0
            )
            mock_get.return_value = mock_basic_tier
            
            # Execute
            result = await repository.get_basic_tier_for_theme(sample_theme_id)
            
            # Verify
            assert result is not None
            assert result.tier_level == 1
            assert result.tier_name == "Basic"
            mock_get.assert_called_once_with(sample_theme_id, 1)
    
    @pytest.mark.asyncio
    async def test_get_tiers_by_tech_level(self, repository, mock_db_session, sample_theme_id):
        """Test getting tiers available at specific tech level."""
        # Setup mock models with different tech requirements
        basic_model = MagicMock(spec=ToolTier)
        basic_model.id = uuid4()
        basic_model.tier_level = 1
        basic_model.required_tech_level = 0
        
        steel_model = MagicMock(spec=ToolTier)
        steel_model.id = uuid4()
        steel_model.tier_level = 3
        steel_model.required_tech_level = 2
        
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [basic_model, steel_model]
        mock_db_session.execute.return_value = mock_result
        
        # Mock the model_to_entity conversion
        with patch.object(repository, '_convert_to_entity') as mock_convert:
            mock_convert.side_effect = [
                ToolTierPydantic(
                    entity_id=basic_model.id,
                    name="Basic Tools",
                    theme_id=sample_theme_id,
                    tier_name="Basic",
                    tier_level=1,
                    effectiveness_multiplier=1.0,
                    required_tech_level=0
                ),
                ToolTierPydantic(
                    entity_id=steel_model.id,
                    name="Steel Tools",
                    theme_id=sample_theme_id,
                    tier_name="Steel",
                    tier_level=3,
                    effectiveness_multiplier=1.5,
                    required_tech_level=2
                )
            ]
            
            # Execute - tech level 2 should return both basic and steel
            result = await repository.get_tiers_by_tech_level(sample_theme_id, 2)
            
            # Verify
            assert len(result) == 2
            assert result[0].tier_level == 1  # Basic
            assert result[1].tier_level == 3  # Steel
            mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_repository_error_handling(self, repository, mock_db_session, sample_theme_id):
        """Test repository error handling."""
        # Setup mock to raise exception
        mock_db_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Execute and verify exception is propagated
        with pytest.raises(SQLAlchemyError):
            await repository.get_by_theme(sample_theme_id)