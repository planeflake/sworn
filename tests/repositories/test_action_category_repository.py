import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from sqlalchemy.exc import SQLAlchemyError

from app.game_state.repositories.action_category_repository import ActionCategoryRepository
from app.game_state.entities.action.action_category_pydantic import ActionCategoryPydantic
from app.db.models.action_category import ActionCategory


class TestActionCategoryRepository:
    """Test suite for ActionCategory repository."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def repository(self, mock_db_session):
        """Create an ActionCategoryRepository instance with mocked session."""
        return ActionCategoryRepository(mock_db_session)
    
    @pytest.fixture
    def sample_category_entity(self):
        """Sample action category entity for testing."""
        return ActionCategoryPydantic(
            entity_id=uuid4(),
            name="Gathering",
            description="Resource collection actions",
            icon="🌳",
            display_order=1,
            is_active=True
        )
    
    @pytest.fixture
    def sample_category_model(self):
        """Sample action category model for testing."""
        model = MagicMock(spec=ActionCategory)
        model.id = uuid4()
        model.name = "Gathering"
        model.parent_category_id = None
        model.description = "Resource collection actions"
        model.icon = "🌳"
        model.display_order = 1
        model.is_active = True
        model.tags = []
        model.meta_data = {}
        return model
    
    @pytest.mark.asyncio
    async def test_get_root_categories(self, repository, mock_db_session, sample_category_model):
        """Test getting root categories (no parent)."""
        # Setup mock
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [sample_category_model]
        mock_db_session.execute.return_value = mock_result
        
        # Mock the model_to_entity conversion
        with patch.object(repository, 'model_to_entity') as mock_convert:
            mock_entity = ActionCategoryPydantic(
                entity_id=sample_category_model.id,
                name=sample_category_model.name,
                description=sample_category_model.description,
                icon=sample_category_model.icon,
                display_order=sample_category_model.display_order,
                is_active=sample_category_model.is_active
            )
            mock_convert.return_value = mock_entity
            
            # Execute
            result = await repository.get_root_categories()
            
            # Verify
            assert len(result) == 1
            assert result[0].name == "Gathering"
            assert result[0].parent_category_id is None
            mock_db_session.execute.assert_called_once()
            mock_convert.assert_called_once_with(sample_category_model)
    
    @pytest.mark.asyncio
    async def test_get_children_of_category(self, repository, mock_db_session, sample_category_model):
        """Test getting child categories of a parent."""
        parent_id = uuid4()
        
        # Setup child category model
        child_model = MagicMock(spec=ActionCategory)
        child_model.id = uuid4()
        child_model.name = "Mining"
        child_model.parent_category_id = parent_id
        child_model.description = "Extracting ores"
        child_model.icon = "⛏️"
        child_model.display_order = 1
        child_model.is_active = True
        child_model.tags = []
        child_model.meta_data = {}
        
        # Setup mock
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [child_model]
        mock_db_session.execute.return_value = mock_result
        
        # Mock the model_to_entity conversion
        with patch.object(repository, 'model_to_entity') as mock_convert:
            mock_entity = ActionCategoryPydantic(
                entity_id=child_model.id,
                name=child_model.name,
                parent_category_id=parent_id,
                description=child_model.description,
                icon=child_model.icon,
                display_order=child_model.display_order,
                is_active=child_model.is_active
            )
            mock_convert.return_value = mock_entity
            
            # Execute
            result = await repository.get_children_of_category(parent_id)
            
            # Verify
            assert len(result) == 1
            assert result[0].name == "Mining"
            assert result[0].parent_category_id == parent_id
            mock_db_session.execute.assert_called_once()
            mock_convert.assert_called_once_with(child_model)
    
    @pytest.mark.asyncio
    async def test_get_category_with_children(self, repository, mock_db_session):
        """Test getting category with its children populated."""
        category_id = uuid4()
        
        # Mock the get_by_id method
        with patch.object(repository, 'get_by_id') as mock_get_by_id:
            parent_category = ActionCategoryPydantic(
                entity_id=category_id,
                name="Gathering",
                description="Resource collection"
            )
            mock_get_by_id.return_value = parent_category
            
            # Mock the get_children_of_category method
            with patch.object(repository, 'get_children_of_category') as mock_get_children:
                child_categories = [
                    ActionCategoryPydantic(
                        entity_id=uuid4(),
                        name="Mining",
                        parent_category_id=category_id,
                        description="Extracting ores"
                    ),
                    ActionCategoryPydantic(
                        entity_id=uuid4(),
                        name="Logging",
                        parent_category_id=category_id,
                        description="Cutting trees"
                    )
                ]
                mock_get_children.return_value = child_categories
                
                # Execute
                result = await repository.get_category_with_children(category_id)
                
                # Verify
                assert result is not None
                assert result.name == "Gathering"
                assert len(result.child_categories) == 2
                assert result.child_categories[0].name == "Mining"
                assert result.child_categories[1].name == "Logging"
                
                mock_get_by_id.assert_called_once_with(category_id)
                mock_get_children.assert_called_once_with(category_id)
    
    @pytest.mark.asyncio
    async def test_get_category_with_children_not_found(self, repository):
        """Test getting category with children when category doesn't exist."""
        category_id = uuid4()
        
        # Mock the get_by_id method to return None
        with patch.object(repository, 'get_by_id') as mock_get_by_id:
            mock_get_by_id.return_value = None
            
            # Execute
            result = await repository.get_category_with_children(category_id)
            
            # Verify
            assert result is None
            mock_get_by_id.assert_called_once_with(category_id)
    
    @pytest.mark.asyncio
    async def test_get_children_of_category_empty(self, repository, mock_db_session):
        """Test getting children when category has no children."""
        parent_id = uuid4()
        
        # Setup mock to return empty list
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        # Execute
        result = await repository.get_children_of_category(parent_id)
        
        # Verify
        assert len(result) == 0
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_repository_inheritance(self, repository):
        """Test that repository properly inherits BaseRepository methods."""
        # The ActionCategoryRepository should have all BaseRepository methods
        assert hasattr(repository, 'create')
        assert hasattr(repository, 'get_by_id')
        assert hasattr(repository, 'get_all')
        assert hasattr(repository, 'update')
        assert hasattr(repository, 'delete')
        assert hasattr(repository, 'model_to_entity')
        assert hasattr(repository, 'entity_to_model')
    
    @pytest.mark.asyncio
    async def test_multiple_root_categories(self, repository, mock_db_session):
        """Test getting multiple root categories."""
        # Setup multiple root category models
        model1 = MagicMock(spec=ActionCategory)
        model1.id = uuid4()
        model1.name = "Gathering"
        model1.parent_category_id = None
        model1.display_order = 1
        
        model2 = MagicMock(spec=ActionCategory)
        model2.id = uuid4()
        model2.name = "Crafting"
        model2.parent_category_id = None
        model2.display_order = 2
        
        # Setup mock
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [model1, model2]
        mock_db_session.execute.return_value = mock_result
        
        # Mock the model_to_entity conversion
        with patch.object(repository, 'model_to_entity') as mock_convert:
            mock_convert.side_effect = [
                ActionCategoryPydantic(
                    entity_id=model1.id,
                    name="Gathering",
                    display_order=1
                ),
                ActionCategoryPydantic(
                    entity_id=model2.id,
                    name="Crafting",
                    display_order=2
                )
            ]
            
            # Execute
            result = await repository.get_root_categories()
            
            # Verify
            assert len(result) == 2
            assert result[0].name == "Gathering"
            assert result[1].name == "Crafting"
    
    @pytest.mark.asyncio
    async def test_repository_error_handling(self, repository, mock_db_session):
        """Test repository error handling."""
        # Setup mock to raise exception
        mock_db_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Execute and verify exception is propagated
        with pytest.raises(SQLAlchemyError):
            await repository.get_root_categories()