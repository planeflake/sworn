# Unit Testing Guide for Updated Location System

This document outlines the unit tests needed to validate the new location system with comprehensive travel connections, buildings, resources, and dynamic danger calculations.

## Test File Structure for CI/CD

```
tests/
├── unit/                           # CI/CD Tests (fast, no DB)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── test_location_instance.py      # Model instantiation & defaults
│   │   ├── test_travel_link.py            # Travel link model logic
│   │   ├── test_wildlife.py               # Wildlife danger calculations
│   │   └── test_character_faction.py      # Faction relationship logic
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── test_location_schemas.py       # Pydantic validation
│   │   ├── test_building_schemas.py       # Building response schemas
│   │   └── test_travel_schemas.py         # Travel connection schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── test_location_service.py       # Business logic (mocked)
│   │   └── test_danger_service.py         # Danger calculation logic
│   ├── utils/
│   │   ├── __init__.py
│   │   └── test_route_utils.py            # Response builder logic (mocked)
│   └── conftest.py                        # Unit test fixtures
├── integration/                    # Local/Staging Tests (with DB)
│   ├── __init__.py
│   ├── test_database_models.py            # Real DB operations
│   ├── test_api_endpoints.py              # Full API tests
│   ├── test_location_workflow.py          # End-to-end workflows
│   └── conftest.py                        # Integration test fixtures
├── migration/                      # Deployment Tests
│   ├── __init__.py
│   └── test_alembic_migrations.py         # Migration validation
└── factories.py                           # Test data factories
```

## CI/CD Unit Tests (Priority Order)

### Priority 1: Core Model Logic

#### `tests/unit/models/test_location_instance.py`
```python
def test_location_instance_creation()          # Basic instantiation
def test_location_instance_defaults()          # Default values
def test_location_instance_field_validation()  # Field constraints
```

#### `tests/unit/models/test_wildlife.py`
```python
def test_wildlife_danger_calculation()         # Core business logic
def test_wildlife_pack_behavior()              # Pack danger bonus
def test_wildlife_single_creature()            # No pack behavior
def test_wildlife_threat_level_enum()          # Enum validation
```

#### `tests/unit/models/test_travel_link.py`
```python
def test_travel_link_creation()                # Basic creation
def test_travel_link_defaults()                # Default speed, visibility
def test_travel_link_array_fields()            # biome_ids, faction_ids
```

### Priority 2: Schema Validation

#### `tests/unit/schemas/test_location_schemas.py`
```python
def test_location_response_schema()            # Main response structure
def test_location_sub_type_schema()            # Sub-type reference
def test_empty_arrays_default()                # Default empty lists
def test_optional_fields()                     # theme_id, biome_id optional
```

#### `tests/unit/schemas/test_building_schemas.py`
```python
def test_building_response_schema()            # Building structure
def test_building_upgrade_schema()             # Upgrade options
def test_building_nested_structure()           # Buildings with upgrades
```

#### `tests/unit/schemas/test_travel_schemas.py`
```python
def test_travel_connection_schema()            # Travel connection structure
def test_biome_faction_references()            # Nested reference objects
def test_danger_level_calculation()            # Dynamic danger in response
```

### Priority 3: Business Logic (Mocked)

#### `tests/unit/services/test_location_service.py`
```python
@patch('app.game_state.repositories.location.location_repository.LocationRepository')
def test_get_location_with_full_data()         # Service orchestration
def test_create_location_with_new_fields()     # New field handling
def test_location_sub_type_assignment()        # Sub-type logic
```

#### `tests/unit/services/test_danger_service.py`
```python
def test_base_danger_calculation()             # Static danger
def test_wildlife_danger_modifier()            # Wildlife impact
def test_faction_relationship_modifier()       # Character faction bonus/penalty
def test_combined_danger_factors()             # All factors together
```

### Priority 4: Utils and Helpers

#### `tests/unit/utils/test_route_utils.py`
```python
@patch('app.api.routes.location.location_route_utils.fetch_location_buildings')
def test_build_location_response()             # Main response builder
def test_location_sub_type_creation()          # Sub-type response building
def test_empty_data_handling()                 # Graceful empty responses
```

## Integration Tests (Local/Staging Only)

### `tests/integration/test_database_models.py`
```python
@pytest.mark.asyncio
async def test_location_instance_database_save()       # Real DB operations
async def test_travel_link_relationships()             # FK constraints
async def test_wildlife_cascade_delete()               # Relationship cascades
```

### `tests/integration/test_api_endpoints.py`
```python
@pytest.mark.asyncio 
async def test_get_location_comprehensive_response()   # Full API response
async def test_location_with_travel_connections()      # Travel data included
async def test_location_with_buildings_resources()     # All related data
```

## Test Categories

### 1. Database Model Tests

#### LocationInstance Model Tests
**File**: `tests/models/test_location_instance.py`

**Tests needed**:
- `test_location_instance_creation()` - Basic model creation with new fields
- `test_location_instance_relationships()` - Theme, biome, faction relationships
- `test_location_instance_travel_links()` - Outgoing/incoming travel link relationships
- `test_location_instance_wildlife()` - Wildlife relationship and cascade delete
- `test_location_instance_base_danger_level_default()` - Default danger level is 1

**Hints**:
```python
async def test_location_instance_creation():
    # Create theme, biome, faction first
    theme = await create_test_theme()
    biome = await create_test_biome()
    faction = await create_test_faction()
    
    location = LocationInstance(
        name="Test Village",
        location_sub_type="village",
        theme_id=theme.id,
        biome_id=biome.id,
        controlled_by_faction_id=faction.id,
        base_danger_level=3
    )
    
    assert location.name == "Test Village"
    assert location.base_danger_level == 3
    assert location.location_sub_type == "village"
```

#### TravelLink Model Tests
**File**: `tests/models/test_travel_link.py`

**Tests needed**:
- `test_travel_link_creation()` - Basic creation with from/to locations
- `test_travel_link_biome_faction_arrays()` - Test biome_ids and faction_ids arrays
- `test_travel_link_relationships()` - from_location and to_location relationships
- `test_travel_link_default_values()` - Default speed=1.0, visibility="visible"

#### Wildlife Model Tests  
**File**: `tests/models/test_wildlife.py`

**Tests needed**:
- `test_wildlife_creation()` - Basic wildlife creation
- `test_wildlife_danger_calculation()` - Test `get_effective_danger()` method
- `test_wildlife_pack_behavior()` - Pack bonuses for danger calculation
- `test_wildlife_location_relationship()` - Location cascade delete

**Hints**:
```python
def test_wildlife_pack_danger_calculation():
    wildlife = Wildlife(
        name="Wolf Pack",
        population=6,
        danger_rating=3,
        pack_behavior=True,
        pack_size_min=3,
        pack_size_max=8
    )
    
    # Base: 3 * 6 = 18
    # Pack bonus: 2 packs * 0.5 = 1.0 multiplier
    # Expected: 18 * (1 + 1.0) = 36
    assert wildlife.get_effective_danger() == 36
```

#### CharacterFactionRelationship Model Tests
**File**: `tests/models/test_character_faction_relationship.py`

**Tests needed**:
- `test_relationship_creation()` - Basic creation with character and faction
- `test_reputation_score_bounds()` - Test -100 to +100 range
- `test_relationship_status_enum()` - Test all status values
- `test_character_cascade_delete()` - Delete character removes relationships

### 2. API Schema Tests

#### Location Response Schema Tests
**File**: `tests/schemas/test_location_schema.py`

**Tests needed**:
- `test_location_response_schema()` - All new fields present
- `test_building_response_schema()` - Building with upgrades structure
- `test_resource_response_schema()` - Resource quantity and units
- `test_travel_connection_schema()` - Travel connection with biomes/factions
- `test_location_sub_type_schema()` - Sub-type reference structure

**Hints**:
```python
def test_location_response_schema():
    data = {
        "id": str(uuid4()),
        "name": "Test Location",
        "location_type_id": str(uuid4()),
        "theme_id": str(uuid4()),
        "biome_id": str(uuid4()),
        "buildings": [],
        "resources": [],
        "resource_nodes": [],
        "travel_connections": []
    }
    
    response = LocationResponse(**data)
    assert response.buildings == []
    assert response.travel_connections == []
    assert response.theme_id is not None
```

### 3. Service Layer Tests

#### Location Service Tests
**File**: `tests/services/test_location_service.py`

**Tests needed**:
- `test_get_location_with_full_data()` - Fetch location with all related data
- `test_create_location_with_new_fields()` - Create with theme_id, biome_id
- `test_update_location_danger_level()` - Update base danger level
- `test_location_sub_type_handling()` - Set and retrieve sub-types

**Hints**:
```python
async def test_get_location_with_full_data():
    # Setup: Create location with buildings, resources, travel links
    location = await create_test_location_with_data()
    
    service = LocationService(db)
    result = await service.get_location_with_full_data(location.id)
    
    assert result is not None
    assert result.entity_id == location.id
    # Verify related data is loaded (implement when full data fetching is complete)
```

### 4. Repository Tests

#### Location Repository Tests
**File**: `tests/repositories/test_location_repository.py`

**Tests needed**:
- `test_get_with_full_data()` - Repository method for full data fetching
- `test_location_with_theme_biome()` - Fetch locations with theme/biome joins
- `test_location_travel_links()` - Fetch with travel connections
- `test_location_wildlife()` - Fetch with wildlife data

### 5. API Route Tests

#### Location Route Tests
**File**: `tests/routes/test_location_routes.py`

**Tests needed**:
- `test_get_location_comprehensive_response()` - Full response structure
- `test_location_with_buildings()` - Response includes buildings array
- `test_location_with_travel_connections()` - Response includes travel connections
- `test_location_danger_calculation()` - Dynamic danger levels in response
- `test_location_sub_type_filtering()` - Filter by sub-type

**Hints**:
```python
async def test_get_location_comprehensive_response():
    # Setup test data
    location = await create_location_with_full_data()
    
    response = client.get(f"/locations/{location.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify all new fields are present
    assert "buildings" in data
    assert "resources" in data
    assert "resource_nodes" in data
    assert "travel_connections" in data
    assert "theme_id" in data
    assert "biome_id" in data
    assert "location_sub_type" in data
    
    # Verify structure of nested objects
    if data["buildings"]:
        building = data["buildings"][0]
        assert "building_id" in building
        assert "upgrades" in building
        
    if data["travel_connections"]:
        connection = data["travel_connections"][0]
        assert "travel_link_id" in connection
        assert "biomes" in connection
        assert "factions" in connection
        assert "danger_level" in connection
```

### 6. Response Builder Tests

#### Location Route Utils Tests
**File**: `tests/utils/test_location_route_utils.py`

**Tests needed**:
- `test_build_location_response()` - Main response builder function
- `test_fetch_location_buildings()` - Building fetching logic
- `test_fetch_location_resources()` - Resource fetching logic  
- `test_fetch_travel_connections()` - Travel connection fetching
- `test_dynamic_danger_calculation()` - Character-specific danger levels

**Hints**:
```python
async def test_fetch_travel_connections():
    # Setup: location with travel links, biomes, factions
    location = await create_test_location()
    destination = await create_test_location()
    biome = await create_test_biome()
    faction = await create_test_faction()
    
    travel_link = TravelLink(
        from_location_id=location.id,
        to_location_id=destination.id,
        name="Forest Path",
        speed=1.0,
        path_type="trail",
        base_danger_level=2,
        biome_ids=[biome.id],
        faction_ids=[faction.id]
    )
    
    connections = await fetch_travel_connections(db, location.id)
    
    assert len(connections) == 1
    assert connections[0].name == "Forest Path"
    assert len(connections[0].biomes) == 1
    assert connections[0].biomes[0].name == biome.name
    assert len(connections[0].factions) == 1
    assert connections[0].danger_level == 2
```

### 7. Integration Tests

#### Full System Integration Tests
**File**: `tests/integration/test_location_system_integration.py`

**Tests needed**:
- `test_complete_location_workflow()` - Create location → add buildings → add travel links → fetch response
- `test_danger_calculation_with_character()` - Character faction relationships affect danger
- `test_wildlife_affects_travel_danger()` - Wildlife populations increase danger
- `test_location_hierarchy_with_travel()` - Parent-child locations with connections

## Test Data Factories

Create helper functions in `tests/factories.py`:

```python
async def create_test_location_with_full_data(db: AsyncSession):
    """Create a location with buildings, resources, travel connections, wildlife."""
    location = await create_test_location(db)
    
    # Add buildings
    building = await create_test_building(db, location_id=location.id)
    
    # Add resources
    resource = await create_test_resource_instance(db, location_id=location.id)
    
    # Add resource nodes  
    node = await create_test_resource_node(db, location_id=location.id)
    
    # Add travel connections
    destination = await create_test_location(db)
    travel_link = await create_test_travel_link(db, location.id, destination.id)
    
    # Add wildlife
    wildlife = await create_test_wildlife(db, location_id=location.id)
    
    return location

async def create_test_travel_link(db: AsyncSession, from_id: UUID, to_id: UUID):
    """Create a test travel link with biomes and factions."""
    biome = await create_test_biome(db)
    faction = await create_test_faction(db)
    
    link = TravelLink(
        from_location_id=from_id,
        to_location_id=to_id,
        name="Test Route",
        speed=1.2,
        path_type="road",
        terrain_modifier=0.9,
        base_danger_level=3,
        biome_ids=[biome.id],
        faction_ids=[faction.id]
    )
    
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link
```

## Running Tests

### CI/CD Pipeline (GitHub Actions)
```bash
# Fast unit tests only (no database)
pytest tests/unit/ -v --tb=short

# With coverage for CI reporting
pytest tests/unit/ --cov=app/db/models --cov=app/api/schemas --cov=app/game_state/services -v
```

### Local Development
```bash
# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests (requires DB)
pytest tests/integration/ -v

# Migration tests (deployment validation)
pytest tests/migration/ -v

# All tests (full suite)
pytest tests/ -v

# Specific test categories
pytest tests/unit/models/ -v                    # Model logic
pytest tests/unit/schemas/ -v                   # Schema validation
pytest tests/unit/services/ -v                  # Business logic
pytest tests/integration/test_api_endpoints.py -v   # API tests
```

### GitHub Actions Configuration
```yaml
# .github/workflows/test.yml
name: Unit Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run unit tests
        run: pytest tests/unit/ --cov=app -v
```

## Test Implementation Priority

### Phase 1: CI/CD Foundation (Week 1)
**Focus**: Fast, reliable tests for every PR

1. **`tests/unit/models/test_location_instance.py`** - Model instantiation
2. **`tests/unit/models/test_wildlife.py`** - Danger calculation logic
3. **`tests/unit/schemas/test_location_schemas.py`** - Response structure
4. **`tests/unit/schemas/test_building_schemas.py`** - Building schema validation

### Phase 2: Business Logic (Week 2)  
**Focus**: Core functionality validation

5. **`tests/unit/services/test_location_service.py`** - Service logic (mocked)
6. **`tests/unit/services/test_danger_service.py`** - Danger calculations
7. **`tests/unit/utils/test_route_utils.py`** - Response building
8. **`tests/unit/models/test_travel_link.py`** - Travel link logic

### Phase 3: Integration (Week 3)
**Focus**: End-to-end workflows (local only)

9. **`tests/integration/test_database_models.py`** - Real DB operations
10. **`tests/integration/test_api_endpoints.py`** - Full API tests
11. **`tests/integration/test_location_workflow.py`** - Complete workflows

### Phase 4: Edge Cases (Ongoing)
**Focus**: Error handling and performance

12. Error handling tests
13. Performance tests for large datasets
14. Migration validation tests

## Quick Start Commands

```bash
# Start with the simplest test
pytest tests/unit/models/test_location_instance.py::test_location_instance_creation -v

# Add schema validation
pytest tests/unit/schemas/test_location_schemas.py::test_location_response_schema -v

# Test business logic
pytest tests/unit/models/test_wildlife.py::test_wildlife_danger_calculation -v

# Run all CI/CD tests
pytest tests/unit/ -v
```

Start with **Phase 1** tests to establish your CI/CD pipeline, then expand to business logic and integration tests as needed.