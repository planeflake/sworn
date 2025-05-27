from uuid import uuid4
from app.db.models.travel_link import TravelLink

def test_travel_link_model():
    travel_link_id = uuid4()
    from_location_id = uuid4()
    to_location_id = uuid4()
    biome_id = uuid4()
    faction_id = uuid4()

    travel_link = TravelLink(
        id=travel_link_id,
        name="test travel link",
        description="test travel link description",
        from_location_id=from_location_id,
        to_location_id=to_location_id,
        speed=1.0,
        path_type="trail",
        terrain_modifier=1.0,
        base_danger_level=1,
        distance_km=1.0,
        base_travel_time_hours=1.0,
        visibility="visible",
        is_active=True,
        weather_affected=True,
        seasonal_modifiers={
            "spring": {"speed": 0.9, "danger": 1.1},
            "summer": {"speed": 1.0, "danger": 1.0},
            "autumn": {"speed": 0.8, "danger": 1.2},
            "winter": {"speed": 0.6, "danger": 1.5}
        },
        biome_ids=[biome_id],
        faction_ids=[faction_id]
    )

    assert travel_link.id == travel_link_id
    assert travel_link.name == "test travel link"
    assert travel_link.description == "test travel link description"
    assert travel_link.from_location_id == from_location_id
    assert travel_link.to_location_id == to_location_id
    assert travel_link.speed == 1.0
    assert travel_link.path_type == "trail"
    assert travel_link.terrain_modifier == 1.0
    assert travel_link.base_danger_level == 1
    assert travel_link.distance_km == 1.0
    assert travel_link.base_travel_time_hours == 1.0
    assert travel_link.visibility == "visible"
    assert travel_link.is_active is True
    assert travel_link.weather_affected is True
    assert travel_link.seasonal_modifiers["winter"]["speed"] == 0.6
    assert travel_link.seasonal_modifiers["winter"]["danger"] == 1.5
    assert travel_link.biome_ids == [biome_id]
    assert travel_link.faction_ids == [faction_id]
