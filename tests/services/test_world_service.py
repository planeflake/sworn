import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch # Use AsyncMock for async methods
from uuid import uuid4, UUID
import dataclasses

# Imports for the code being tested
from app.game_state.services.world_service import WorldService
from app.game_state.entities.world import World as WorldDomainEntity
from app.game_state.models.world import WorldEntity as WorldApiModel # Assuming this is your Pydantic model
# Import dependencies that need mocking
from app.game_state.repositories.world_repository import WorldRepository
from app.game_state.services.theme_service import ThemeService
from app.game_state.managers.world_manager import WorldManager

# Use pytest-asyncio for async tests
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_db_session():
    """Fixture for a mocked async database session."""
    # WorldService mainly passes the session to repositories/other services
    # So, a simple MagicMock might suffice unless methods are called directly on it.
    return MagicMock() # Or AsyncMock if service calls session methods directly

@pytest_asyncio.fixture
async def world_service(mock_db_session):
    """Fixture to provide a WorldService instance with mocked dependencies."""
    # Patch the dependencies *before* WorldService is instantiated
    with patch('app.game_state.services.world_service.WorldRepository', new_callable=AsyncMock) as MockWorldRepo, \
         patch('app.game_state.services.world_service.ThemeService', new_callable=AsyncMock) as MockThemeService, \
         patch('app.game_state.services.world_service.WorldManager', new_callable=MagicMock) as MockWorldManager: # Use MagicMock if manager methods are synchronous

        # Instantiate the service - it will use the mocked classes
        service = WorldService(db=mock_db_session)
        
        # Store mocks on the service instance for easy access in tests, or return them
        service.mock_repository = MockWorldRepo.return_value # Access the instance
        service.mock_theme_service = MockThemeService.return_value # Access the instance
        service.mock_world_manager = MockWorldManager # Access the static/class mock
        
        yield service # Provide the service instance to the test

# --- Test Data ---
@pytest.fixture
def sample_world_domain():
    """Sample World Domain Entity."""
    return WorldDomainEntity(
        id=uuid4(),
        name="Testopia",
        theme_id=uuid4(),
        game_day=10
    )

@pytest.fixture
def sample_world_api(sample_world_domain):
    """Sample World API Model corresponding to sample_world_domain."""
    # Ensure this conversion matches the logic in _convert_domain_to_api
    return WorldApiModel(
        id=sample_world_domain.id,
        name=sample_world_domain.name,
        theme_id=sample_world_domain.theme_id,
        game_day=sample_world_domain.game_day
        # Add other fields as necessary
    )

# --- Tests ---

class TestGetWorld:
    async def test_get_world_found(self, world_service, sample_world_domain, sample_world_api):
        """Test get_world when the world exists."""
        # Arrange
        test_id = sample_world_domain.id
        world_service.mock_repository.find_by_id.return_value = sample_world_domain
        
        # Act
        result = await world_service.get_world(test_id)
        
        # Assert
        world_service.mock_repository.find_by_id.assert_awaited_once_with(test_id)
        assert result is not None
        assert isinstance(result, WorldApiModel)
        assert result.id == sample_world_domain.id
        assert result.name == sample_world_domain.name
        assert result.theme_id == sample_world_domain.theme_id
        assert result.game_day == sample_world_domain.game_day

    async def test_get_world_not_found(self, world_service):
        """Test get_world when the world does not exist."""
        # Arrange
        test_id = uuid4()
        world_service.mock_repository.find_by_id.return_value = None
        
        # Act
        result = await world_service.get_world(test_id)
        
        # Assert
        world_service.mock_repository.find_by_id.assert_awaited_once_with(test_id)
        assert result is None

class TestGetAllWorlds:
     async def test_get_all_worlds_returns_list(self, world_service, sample_world_domain, sample_world_api):
        """Test get_all_worlds returns a list of API models."""
        # Arrange
        domain_worlds = [sample_world_domain, dataclasses.replace(sample_world_domain, id=uuid4(), name="Another World")]
        world_service.mock_repository.find_all.return_value = domain_worlds
        
        # Act
        results = await world_service.get_all_worlds(skip=0, limit=10)
        
        # Assert
        world_service.mock_repository.find_all.assert_awaited_once_with(skip=0, limit=10)
        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(w, WorldApiModel) for w in results)
        assert results[0].id == domain_worlds[0].id
        assert results[1].id == domain_worlds[1].id

     async def test_get_all_worlds_empty(self, world_service):
        """Test get_all_worlds when no worlds exist."""
        # Arrange
        world_service.mock_repository.find_all.return_value = []
        
        # Act
        results = await world_service.get_all_worlds(skip=0, limit=10)
        
        # Assert
        world_service.mock_repository.find_all.assert_awaited_once_with(skip=0, limit=10)
        assert results == []

class TestCreateWorld:
    async def test_create_world_success(self, world_service, sample_world_domain, sample_world_api):
        """Test successful world creation."""
        # Arrange
        theme_id = uuid4()
        world_name = "NewWorld"
        
        # Mock the domain entity that WorldManager *would* create (without theme_id initially)
        manager_created_domain = WorldDomainEntity(name=world_name, theme_id=None) # ID generated by factory
        
        # Mock the domain entity *after* theme_id is assigned and it's saved (it now has an ID and theme_id)
        saved_domain = dataclasses.replace(manager_created_domain, id=uuid4(), theme_id=theme_id)

        world_service.mock_theme_service.exists.return_value = True
        world_service.mock_world_manager.create_world.return_value = manager_created_domain # Return the one without theme_id yet
        world_service.mock_repository.save.return_value = saved_domain # Return the saved one with ID/theme

        # Patch the converter to ensure it behaves as expected for this test
        with patch.object(WorldService, '_convert_domain_to_api', return_value=sample_world_api) as mock_converter:
             mock_converter.return_value = WorldApiModel(**dataclasses.asdict(saved_domain)) # Use the *saved* data

             # Act
             result = await world_service.create_world(name=world_name, theme_id=theme_id)

        # Assert
        world_service.mock_theme_service.exists.assert_awaited_once_with(theme_id)
        world_service.mock_world_manager.create_world.assert_awaited_once_with(name=world_name)
        
        # Check the object passed to save had the theme_id assigned
        call_args, _ = world_service.mock_repository.save.call_args
        saved_object = call_args[0]
        assert isinstance(saved_object, WorldDomainEntity)
        assert saved_object.name == world_name
        assert saved_object.theme_id == theme_id # Crucial check
        
        world_service.mock_repository.save.assert_awaited_once()
        mock_converter.assert_called_once_with(saved_domain) # Converter called with saved entity

        assert result is not None
        assert isinstance(result, WorldApiModel)
        assert result.id == saved_domain.id
        assert result.name == saved_domain.name
        assert result.theme_id == saved_domain.theme_id
        
    async def test_create_world_theme_not_found(self, world_service):
        """Test world creation fails if theme doesn't exist."""
        # Arrange
        theme_id = uuid4()
        world_name = "NoThemeWorld"
        world_service.mock_theme_service.exists.return_value = False
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Theme ID not found: {theme_id}"):
            await world_service.create_world(name=world_name, theme_id=theme_id)
            
        world_service.mock_theme_service.exists.assert_awaited_once_with(theme_id)
        world_service.mock_world_manager.create_world.assert_not_awaited()
        world_service.mock_repository.save.assert_not_awaited()

    async def test_create_world_manager_fails(self, world_service):
        """Test world creation fails if WorldManager returns None."""
        # Arrange
        theme_id = uuid4()
        world_name = "ManagerFailWorld"
        world_service.mock_theme_service.exists.return_value = True
        world_service.mock_world_manager.create_world.return_value = None # Simulate manager failure

        # Act & Assert
        # The current code raises AttributeError when trying to set theme_id on None
        with pytest.raises(AttributeError):
             await world_service.create_world(name=world_name, theme_id=theme_id)

        world_service.mock_theme_service.exists.assert_awaited_once_with(theme_id)
        world_service.mock_world_manager.create_world.assert_awaited_once_with(name=world_name)
        world_service.mock_repository.save.assert_not_awaited()

    async def test_create_world_repo_save_fails(self, world_service, sample_world_domain):
         """Test world creation fails if repository save raises an error."""
         # Arrange
         theme_id = uuid4()
         world_name = "RepoFailWorld"
         manager_created_domain = WorldDomainEntity(name=world_name, theme_id=None)
         
         world_service.mock_theme_service.exists.return_value = True
         world_service.mock_world_manager.create_world.return_value = manager_created_domain
         world_service.mock_repository.save.side_effect = ValueError("DB connection error") # Simulate DB error

         # Act & Assert
         with pytest.raises(ValueError, match="Database error creating world"):
             await world_service.create_world(name=world_name, theme_id=theme_id)

         world_service.mock_repository.save.assert_awaited_once() # Save was attempted

class TestDeleteWorld:
     async def test_delete_world_success(self, world_service):
        """Test successful world deletion."""
        # Arrange
        test_id = uuid4()
        world_service.mock_repository.delete.return_value = True
        
        # Act
        result = await world_service.delete_world(test_id)
        
        # Assert
        world_service.mock_repository.delete.assert_awaited_once_with(test_id)
        assert result is True

     async def test_delete_world_failure(self, world_service):
        """Test failed world deletion (e.g., not found)."""
        # Arrange
        test_id = uuid4()
        world_service.mock_repository.delete.return_value = False
        
        # Act
        result = await world_service.delete_world(test_id)
        
        # Assert
        world_service.mock_repository.delete.assert_awaited_once_with(test_id)
        assert result is False
        
     async def test_delete_world_exception(self, world_service):
          """Test world deletion handles repository exceptions."""
          # Arrange
          test_id = uuid4()
          world_service.mock_repository.delete.side_effect = Exception("Database error during delete")
          
          # Act
          result = await world_service.delete_world(test_id)
          
          # Assert
          world_service.mock_repository.delete.assert_awaited_once_with(test_id)
          assert result is False # Service currently catches exception and returns False

class TestAdvanceGameDay:
     async def test_advance_day_success(self, world_service, sample_world_domain):
        """Test successfully advancing the game day."""
        # Arrange
        test_id = sample_world_domain.id
        
        # Simulate the state *after* increment_day and save
        updated_domain = dataclasses.replace(sample_world_domain, game_day=sample_world_domain.game_day + 1)
        updated_api = WorldApiModel(**dataclasses.asdict(updated_domain))

        world_service.mock_repository.find_by_id.return_value = sample_world_domain
        # Mock increment_day directly on the manager instance
        world_service.mock_world_manager.increment_day.return_value = updated_domain
        world_service.mock_repository.save.return_value = updated_domain
        
        # Patch converter for this test
        with patch.object(WorldService, '_convert_domain_to_api', return_value=updated_api):
             # Act
             result = await world_service.advance_game_day(test_id)

        # Assert
        world_service.mock_repository.find_by_id.assert_awaited_once_with(test_id)
        # Check that increment_day was called with the *original* domain object
        world_service.mock_world_manager.increment_day.assert_called_once_with(sample_world_domain)
        # Check that save was called with the *updated* domain object
        world_service.mock_repository.save.assert_awaited_once_with(updated_domain)
        
        assert result is not None
        assert result.id == updated_domain.id
        assert result.game_day == updated_domain.game_day

     async def test_advance_day_world_not_found(self, world_service):
         """Test advancing day fails if world not found."""
         # Arrange
         test_id = uuid4()
         world_service.mock_repository.find_by_id.return_value = None

         # Act
         result = await world_service.advance_game_day(test_id)

         # Assert
         world_service.mock_repository.find_by_id.assert_awaited_once_with(test_id)
         assert result is None
         world_service.mock_world_manager.increment_day.assert_not_called()
         world_service.mock_repository.save.assert_not_awaited()

     async def test_advance_day_save_fails(self, world_service, sample_world_domain):
         """Test advancing day returns None if save fails."""
         # Arrange
         test_id = sample_world_domain.id
         updated_domain = dataclasses.replace(sample_world_domain, game_day=sample_world_domain.game_day + 1)

         world_service.mock_repository.find_by_id.return_value = sample_world_domain
         world_service.mock_world_manager.increment_day.return_value = updated_domain
         world_service.mock_repository.save.side_effect = Exception("DB Save Error")

         # Act
         result = await world_service.advance_game_day(test_id)

         # Assert
         world_service.mock_repository.save.assert_awaited_once_with(updated_domain)
         assert result is None # Service returns None on save error

class TestAssignTheme:
    async def test_assign_theme_success_changed(self, world_service, sample_world_domain):
        """Test successfully assigning a new theme."""
        # Arrange
        world_id = sample_world_domain.id
        new_theme_id = uuid4()
        original_domain = dataclasses.replace(sample_world_domain, theme_id=uuid4()) # Start with a different theme
        updated_domain = dataclasses.replace(original_domain, theme_id=new_theme_id)
        updated_api = WorldApiModel(**dataclasses.asdict(updated_domain))

        world_service.mock_theme_service.exists.return_value = True
        world_service.mock_repository.find_by_id.return_value = original_domain
        world_service.mock_repository.save.return_value = updated_domain

        with patch.object(WorldService, '_convert_domain_to_api', return_value=updated_api):
             # Act
             result = await world_service.assign_theme_to_world(world_id, new_theme_id)

        # Assert
        world_service.mock_theme_service.exists.assert_awaited_once_with(new_theme_id)
        world_service.mock_repository.find_by_id.assert_awaited_once_with(world_id)
        # Check save was called with the correct object state
        call_args, _ = world_service.mock_repository.save.call_args
        saved_object = call_args[0]
        assert saved_object.theme_id == new_theme_id
        world_service.mock_repository.save.assert_awaited_once()

        assert result is not None
        assert result.id == world_id
        assert result.theme_id == new_theme_id

    async def test_assign_theme_success_no_change(self, world_service, sample_world_domain):
        """Test assigning the same theme results in no save operation."""
        # Arrange
        world_id = sample_world_domain.id
        current_theme_id = sample_world_domain.theme_id
        
        # Ensure the domain entity returned by find_by_id already has the target theme_id
        world_service.mock_theme_service.exists.return_value = True
        world_service.mock_repository.find_by_id.return_value = sample_world_domain # Already has current_theme_id
        
        # API model corresponds to the existing domain entity
        api_model = WorldApiModel(**dataclasses.asdict(sample_world_domain))

        with patch.object(WorldService, '_convert_domain_to_api', return_value=api_model):
             # Act
             result = await world_service.assign_theme_to_world(world_id, current_theme_id)

        # Assert
        world_service.mock_theme_service.exists.assert_awaited_once_with(current_theme_id)
        world_service.mock_repository.find_by_id.assert_awaited_once_with(world_id)
        world_service.mock_repository.save.assert_not_awaited() # Crucial: save should not be called

        assert result is not None
        assert result.id == world_id
        assert result.theme_id == current_theme_id

    async def test_assign_theme_theme_not_found(self, world_service, sample_world_domain):
        """Test assigning fails if the theme doesn't exist."""
        # Arrange
        world_id = sample_world_domain.id
        non_existent_theme_id = uuid4()
        world_service.mock_theme_service.exists.return_value = False

        # Act & Assert
        with pytest.raises(ValueError, match=f"Theme ID not found: {non_existent_theme_id}"):
            await world_service.assign_theme_to_world(world_id, non_existent_theme_id)

        world_service.mock_theme_service.exists.assert_awaited_once_with(non_existent_theme_id)
        world_service.mock_repository.find_by_id.assert_not_awaited()
        world_service.mock_repository.save.assert_not_awaited()

    async def test_assign_theme_world_not_found(self, world_service):
        """Test assigning fails if the world doesn't exist."""
        # Arrange
        non_existent_world_id = uuid4()
        theme_id = uuid4()
        world_service.mock_theme_service.exists.return_value = True
        world_service.mock_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match=f"World {non_existent_world_id} not found"):
            await world_service.assign_theme_to_world(non_existent_world_id, theme_id)

        world_service.mock_theme_service.exists.assert_awaited_once_with(theme_id)
        world_service.mock_repository.find_by_id.assert_awaited_once_with(non_existent_world_id)
        world_service.mock_repository.save.assert_not_awaited()

    async def test_assign_theme_save_fails(self, world_service, sample_world_domain):
        """Test assigning fails if the repository save operation fails."""
        # Arrange
        world_id = sample_world_domain.id
        new_theme_id = uuid4()
        original_domain = dataclasses.replace(sample_world_domain, theme_id=uuid4()) # Start with a different theme

        world_service.mock_theme_service.exists.return_value = True
        world_service.mock_repository.find_by_id.return_value = original_domain
        world_service.mock_repository.save.side_effect = ValueError("DB constraint violation") # Simulate save error

        # Act & Assert
        with pytest.raises(ValueError, match="Database error assigning theme"):
            await world_service.assign_theme_to_world(world_id, new_theme_id)

        world_service.mock_repository.save.assert_awaited_once() # Save was attempted
        
# Add tests for get_day, get_world_name, exists if desired - they are simpler variations of get_world