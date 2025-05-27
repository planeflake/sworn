import pytest
from uuid import uuid4, UUID
from datetime import datetime
from pydantic import ValidationError

# Import the entity we're testing
from app.game_state.entities.character.character_pydantic import CharacterEntityPydantic

# Import enums
from app.game_state.enums.character import CharacterTypeEnum, CharacterStatusEnum, CharacterTraitEnum

# Import related entities (mock these if needed)
from app.game_state.entities.equipment import EquipmentEntity
from app.game_state.entities.skill import SkillEntity
from app.game_state.entities.stat import StatEntity
from app.game_state.entities.item import Item


class TestCharacterEntityPydantic:
    """Test suite for CharacterEntityPydantic entity"""

    @pytest.fixture
    def valid_character_data(self):
        """Provide valid data for character creation"""
        return {
            "name": "Test Hero",
            "character_type": CharacterTypeEnum.PLAYER,
            "world_id": uuid4(),
            "description": "A brave test character"
        }

    @pytest.fixture
    def full_character_data(self):
        """Provide complete character data with all optional fields"""
        world_id = uuid4()
        player_id = uuid4()
        location_id = uuid4()

        return {
            "name": "Complete Hero",
            "character_type": CharacterTypeEnum.NPC,
            "world_id": world_id,
            "description": "A fully configured character",
            "traits": [CharacterTraitEnum.DEFENSIVE, CharacterTraitEnum.ECONOMICAL],
            "level": 5,
            "is_active": True,
            "status": CharacterStatusEnum.ALIVE,
            "player_account_id": player_id,
            "current_location_id": location_id,
            "last_login": datetime.now()
        }

    def test_character_creation_minimal_fields(self, valid_character_data):
        """Test creating a character with only required fields"""
        character = CharacterEntityPydantic(**valid_character_data)

        # Required fields should be set
        assert character.name == valid_character_data["name"]
        assert character.character_type == valid_character_data["character_type"]
        assert character.world_id == valid_character_data["world_id"]
        assert character.description == valid_character_data["description"]

        # Default values should be applied
        assert character.level == 1
        assert character.is_active is True
        assert character.status == CharacterStatusEnum.ALIVE
        assert character.traits == []
        assert character.stats == []
        assert character.equipment == []
        assert character.items == []
        assert character.skills == []

        # Optional fields should be None
        assert character.player_account_id is None
        assert character.current_location_id is None
        assert character.last_login is None

        # Should have inherited fields from BaseEntityPydantic
        assert isinstance(character.entity_id, UUID)
        assert isinstance(character.created_at, datetime)
        # updated_at is None until first update
        assert character.updated_at is None

    def test_character_creation_with_defaults(self):
        """Test creating a character with only truly required fields (using defaults)"""
        character = CharacterEntityPydantic(
            character_type=CharacterTypeEnum.PLAYER,
            world_id=uuid4()
        )

        # Should use default name from base class
        assert character.name == "Unnamed Entity"
        assert character.character_type == CharacterTypeEnum.PLAYER
        assert isinstance(character.world_id, UUID)

        # All other defaults should apply
        assert character.level == 1
        assert character.is_active is True
        assert character.status == CharacterStatusEnum.ALIVE
        assert character.traits == []

    def test_character_creation_full_fields(self, full_character_data):
        """Test creating a character with all fields populated"""
        character = CharacterEntityPydantic(**full_character_data)

        # All fields should match input
        assert character.name == full_character_data["name"]
        assert character.character_type == full_character_data["character_type"]
        assert character.world_id == full_character_data["world_id"]
        assert character.description == full_character_data["description"]
        assert character.traits == full_character_data["traits"]
        assert character.level == full_character_data["level"]
        assert character.status == full_character_data["status"]
        assert character.player_account_id == full_character_data["player_account_id"]
        assert character.current_location_id == full_character_data["current_location_id"]
        assert character.last_login == full_character_data["last_login"]

    def test_character_validation_missing_required_fields(self):
        """Test that missing required fields raise ValidationError"""
        # Missing character_type should fail
        with pytest.raises(ValidationError) as exc_info:
            CharacterEntityPydantic(
                world_id=uuid4()
                # name has default "Unnamed Entity" from base class
            )
        assert "character_type" in str(exc_info.value)

        # Missing world_id should fail
        with pytest.raises(ValidationError) as exc_info:
            CharacterEntityPydantic(
                character_type=CharacterTypeEnum.PLAYER
                # name has default from base class
            )
        assert "world_id" in str(exc_info.value)

        # Both missing should fail
        with pytest.raises(ValidationError) as exc_info:
            CharacterEntityPydantic()
        validation_msg = str(exc_info.value)
        assert "character_type" in validation_msg or "world_id" in validation_msg

    def test_character_type_enum_validation(self, valid_character_data):
        """Test character type enum validation"""
        # Valid enum value
        valid_character_data["character_type"] = CharacterTypeEnum.NPC
        character = CharacterEntityPydantic(**valid_character_data)
        assert character.character_type == CharacterTypeEnum.NPC

        # Invalid enum value should raise ValidationError
        valid_character_data["character_type"] = "INVALID_TYPE"
        with pytest.raises(ValidationError) as exc_info:
            CharacterEntityPydantic(**valid_character_data)
        assert "character_type" in str(exc_info.value)

    def test_character_status_enum_validation(self, valid_character_data):
        """Test character status enum validation"""
        # Valid enum values
        for status in CharacterStatusEnum:
            valid_character_data["status"] = status
            character = CharacterEntityPydantic(**valid_character_data)
            assert character.status == status

        # Invalid enum value
        valid_character_data["status"] = "INVALID_STATUS"
        with pytest.raises(ValidationError) as exc_info:
            CharacterEntityPydantic(**valid_character_data)
        assert "status" in str(exc_info.value)

    def test_character_traits_validation(self, valid_character_data):
        """Test character traits list validation"""
        # Valid single trait
        valid_character_data["traits"] = [CharacterTraitEnum.DEFENSIVE]
        character = CharacterEntityPydantic(**valid_character_data)
        assert character.traits == [CharacterTraitEnum.DEFENSIVE]

        # Valid multiple traits
        traits = [CharacterTraitEnum.DEFENSIVE, CharacterTraitEnum.ECONOMICAL]
        valid_character_data["traits"] = traits
        character = CharacterEntityPydantic(**valid_character_data)
        assert character.traits == traits

        # Empty list should work
        valid_character_data["traits"] = []
        character = CharacterEntityPydantic(**valid_character_data)
        assert character.traits == []

        # Invalid trait should raise ValidationError
        valid_character_data["traits"] = ["INVALID_TRAIT"]
        with pytest.raises(ValidationError) as exc_info:
            CharacterEntityPydantic(**valid_character_data)
        assert "traits" in str(exc_info.value)

    def test_level_validation(self, valid_character_data):
        """Test character level validation"""
        # Valid positive level
        valid_character_data["level"] = 10
        character = CharacterEntityPydantic(**valid_character_data)
        assert character.level == 10

        # Level 1 should work (default)
        valid_character_data["level"] = 1
        character = CharacterEntityPydantic(**valid_character_data)
        assert character.level == 1

        # Zero level might be invalid depending on your business rules
        # Uncomment if you have validation for this
        # valid_character_data["level"] = 0
        # with pytest.raises(ValidationError):
        #     CharacterEntityPydantic(**valid_character_data)

        # Negative level should probably be invalid
        # Uncomment if you have validation for this
        # valid_character_data["level"] = -1
        # with pytest.raises(ValidationError):
        #     CharacterEntityPydantic(**valid_character_data)

    def test_uuid_field_validation(self, valid_character_data):
        """Test UUID field validation"""
        # Valid UUID string should be converted
        uuid_str = str(uuid4())
        valid_character_data["world_id"] = uuid_str
        character = CharacterEntityPydantic(**valid_character_data)
        assert isinstance(character.world_id, UUID)
        assert str(character.world_id) == uuid_str

        # Valid UUID object should work
        uuid_obj = uuid4()
        valid_character_data["world_id"] = uuid_obj
        character = CharacterEntityPydantic(**valid_character_data)
        assert character.world_id == uuid_obj

        # Invalid UUID string should raise ValidationError
        valid_character_data["world_id"] = "not-a-uuid"
        with pytest.raises(ValidationError) as exc_info:
            CharacterEntityPydantic(**valid_character_data)
        assert "world_id" in str(exc_info.value)

    def test_datetime_field_validation(self, valid_character_data):
        """Test datetime field validation"""
        # Valid datetime object
        now = datetime.now()
        valid_character_data["last_login"] = now
        character = CharacterEntityPydantic(**valid_character_data)
        assert character.last_login == now

        # ISO string should be parsed to datetime
        iso_string = "2023-01-01T12:00:00"
        valid_character_data["last_login"] = iso_string
        character = CharacterEntityPydantic(**valid_character_data)
        assert isinstance(character.last_login, datetime)

        # Invalid datetime string should raise ValidationError
        valid_character_data["last_login"] = "not-a-datetime"
        with pytest.raises(ValidationError) as exc_info:
            CharacterEntityPydantic(**valid_character_data)
        assert "last_login" in str(exc_info.value)

    def test_character_serialization(self, full_character_data):
        """Test character can be serialized to dict and JSON"""
        character = CharacterEntityPydantic(**full_character_data)

        # Should convert to dict
        char_dict = character.model_dump()
        assert isinstance(char_dict, dict)
        assert char_dict["name"] == character.name
        assert char_dict["level"] == character.level

        # Should convert to JSON
        char_json = character.model_dump_json()
        assert isinstance(char_json, str)
        assert character.name in char_json

    def test_character_deserialization(self, full_character_data):
        """Test character can be created from dict"""
        # Create character
        original = CharacterEntityPydantic(**full_character_data)

        # Convert to dict and back
        char_dict = original.model_dump()
        recreated = CharacterEntityPydantic(**char_dict)

        # Should be equivalent
        assert recreated.name == original.name
        assert recreated.character_type == original.character_type
        assert recreated.level == original.level
        assert recreated.traits == original.traits

    def test_character_model_config(self, valid_character_data):
        """Test Pydantic model configuration"""
        character = CharacterEntityPydantic(**valid_character_data)

        # Should allow arbitrary types (for complex nested entities)
        assert character.model_config["arbitrary_types_allowed"] is True

        # Should support from_attributes (for ORM integration)
        assert character.model_config["from_attributes"] is True

        # Should have JSON schema example
        assert "json_schema_extra" in character.model_config
        example = character.model_config["json_schema_extra"]["example"]
        assert "name" in example
        assert "character_type" in example

    def test_character_inheritance(self, valid_character_data):
        """Test that character properly inherits from BaseEntityPydantic"""
        character = CharacterEntityPydantic(**valid_character_data)

        # Should have inherited fields
        assert hasattr(character, 'entity_id')
        assert hasattr(character, 'created_at')
        assert hasattr(character, 'updated_at')
        assert hasattr(character, 'name')  # Assuming this is in base class

        # Inherited fields should have correct types
        assert isinstance(character.entity_id, UUID)
        assert isinstance(character.created_at, datetime)
        # updated_at might be None until first update
        assert character.updated_at is None or isinstance(character.updated_at, datetime)

    def test_character_equality(self, valid_character_data):
        """Test character equality comparison"""
        char1 = CharacterEntityPydantic(**valid_character_data)

        # Same data should create equal characters (if entity_id is the same)
        char2_data = valid_character_data.copy()
        char2_data["entity_id"] = char1.entity_id
        char2 = CharacterEntityPydantic(**char2_data)

        # This depends on how equality is implemented in your base class
        # Uncomment if you have custom equality logic
        # assert char1 == char2

        # Different characters should not be equal
        char3 = CharacterEntityPydantic(**valid_character_data)
        assert char1.entity_id != char3.entity_id

    def test_character_string_representation(self, valid_character_data):
        """Test character string representation"""
        character = CharacterEntityPydantic(**valid_character_data)

        char_str = str(character)
        char_repr = repr(character)

        # Should contain character name and type
        assert character.name in char_str
        assert "CharacterEntityPydantic" in char_repr

    @pytest.mark.parametrize("trait", list(CharacterTraitEnum))
    def test_all_character_traits(self, valid_character_data, trait):
        """Test that all character traits are valid"""
        valid_character_data["traits"] = [trait]
        character = CharacterEntityPydantic(**valid_character_data)
        assert trait in character.traits

    @pytest.mark.parametrize("char_type", list(CharacterTypeEnum))
    def test_all_character_types(self, valid_character_data, char_type):
        """Test that all character types are valid"""
        valid_character_data["character_type"] = char_type
        character = CharacterEntityPydantic(**valid_character_data)
        assert character.character_type == char_type

    @pytest.mark.parametrize("status", list(CharacterStatusEnum))
    def test_all_character_statuses(self, valid_character_data, status):
        """Test that all character statuses are valid"""
        valid_character_data["status"] = status
        character = CharacterEntityPydantic(**valid_character_data)
        assert character.status == status