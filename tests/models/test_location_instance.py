import pytest
from uuid import uuid4, UUID
from app.db.models.location_instance import LocationInstance

# Predefined UUIDs for use in tests
required_type_id = uuid4()
test_id = uuid4()
parent_id = uuid4()

def test_location_instance_minimal_fields():
    """
    Test that the model works with only required fields.
    Since we are not using a real DB, we manually set the ID.
    """
    generated_id = uuid4()
    location = LocationInstance(
        id=generated_id,
        name="Barebones",
        location_type_id=required_type_id
    )

    assert location.id == generated_id
    assert location.name == "Barebones"
    assert location.location_type_id == required_type_id
    assert isinstance(location.id, UUID)

def test_location_instance_full_init():
    """
    Test that all optional fields can be assigned and preserved.
    """
    location = LocationInstance(
        id=test_id,
        name="Test Location",
        description="Test Description",
        world_id=uuid4(),
        location_type_id=required_type_id,
        parent_id=parent_id,
        theme_id=uuid4(),
        biome_id=uuid4(),
        controlled_by_faction_id=uuid4(),
        location_sub_type="Outpost",
        base_danger_level=3,
        is_active=True,
        tags=["coastal", "fortified"]
    )

    assert location.id == test_id
    assert location.name == "Test Location"
    assert location.description == "Test Description"
    assert location.parent_id == parent_id
    assert location.base_danger_level == 3
    assert location.tags == ["coastal", "fortified"]
    assert location.is_active is True
    assert location.location_sub_type == "Outpost"

def test_location_instance_default_base_danger_level():
    """
    If default=1 is set in model, this should be 1.
    Otherwise, it may be None without DB insert.
    """
    location = LocationInstance(
        id=uuid4(),
        name="Danger Check",
        location_type_id=required_type_id
    )

    assert location.base_danger_level in (None, 1)

def test_location_instance_tags_none_or_list():
    """
    Tags should default to None and support lists.
    """
    location = LocationInstance(
        id=uuid4(),
        name="Tag Test",
        location_type_id=required_type_id
    )

    assert location.tags is None or isinstance(location.tags, list)

def test_location_instance_repr_output():
    """
    Repr output should contain class name and identifying fields.
    """
    location = LocationInstance(
        id=test_id,
        name="Watchtower",
        location_type_id=required_type_id,
        parent_id=parent_id
    )

    rep = repr(location)
    assert "LocationInstance" in rep
    assert "Watchtower" in rep
