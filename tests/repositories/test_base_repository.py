import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID
import dataclasses
from typing import Dict, Any, Optional, List
from sqlalchemy.exc import SQLAlchemyError

# Import the BaseRepository and required components
from app.game_state.repositories.base_repository import BaseRepository
from app.game_state.entities.base import BaseEntity
from app.db.async_session import AsyncSession
from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.ext.declarative import declarative_base

# Create test models and entities for testing
Base = declarative_base()

# Test model for SQLAlchemy
class TestModel(Base):
    __tablename__ = 'test_models'
    
    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    json_data = Column(JSON, nullable=True)

# Test entity for the domain
@dataclasses.dataclass
class TestEntity(BaseEntity):
    name: str
    json_data: Dict[UUID, int] = dataclasses.field(default_factory=dict)

# Concrete repository implementation for testing
class TestRepository(BaseRepository[TestEntity, TestModel, UUID]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model_cls=TestModel, entity_cls=TestEntity)

# Fixtures
@pytest.fixture
def test_uuid():
    return uuid4()

@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock(spec=AsyncSession)
    
    # Mock execute method to return result with scalar
    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    
    # Default behavior for scalar_one_or_none - override in tests
    mock_result.scalar_one_or_none.return_value = None
    
    # Default behavior for scalars().all() - override in tests
    mock_scalars = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_scalars.all.return_value = []
    
    return mock_session

@pytest_asyncio.fixture
async def repository(mock_db_session):
    return TestRepository(db=mock_db_session)

@pytest.fixture
def sample_entity(test_uuid):
    resource_uuid = uuid4()
    return TestEntity(
        entity_id=test_uuid,
        name="Test Entity",
        json_data={resource_uuid: 10}
    )

@pytest.fixture
def sample_model(test_uuid, sample_entity):
    model = TestModel(
        id=test_uuid,
        name=sample_entity.name,
        json_data={str(k): v for k, v in sample_entity.json_data.items()}
    )
    return model

# Test classes
class TestEntityToModelDict:
    @pytest.mark.asyncio
    async def test_entity_to_model_dict_basic(self, repository, sample_entity):
        """Test conversion from entity to model dict with basic fields."""
        # Act
        result = await repository._entity_to_model_dict(sample_entity)
        
        # Assert
        assert 'name' in result
        assert result['name'] == sample_entity.name
        assert 'id' in result
        assert result['id'] == sample_entity.entity_id
    
    @pytest.mark.asyncio
    async def test_entity_to_model_dict_uuid_conversion(self, repository, sample_entity):
        """Test conversion handles UUID keys in dict fields."""
        # Get a UUID key from the entity's json_data
        uuid_key = next(iter(sample_entity.json_data.keys()))
        
        # Act
        result = await repository._entity_to_model_dict(sample_entity)
        
        # Assert
        assert 'json_data' in result
        assert isinstance(result['json_data'], dict)
        
        # The UUID key should be converted to string
        assert str(uuid_key) in result['json_data']
        assert isinstance(next(iter(result['json_data'].keys())), str)
        assert result['json_data'][str(uuid_key)] == sample_entity.json_data[uuid_key]

class TestConvertToEntity:
    @pytest.mark.asyncio
    async def test_convert_to_entity_basic(self, repository, sample_model):
        """Test conversion from model to entity with basic fields."""
        # Act
        result = await repository._convert_to_entity(sample_model)
        
        # Assert
        assert result is not None
        assert isinstance(result, TestEntity)
        assert result.name == sample_model.name
        assert result.entity_id == sample_model.id
    
    @pytest.mark.asyncio
    async def test_convert_to_entity_uuid_conversion(self, repository, sample_model):
        """Test conversion handles string keys in JSON fields to UUID keys."""
        # Get a string key from the model's json_data
        str_key = next(iter(sample_model.json_data.keys()))
        
        # Act
        result = await repository._convert_to_entity(sample_model)
        
        # Assert
        assert hasattr(result, 'json_data')
        assert isinstance(result.json_data, dict)
        
        # The string key should be converted to UUID
        uuid_key = UUID(str_key)
        assert uuid_key in result.json_data
        assert isinstance(next(iter(result.json_data.keys())), UUID)
        assert result.json_data[uuid_key] == sample_model.json_data[str_key]

class TestFindByName:
    @pytest.mark.asyncio
    async def test_find_by_name_found(self, repository, mock_db_session, sample_model, sample_entity):
        """Test find_by_name returns entity when found."""
        # Arrange
        mock_result = mock_db_session.execute.return_value
        mock_result.scalar_one_or_none.return_value = sample_model
        
        # Act
        result = await repository.find_by_name("Test Entity")
        
        # Assert
        assert result is not None
        assert isinstance(result, TestEntity)
        assert result.name == sample_entity.name
        assert result.entity_id == sample_entity.entity_id
    
    @pytest.mark.asyncio
    async def test_find_by_name_not_found(self, repository, mock_db_session):
        """Test find_by_name returns None when not found."""
        # Arrange
        mock_result = mock_db_session.execute.return_value
        mock_result.scalar_one_or_none.return_value = None
        
        # Act
        result = await repository.find_by_name("Non-existent Entity")
        
        # Assert
        assert result is None

class TestFindByNameInsensitive:
    @pytest.mark.asyncio
    async def test_find_by_name_insensitive_found(self, repository, mock_db_session, sample_model, sample_entity):
        """Test find_by_name_insensitive returns entity with case-insensitive search."""
        # Arrange
        mock_result = mock_db_session.execute.return_value
        mock_result.scalar_one_or_none.return_value = sample_model
        
        # Act
        result = await repository.find_by_name_insensitive("test entity")  # Mixed case
        
        # Assert
        assert result is not None
        assert isinstance(result, TestEntity)
        assert result.name == sample_entity.name
        
        # Verify that the query used func.lower() for case-insensitive search
        call_args = mock_db_session.execute.call_args[0][0]
        # This is a simplified check - the actual query is more complex
        assert "func.lower" in str(call_args) or "LOWER" in str(call_args)

class TestFindAllByName:
    @pytest.mark.asyncio
    async def test_find_all_by_name_partial_match(self, repository, mock_db_session, sample_model, sample_entity):
        """Test find_all_by_name returns matching entities with partial match."""
        # Arrange
        mock_result = mock_db_session.execute.return_value
        mock_scalars = mock_result.scalars.return_value
        mock_scalars.all.return_value = [sample_model]
        
        # Act
        result = await repository.find_all_by_name("Test", partial_match=True)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TestEntity)
        assert result[0].name == sample_entity.name
        
        # Verify LIKE query was used for partial matching
        call_args = mock_db_session.execute.call_args[0][0]
        assert "ilike" in str(call_args).lower() or "like" in str(call_args).lower()

class TestBulkOperations:
    @pytest.mark.asyncio
    async def test_bulk_save_new_entities(self, repository, mock_db_session, sample_entity):
        """Test bulk_save handles new entities correctly."""
        # Arrange
        entities = [
            sample_entity,
            TestEntity(name="Entity 2", json_data={uuid4(): 20}),
            TestEntity(name="Entity 3", json_data={uuid4(): 30})
        ]
        
        # Mock DB objects that would be returned after save
        saved_models = []
        for i, entity in enumerate(entities):
            model = TestModel(
                id=entity.entity_id or uuid4(),
                name=entity.name,
                json_data={str(k): v for k, v in entity.json_data.items()}
            )
            saved_models.append(model)
        
        # Setup mock to return the saved models after flush
        def add_side_effect(obj):
            # Simulate adding to session - indexes into saved_models
            index = next((i for i, e in enumerate(entities) if e.name == obj.name), 0)
            obj.id = saved_models[index].id
            
        mock_db_session.add.side_effect = add_side_effect
        
        # Act
        results = await repository.bulk_save(entities)
        
        # Assert
        assert len(results) == len(entities)
        assert all(isinstance(entity, TestEntity) for entity in results)
        assert mock_db_session.add.call_count == len(entities)
        assert mock_db_session.flush.await_count == 1
    
    @pytest.mark.asyncio
    async def test_bulk_delete(self, repository, mock_db_session):
        """Test bulk_delete removes multiple entities."""
        # Arrange
        ids_to_delete = [uuid4(), uuid4(), uuid4()]
        mock_result = mock_db_session.execute.return_value
        mock_result.rowcount = len(ids_to_delete)  # All deleted successfully
        
        # Act
        result = await repository.bulk_delete(ids_to_delete)
        
        # Assert
        assert result == len(ids_to_delete)
        assert mock_db_session.execute.await_count == 1
        # Verify the query contains an IN clause with the IDs
        call_args = mock_db_session.execute.call_args[0][0]
        assert "IN" in str(call_args) or "in_" in str(call_args)
        # Flush should be called to commit the deletion
        assert mock_db_session.flush.await_count == 1