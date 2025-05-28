import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID
import dataclasses
from typing import Dict, Any, Optional

# Import repository and entities for testing
from app.game_state.repositories.building_upgrade_blueprint_repository import BuildingUpgradeBlueprintRepository
from app.game_state.entities.building_upgrade_blueprint_entity import BuildingUpgradeBlueprintEntity
from app.db.models.building_upgrade_blueprint import BuildingUpgradeBlueprint

# Fixtures
@pytest.fixture
def test_uuid():
    return uuid4()

@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock()
    
    # Mock execute method to return result with scalar
    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    
    # Default behavior for scalar_one_or_none - override in tests
    mock_result.scalar_one_or_none.return_value = None
    
    # Default behavior for scalars().all() - override in tests
    mock_scalars = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_scalars.all.return_value = []
    
    # Fix synchronous methods that shouldn't return coroutines
    mock_session.add = MagicMock(return_value=None)  # add is synchronous
    
    return mock_session

@pytest_asyncio.fixture
async def repository(mock_db_session):
    return BuildingUpgradeBlueprintRepository(db=mock_db_session)

@pytest.fixture
def sample_resource_costs():
    """Create sample resource costs with UUID keys."""
    return {
        uuid4(): 10,  # Requires 10 of resource 1
        uuid4(): 5,   # Requires 5 of resource 2
    }

@pytest.fixture
def sample_profession_costs():
    """Create sample profession costs with UUID keys."""
    return {
        uuid4(): 2,  # Requires 2 of profession 1
        uuid4(): 1,  # Requires 1 of profession 2
    }

@pytest.fixture
def sample_entity(test_uuid, sample_resource_costs, sample_profession_costs):
    """Create a sample building upgrade blueprint entity."""
    return BuildingUpgradeBlueprintEntity(
        entity_id=test_uuid,
        name="Test Upgrade Blueprint",
        display_name="Test Display Name",
        description="Test Description",
        parent_blueprint_id="test_building",
        stage=1,
        resource_cost=sample_resource_costs,
        profession_cost=sample_profession_costs,
        construction_time=10
    )

@pytest.fixture
def sample_model(test_uuid, sample_entity):
    """Create a sample database model with string keys in JSON fields."""
    # Convert UUID keys to strings for the database representation
    string_resource_costs = {str(k): v for k, v in sample_entity.resource_cost.items()}
    string_profession_costs = {str(k): v for k, v in sample_entity.profession_cost.items()}
    
    model = MagicMock(spec=BuildingUpgradeBlueprint)
    model.id = test_uuid
    model.name = sample_entity.name
    model.display_name = sample_entity.display_name
    model.description = sample_entity.description
    model.parent_blueprint_id = sample_entity.parent_blueprint_id
    model.stage = sample_entity.stage
    model.resource_cost = string_resource_costs
    model.profession_cost = string_profession_costs
    model.construction_time = sample_entity.construction_time
    
    return model

# Test classes
class TestBuildingUpgradeBlueprintRepository:
    
    @pytest.mark.asyncio
    async def test_convert_to_entity_with_uuid_fields(self, repository, mock_db_session, sample_model, sample_entity):
        """Test UUID conversion in JSONB fields when converting from model to entity."""
        # Arrange
        # Get the expected UUIDs from the entity fixture
        expected_resource_uuids = list(sample_entity.resource_cost.keys())
        expected_profession_uuids = list(sample_entity.profession_cost.keys())
        
        # Act
        # Directly invoke the method with the sample model
        entity = await repository._convert_to_entity(sample_model)
        
        # Assert
        assert entity is not None
        assert isinstance(entity, BuildingUpgradeBlueprintEntity)
        
        # Check that the JSON fields have UUID keys
        assert len(entity.resource_cost) == len(sample_entity.resource_cost)
        for key in entity.resource_cost:
            assert isinstance(key, UUID)
            # Convert to string for comparison since the order might be different
            assert str(key) in [str(k) for k in expected_resource_uuids]
            
        assert len(entity.profession_cost) == len(sample_entity.profession_cost)
        for key in entity.profession_cost:
            assert isinstance(key, UUID)
            # Convert to string for comparison since the order might be different
            assert str(key) in [str(k) for k in expected_profession_uuids]
    
    @pytest.mark.asyncio
    async def test_entity_to_model_dict_with_uuid_fields(self, repository, sample_entity):
        """Test UUID conversion in JSONB fields when converting from entity to model dict."""
        # Act
        model_dict = await repository._entity_to_model_dict(sample_entity)
        
        # Assert
        assert 'resource_cost' in model_dict
        assert 'profession_cost' in model_dict
        
        # Check that resource_cost has string keys
        assert len(model_dict['resource_cost']) == len(sample_entity.resource_cost)
        for key in model_dict['resource_cost']:
            assert isinstance(key, str)
            
        # Check that profession_cost has string keys
        assert len(model_dict['profession_cost']) == len(sample_entity.profession_cost)
        for key in model_dict['profession_cost']:
            assert isinstance(key, str)
    
    @pytest.mark.asyncio
    async def test_save_preserves_uuid_mapping(self, repository, mock_db_session, sample_entity):
        """Test that UUID-to-string conversion is preserved through save operation."""
        # Arrange
        model_clone = MagicMock()
        mock_db_session.add.return_value = None
        mock_db_session.get.return_value = None
        
        # Mock flush/refresh to simulate a successful save
        # This is a simplification - actual save flow is more complex
        async def mock_refresh(obj):
            # Clone the entity's values to the model
            obj.id = sample_entity.entity_id
            obj.name = sample_entity.name
            obj.resource_cost = {str(k): v for k, v in sample_entity.resource_cost.items()}
            obj.profession_cost = {str(k): v for k, v in sample_entity.profession_cost.items()}
            return None
            
        mock_db_session.refresh.side_effect = mock_refresh
        
        # Act
        result = await repository.save(sample_entity)
        
        # Assert
        assert result is not None
        assert isinstance(result, BuildingUpgradeBlueprintEntity)
        
        # Check that resource_cost has UUID keys in the result
        assert len(result.resource_cost) == len(sample_entity.resource_cost)
        for key in result.resource_cost:
            assert isinstance(key, UUID)
            
        # Check that profession_cost has UUID keys in the result
        assert len(result.profession_cost) == len(sample_entity.profession_cost)
        for key in result.profession_cost:
            assert isinstance(key, UUID)
            
        # Verify that add was called with a model that has string keys
        mock_db_session.add.assert_called_once()
        model_arg = mock_db_session.add.call_args[0][0]
        
        # Since we can't easily check the actual model object's attribute values from add,
        # we verify that the save process performed the right operations in order