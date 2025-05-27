import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

# Import the repository and dependencies
from app.game_state.repositories.character_repository import CharacterRepository
from app.game_state.entities.character import CharacterEntity
from app.db.models.character import Character
from app.db.async_session import AsyncSession
from app.game_state.enums.character import CharacterTypeEnum, CharacterStatusEnum, CharacterTraitEnum

# Test fixtures
@pytest.fixture
def test_uuid():
    return uuid4()


@pytest.fixture
def world_uuid():
    return uuid4()


@pytest.fixture
def mock_db_session():
    """Mock AsyncSession for database operations"""
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

    # Mock get, add, flush, refresh, delete methods
    mock_session.get.return_value = None
    mock_session.add = MagicMock()
    mock_session.flush = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.delete = AsyncMock()
    mock_session.rollback = AsyncMock()

    return mock_session


@pytest_asyncio.fixture
async def character_repository(mock_db_session):
    """Create CharacterRepository instance with mocked session"""
    return CharacterRepository(db=mock_db_session)


@pytest.fixture
def sample_character_entity(test_uuid, world_uuid):
    """Sample character entity for testing"""
    return CharacterEntity(
        entity_id=test_uuid,
        name="Test Hero",
        character_type=CharacterTypeEnum.PLAYER,
        world_id=world_uuid,
        description="A brave test character",
        level=5,
        traits=[CharacterTraitEnum.DEFENSIVE, CharacterTraitEnum.ECONOMICAL],
        status=CharacterStatusEnum.ALIVE,
        is_active=True
    )


@pytest.fixture
def sample_character_model(test_uuid, world_uuid):
    """Sample character DB model for testing"""
    model = Character(
        id=test_uuid,
        name="Test Hero",
        character_type=CharacterTypeEnum.PLAYER,
        world_id=world_uuid,
        description="A brave test character",
        level=5,
        character_traits=[CharacterTraitEnum.DEFENSIVE, CharacterTraitEnum.ECONOMICAL],
        status=CharacterStatusEnum.ALIVE,
        is_active=True,
        created_at=datetime.now(),
        updated_at=None
    )
    return model


class TestCharacterRepositoryInit:
    """Test repository initialization"""

    @pytest.mark.asyncio
    async def test_repository_initialization(self, mock_db_session):
        """Test that repository initializes correctly"""
        repo = CharacterRepository(db=mock_db_session)

        assert repo.db == mock_db_session
        assert repo.model_cls == Character
        assert repo.entity_cls == CharacterEntity
        assert hasattr(repo, '_pk_attr_names')
        assert hasattr(repo, '_model_column_keys')


class TestCharacterRepositoryEntityConversion:
    """Test entity to model conversion and vice versa"""

    @pytest.mark.asyncio
    async def test_entity_to_model_dict_basic(self, character_repository, sample_character_entity):
        """Test converting character entity to model dict"""
        # Act
        result = await character_repository._entity_to_model_dict(sample_character_entity)

        # Assert
        assert 'name' in result
        assert result['name'] == sample_character_entity.name
        assert 'character_type' in result
        assert result['character_type'] == sample_character_entity.character_type
        assert 'level' in result
        assert result['level'] == sample_character_entity.level

        # Check that entity_id is mapped to id
        assert 'id' in result
        assert result['id'] == sample_character_entity.entity_id

    @pytest.mark.asyncio
    async def test_entity_to_model_dict_traits_mapping(self, character_repository, sample_character_entity):
        """Test that character traits are properly mapped to character_traits"""
        # Act
        result = await character_repository._entity_to_model_dict(sample_character_entity)

        # Assert
        assert 'character_traits' in result
        assert result['character_traits'] == sample_character_entity.traits
        assert CharacterTraitEnum.DEFENSIVE in result['character_traits']
        assert CharacterTraitEnum.ECONOMICAL in result['character_traits']

    @pytest.mark.asyncio
    async def test_entity_to_model_dict_empty_traits(self, character_repository, sample_character_entity):
        """Test handling of empty traits list"""
        # Arrange
        sample_character_entity.traits = []

        # Act
        result = await character_repository._entity_to_model_dict(sample_character_entity)

        # Assert
        assert 'character_traits' in result
        assert result['character_traits'] == []

    @pytest.mark.asyncio
    async def test_entity_to_model_dict_none_traits(self, character_repository, sample_character_entity):
        """Test handling of None traits"""
        # Arrange
        sample_character_entity.traits = None

        # Act
        result = await character_repository._entity_to_model_dict(sample_character_entity)

        # Assert
        assert 'character_traits' in result
        assert result['character_traits'] == []

    @pytest.mark.asyncio
    async def test_convert_to_entity_basic(self, character_repository, sample_character_model):
        """Test converting character model to entity"""
        # Act
        result = await character_repository._convert_to_entity(sample_character_model)

        # Assert
        assert result is not None
        assert isinstance(result, CharacterEntity)
        assert result.name == sample_character_model.name
        assert result.character_type == sample_character_model.character_type
        assert result.level == sample_character_model.level
        assert result.entity_id == sample_character_model.id

    @pytest.mark.asyncio
    async def test_convert_to_entity_traits_mapping(self, character_repository, sample_character_model):
        """Test that character_traits are properly mapped to traits"""
        # Act
        result = await character_repository._convert_to_entity(sample_character_model)

        # Assert
        assert result is not None
        assert hasattr(result, 'traits')
        assert result.traits == list(sample_character_model.character_traits)
        assert CharacterTraitEnum.DEFENSIVE in result.traits
        assert CharacterTraitEnum.ECONOMICAL in result.traits

    @pytest.mark.asyncio
    async def test_convert_to_entity_none_model(self, character_repository):
        """Test converting None model returns None"""
        # Act
        result = await character_repository._convert_to_entity(None)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_convert_to_entity_empty_traits(self, character_repository, sample_character_model):
        """Test handling of empty character_traits"""
        # Arrange
        sample_character_model.character_traits = []

        # Act
        result = await character_repository._convert_to_entity(sample_character_model)

        # Assert
        assert result is not None
        assert result.traits == []

    @pytest.mark.asyncio
    async def test_convert_to_entity_none_traits(self, character_repository, sample_character_model):
        """Test handling of None character_traits"""
        # Arrange
        sample_character_model.character_traits = None

        # Act
        result = await character_repository._convert_to_entity(sample_character_model)

        # Assert
        assert result is not None
        # Should handle None gracefully - behavior depends on implementation


class TestCharacterRepositoryCRUD:
    """Test CRUD operations"""

    @pytest.mark.asyncio
    async def test_save_new_character(self, character_repository, mock_db_session, sample_character_entity):
        """Test saving a new character"""
        # Arrange
        sample_character_entity.entity_id = None  # New entity
        mock_db_session.get.return_value = None  # Not found in DB

        # Mock the model creation and refresh
        saved_model = Character(
            id=uuid4(),
            name=sample_character_entity.name,
            character_type=sample_character_entity.character_type,
            world_id=sample_character_entity.world_id
        )

        async def mock_refresh(obj):
            obj.id = saved_model.id
            obj.created_at = datetime.now()
            obj.updated_at = None

        mock_db_session.refresh.side_effect = mock_refresh

        # Act
        with patch.object(character_repository, '_convert_to_entity', return_value=sample_character_entity):
            result = await character_repository.save(sample_character_entity)

        # Assert
        assert result == sample_character_entity
        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_existing_character(self, character_repository, mock_db_session, sample_character_entity,
                                           sample_character_model):
        """Test updating an existing character"""
        # Arrange: set the entity_id and mock the database to return an existing model
        sample_character_entity.entity_id = sample_character_model.id
        # WORKAROUND: The base repository looks for 'id' attribute on entity, but CharacterEntity uses 'entity_id'
        # Set both to ensure the repository can find the primary key value
        sample_character_entity.id = sample_character_model.id
        mock_db_session.get.return_value = sample_character_model

        # Act: Save the entity (should update existing, not insert new)
        result = await character_repository.save(sample_character_entity)

        # Assert: Make sure the result is correct and no add() was called
        assert result.entity_id == sample_character_entity.entity_id
        mock_db_session.get.assert_called_once_with(Character, sample_character_model.id)
        mock_db_session.add.assert_not_called()  # Should not add an existing model
        mock_db_session.flush.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, character_repository, mock_db_session, test_uuid):
        """Test finding character by ID when it doesn't exist"""
        # Arrange
        mock_db_session.get.return_value = None

        # Act
        result = await character_repository.find_by_id(test_uuid)

        # Assert
        assert result is None
        mock_db_session.get.assert_called_once_with(Character, test_uuid)

    @pytest.mark.asyncio
    async def test_get_by_name(self, character_repository):
        """Test the get_by_name method"""
        # Arrange
        test_name = "Test Hero"
        expected_entity = MagicMock()

        # Act
        with patch.object(character_repository, 'get_by_field', return_value=expected_entity) as mock_get_by_field:
            result = await character_repository.get_by_name(test_name)

        # Assert
        assert result == expected_entity
        mock_get_by_field.assert_called_once_with("name", test_name)

    @pytest.mark.asyncio
    async def test_delete_character_found(self, character_repository, mock_db_session, test_uuid,
                                          sample_character_model):
        """Test deleting a character that exists"""
        # Arrange
        mock_db_session.get.return_value = sample_character_model

        # Act
        result = await character_repository.delete(test_uuid)

        # Assert
        assert result is True
        mock_db_session.get.assert_called_once_with(Character, test_uuid)
        mock_db_session.delete.assert_called_once_with(sample_character_model)
        mock_db_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_character_not_found(self, character_repository, mock_db_session, test_uuid):
        """Test deleting a character that doesn't exist"""
        # Arrange
        mock_db_session.get.return_value = None

        # Act
        result = await character_repository.delete(test_uuid)

        # Assert
        assert result is False
        mock_db_session.get.assert_called_once_with(Character, test_uuid)
        mock_db_session.delete.assert_not_called()
        mock_db_session.flush.assert_not_called()

    @pytest.mark.asyncio
    async def test_find_all(self, character_repository, mock_db_session, sample_character_model,
                            sample_character_entity):
        """Test finding all characters with pagination"""
        # Arrange
        mock_result = mock_db_session.execute.return_value
        mock_scalars = mock_result.scalars.return_value
        mock_scalars.all.return_value = [sample_character_model]

        # Act
        with patch.object(character_repository, '_convert_to_entity', return_value=sample_character_entity):
            result = await character_repository.find_all(skip=0, limit=10)

        # Assert
        assert len(result) == 1
        assert result[0] == sample_character_entity
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_exists_character_found(self, character_repository, mock_db_session, test_uuid):
        """Test checking if character exists when it does"""
        # Arrange
        mock_result = mock_db_session.execute.return_value
        mock_result.scalar_one_or_none.return_value = True

        # Act
        result = await character_repository.exists(test_uuid)

        # Assert
        assert result is True
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_exists_character_not_found(self, character_repository, mock_db_session, test_uuid):
        """Test checking if character exists when it doesn't"""
        # Arrange
        mock_result = mock_db_session.execute.return_value
        mock_result.scalar_one_or_none.return_value = False

        # Act
        result = await character_repository.exists(test_uuid)

        # Assert
        assert result is False
        mock_db_session.execute.assert_called_once()


class TestCharacterRepositorySpecialMethods:
    """Test character-specific methods"""

    @pytest.mark.asyncio
    async def test_add_resources_placeholder(self, character_repository):
        """Test the add_resources method (currently placeholder)"""
        # Arrange
        character_id = uuid4()
        resource_entities = []  # Empty list for now since method is placeholder

        # Act
        result = await character_repository.add_resources(character_id, resource_entities)

        # Assert
        assert result is None  # Method currently returns None (placeholder)


class TestCharacterRepositoryEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_save_none_entity(self, character_repository):
        """Test saving None entity raises appropriate error"""
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot save None entity"):
            await character_repository.save(None)

    @pytest.mark.asyncio
    async def test_entity_to_model_dict_none_entity(self, character_repository):
        """Test converting None entity raises appropriate error"""
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot convert None entity"):
            await character_repository._entity_to_model_dict(None)

    @pytest.mark.asyncio
    async def test_find_by_id_invalid_uuid(self, character_repository, mock_db_session):
        """Test finding by invalid UUID"""
        # Arrange
        invalid_id = "not-a-uuid"
        mock_db_session.get.side_effect = ValueError("Invalid UUID")

        # Act & Assert
        with pytest.raises(ValueError):
            await character_repository.find_by_id(invalid_id)

    @pytest.mark.asyncio
    async def test_bulk_save_empty_list(self, character_repository):
        """Test bulk saving empty list"""
        # Act
        result = await character_repository.bulk_save([])

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_bulk_save_multiple_characters(self, character_repository, mock_db_session, world_uuid):
        """Test bulk saving multiple characters"""
        # Arrange
        entities = [
            CharacterEntity(
                name=f"Hero {i}",
                character_type=CharacterTypeEnum.PLAYER,
                world_id=world_uuid,
                level=i
            )
            for i in range(3)
        ]

        # Mock successful bulk save
        saved_entities = entities.copy()
        for i, entity in enumerate(saved_entities):
            entity.entity_id = uuid4()

        # Act
        with patch.object(character_repository, 'save', side_effect=saved_entities):
            result = await character_repository.bulk_save(entities)

        # Assert
        assert len(result) == 3
        assert all(isinstance(entity, CharacterEntity) for entity in result)


class TestCharacterRepositoryInheritedMethods:
    """Test methods inherited from BaseRepository"""

    @pytest.mark.asyncio
    async def test_find_by_name_insensitive(self, character_repository, mock_db_session, sample_character_model,
                                            sample_character_entity):
        """Test case-insensitive name search"""
        # Arrange
        mock_result = mock_db_session.execute.return_value
        mock_result.scalar_one_or_none.return_value = sample_character_model

        # Act
        with patch.object(character_repository, '_convert_to_entity', return_value=sample_character_entity):
            result = await character_repository.find_by_name_insensitive("TEST HERO")

        # Assert
        assert result == sample_character_entity
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_all_by_name_partial_match(self, character_repository, mock_db_session, sample_character_model,
                                                  sample_character_entity):
        """Test finding all characters by partial name match"""
        # Arrange
        mock_result = mock_db_session.execute.return_value
        mock_scalars = mock_result.scalars.return_value
        mock_scalars.all.return_value = [sample_character_model]

        # Act
        with patch.object(character_repository, '_convert_to_entity', return_value=sample_character_entity):
            result = await character_repository.find_all_by_name("Hero", partial_match=True)

        # Assert
        assert len(result) == 1
        assert result[0] == sample_character_entity
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_multiple_fields(self, character_repository, mock_db_session, sample_character_model,
                                           sample_character_entity):
        """Test finding characters by multiple fields"""
        # Arrange
        mock_result = mock_db_session.execute.return_value
        mock_scalars = mock_result.scalars.return_value
        mock_scalars.all.return_value = [sample_character_model]

        search_criteria = {
            "character_type": CharacterTypeEnum.PLAYER,
            "level": 5
        }

        # Act
        with patch.object(character_repository, '_convert_to_entity', return_value=sample_character_entity):
            result = await character_repository.find_by_multiple_fields(search_criteria)

        # Assert
        assert len(result) == 1
        assert result[0] == sample_character_entity
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_all(self, character_repository, mock_db_session):
        """Test counting all characters"""
        # Arrange
        mock_result = mock_db_session.execute.return_value
        mock_result.scalar_one_or_none.return_value = 42

        # Act
        result = await character_repository.count_all()

        # Assert
        assert result == 42
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_all_paginated(self, character_repository, mock_db_session, sample_character_model,
                                      sample_character_entity):
        """Test paginated character search"""
        # Arrange
        # Mock the items query
        mock_result_items = MagicMock()
        mock_scalars_items = mock_result_items.scalars.return_value
        mock_scalars_items.all.return_value = [sample_character_model]

        # Mock the count query
        mock_result_count = MagicMock()
        mock_result_count.scalar_one_or_none.return_value = 100

        # Set up execute to return different results for different calls
        mock_db_session.execute.side_effect = [mock_result_items, mock_result_count]

        # Act
        with patch.object(character_repository, '_convert_to_entity', return_value=sample_character_entity):
            result = await character_repository.find_all_paginated(skip=0, limit=10)

        # Assert
        assert "items" in result
        assert "total" in result
        assert "limit" in result
        assert "skip" in result
        assert len(result["items"]) == 1
        assert result["total"] == 100
        assert result["limit"] == 10
        assert result["skip"] == 0