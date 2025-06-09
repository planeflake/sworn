# Development Plan

## Priorities

✅ **COMPLETED** - Change game state entities from @dataclass to pydantic

## Settlement Management
1. **Build Components**:
   - Settlement Manager - ✅ COMPLETED
   - Settlement Repository - ✅ COMPLETED
   - Settlement Service - ✅ COMPLETED

2. **Develop Routes**:
   - Settlement Routes - ✅ COMPLETED
   
3. **Test**:
   - Assign Theme to World Route - ✅ COMPLETED

4. **Create Building Framework** - ✅ COMPLETED
   - Manager, Service, Repo, Entity
   - Building Upgrade Blueprints also implemented

5. **Create Resource Framework** - ✅ COMPLETED
   - Manager, Service, Repo, Entity
   - Resource routes implemented

6. **Create NPC Framework** - ✅ COMPLETED
   - Manager, Service, Repo, Entity
   - Character routes implemented

## Settlement Details
Flesh out a settlement with:
- Leader - ✅ COMPLETED
- Buildings - ✅ COMPLETED
- Resources - ✅ COMPLETED

## Dependencies
### Required Chains - All Done:
- NPC Entity Chain - ✅ COMPLETED
- Resource Chain - ✅ COMPLETED
- Building Chain - ✅ COMPLETED

### Workers:
- NPC Worker - ⬜️ NOT STARTED
- Settlement Worker - ⚠️ PARTIALLY IMPLEMENTED

#### Example Worker Methods:
- `npc.find_action`
- `settlement.check_expansion`
- `settlement.check_resources`
- `settlement.find_threats`

## Leader-Based Settlement Expansion System

Create a system where settlement leaders make building and expansion decisions based on their character traits (defensive, economic, expansive, etc.):

1. **Character Trait System** - ✅ COMPLETED:
   - ✅ Created character traits in `app/game_state/enums/character.py`
   - ✅ Added traits like DEFENSIVE, ECONOMICAL, EXPANSIVE, CULTURAL
   - ✅ Updated `CharacterEntity` to include a list of traits

2. **Building Categorization** - ✅ COMPLETED:
   - Created `app/game_state/enums/building_attributes.py` with building attribute types
   - Added methods to BuildingBlueprintEntity to work with attributes in metadata
   - Created mapping between character traits and building attributes
   - Created utility script to update existing buildings with attributes

3. **Resource Management** - ✅ COMPLETED:
   - Settlement model has resources field as Dict[str, int] for quantities
   - SettlementEntity has methods for resource management
   - SettlementRepository handles resource operations with DB
   - SettlementService provides resource management API
   - API routes for resource operations implemented

4. **Building Evaluation System** - ✅ COMPLETED:
   - Created `app/game_state/services/building_evaluation_service.py`
   - Implemented trait-based scoring algorithm
   - Created building recommendation system with weighted scoring

5. **Settlement Worker Implementation** - ⚠️ PARTIALLY IMPLEMENTED:
   - ✅ Extended `_expand_settlement_async()` to use BuildingEvaluationService
   - ✅ Added leader trait-based decision-making logic
   - ✅ Updated construct_building to check and deduct resources
   - ✅ Fixed resource dictionary UUID key handling for proper serialization
   - Next steps:
     - Complete resource-aware construction process
     - Implement GET route for retrieving all settlements
     - Add filtering options for settlements by world_id, leader_id
     - Add resource generation to settlement worker cycle

6. **Testing & Integration** - ⬜️ NOT STARTED:
   - Next steps:
     - Create unit tests for trait-based decision making
     - Test with different leader trait combinations
     - Ensure expansion decisions align with leader traits
     - Validate resource management works correctly

## Resource Nodes and Economy System

This is a new major feature to add realistic resource production and economy to settlements.

1. **Resource Nodes Framework** - ⬜️ NOT STARTED:
   - Create DB model for resource nodes (ResourceNode)
   - Add fields: node_id, name, display_name, resource_type_id, base_output, quality, max_capacity
   - Create migration script for the nodes table
   - Create ResourceNodeEntity, Repository, Manager, Service classes
   - Add relationship to settlements (settlement_id foreign key)
   - Create API schema and routes for CRUD operations

2. **Node Types and Variations** - ⬜️ NOT STARTED:
   - Define node types: iron_mine, copper_mine, forest, river, lake, field, etc.
   - Create quality levels for nodes (poor, average, rich, abundant)
   - Implement JSON-based registry for node types in seed data
   - Create scaling factors for base resource production

3. **Resource Node Buildings** - ⬜️ NOT STARTED:
   - Create building blueprints specific to resource nodes:
     - Iron node → Small iron mine → Medium iron mine → Large iron mine
     - Forest → Logging camp → Lumber mill → Advanced lumber mill
   - Add metadata to link buildings with resource nodes
   - Create upgrade paths with resource requirements
   - Add production multipliers to buildings

4. **Population and Profession Effect** - ⬜️ NOT STARTED:
   - Add citizen count tracking in Settlement model
   - Link citizens to professions
   - Create profession-based production modifiers:
     - Miner: base → experienced → expert
     - Lumberjack: base → experienced → expert
   - Add methods to calculate total production based on:
     - Node base output
     - Building multiplier
     - Worker skill level
     - Number of workers assigned

5. **Resource Node Processing Service** - ⬜️ NOT STARTED:
   - Create ResourceNodeProcessorService
   - Implement periodic calculation of resource production
   - Calculate values based on all modifiers
   - Add daily/weekly resource generation
   - Add methods to track and update node depletion over time

6. **Dynamic Resource Events** - ⬜️ NOT STARTED:
   - Create EventEntity, Repository, Manager, Service
   - Add DB model for events affecting resource nodes:
     - Natural disasters (flood, landslide, earthquake)
     - Discoveries (new mineral vein, fertile soil)
     - Seasonal changes (drought, abundant rainfall)
   - Create event effects (boost production, reduce output, reveal new nodes)
   - Implement event trigger and processing system

7. **Economic Production Chain** - ⬜️ NOT STARTED:
   - Implement resource processing chains:
     - Iron ore → Iron ingots → Iron tools
     - Wood → Lumber → Furniture
   - Create buildings for processing chains
   - Add crafting-based professions
   - Implement value-added calculations

8. **API & Testing** - ⬜️ NOT STARTED:
   - Create API endpoints for:
     - Resource node CRUD operations
     - Resource production statistics
     - Assigning workers to nodes
     - Viewing production chains
     - Resource events
   - Create unit tests for resource production
   - Create integration tests for production chains

## 🎉 MAJOR MILESTONE COMPLETED: Pydantic Migration

### ✅ **COMPLETED** - Complete Dataclass to Pydantic Migration:
- ✅ All Managers (6/6) migrated to Pydantic entities
- ✅ All Repositories (16/16) migrated to Pydantic entities  
- ✅ All Services (15/15) migrated to Pydantic entities
- ✅ Legacy cleanup completed - removed 10+ unused dataclass entity files
- ✅ Updated all entity module imports to prioritize Pydantic entities
- ✅ Added graceful degradation for backward compatibility
- ✅ Updated migration documentation with completion status

### 🎯 Benefits Achieved:
- Better validation and type safety throughout the codebase
- Automatic JSON schema generation for API documentation
- Consistent API schema design across all endpoints
- Future-proof architecture ready for further enhancements

**CURRENT PRIORITY:** 
1. **CRITICAL: Service Layer Architecture Consistency** - Fix remaining services to return API schemas instead of domain entities
2. Complete Settlement Worker Implementation with Resource Generation 
3. Implement Resource Nodes Framework for Resource Generation
4. Implement GET All Settlements Route with Filtering
5. Implement Zone Entity for Geographic Organization
6. Restructure DB Models for Better Organization
7. Implement Character Traits System

## 🚨 CRITICAL: Service Layer Architecture Inconsistencies

### ✅ **COMPLETED** - Services Following Correct Pattern:
- theme_service.py ✅
- biome_service.py ✅  
- settlement_service.py ✅
- profession_service.py ✅
- resource_service.py ✅
- character_service.py ✅
- building_instance_service.py ✅
- building_upgrade_blueprint_service.py ✅

### 🔥 **URGENT FIXES NEEDED** - Services Returning Domain Entities Instead of API Schemas:

**Major Refactors Required:**

1. **location/location_service.py** - ALL methods return `LocationEntityPydantic` instead of `LocationResponse`
   - `get_location()` → Should return `LocationResponse`
   - `get_locations_by_type_id()` → Should return `List[LocationResponse]`
   - `get_locations_by_type_code()` → Should return `List[LocationResponse]`
   - `get_children()` → Should return `List[LocationResponse]`
   - `create_location()` → Should return `LocationResponse`
   - `update_location()` → Should return `Optional[LocationResponse]`
   - `get_location_with_full_data()` → Should return `Optional[LocationResponse]`

2. **location/location_type_service.py** - ALL methods return `LocationTypeEntityPydantic` instead of `LocationTypeResponse`
   - `get_type()` → Should return `LocationTypeResponse`
   - `get_type_by_code()` → Should return `LocationTypeResponse`
   - `get_all_types()` → Should return `List[LocationTypeResponse]`
   - `create_type()` → Should return `LocationTypeResponse`
   - `update_type()` → Should return `Optional[LocationTypeResponse]`

3. **building_evaluation_service.py** - Returns mixed domain entities
   - `get_settlement_leader()` → Should return `CharacterRead`
   - `get_recommended_buildings()` → Should return `List[Tuple[BuildingBlueprintRead, float]]`

4. **skill_service.py** - ALL methods return `SkillDefinitionEntityPydantic` instead of `SkillDefinitionRead`
   - `get_skill()` → Should return `SkillDefinitionRead`
   - `add_skill()` → Should return `SkillDefinitionRead`
   - `rename_skill()` → Should return `SkillDefinitionRead`
   - **ALSO**: Uses HTTPException in service layer (should be in API layer)

**Conversion Pattern Updates Needed:**

5. **building_blueprint_service.py** - Uses complex manual conversion instead of `model_validate(entity.to_dict())`
   - Replace `_convert_entity_to_read_schema` with simple `BuildingBlueprintRead.model_validate(entity.to_dict())`

6. **skill_definition_service.py** - Uses manual field mapping instead of `model_validate(entity.to_dict())`
   - Replace manual dictionary building with `SkillDefinitionRead.model_validate(entity.to_dict())`

**Minor Fixes:**

7. **world_service.py** - Has broken method
   - Fix `get_world()` method that returns `await domain_entity` instead of converting to schema

8. **zone_service.py** - Mixed patterns
   - Standardize to use consistent `_convert_entity_to_read_schema` pattern

9. **pricing_service.py** - Incomplete implementation
   - Complete rewrite needed to follow proper service pattern

### 🎯 **Required Changes Pattern:**
```python
# WRONG (returning domain entity):
async def get_something(self, id: UUID) -> Optional[SomethingEntityPydantic]:
    entity = await self.repository.find_by_id(id)
    return entity

# CORRECT (returning API schema):
async def get_something(self, id: UUID) -> Optional[SomethingRead]:
    entity = await self.repository.find_by_id(id)
    if entity:
        return SomethingRead.model_validate(entity.to_dict())
    return None
```

### 📝 **Action Items:**
1. Update all location services (highest priority - most used)
2. Fix building_evaluation_service.py 
3. Update skill_service.py
4. Simplify conversion methods in building_blueprint_service.py and skill_definition_service.py
5. Fix world_service.py broken method
6. Standardize zone_service.py patterns
7. Rewrite pricing_service.py

## Character Traits System Implementation

Expand the character traits system to influence settlement decision-making:

1. **Trait API Implementation** - ⬜️ NOT STARTED:
   - Create API schema for character traits in app/api/schemas/character.py
   - Add trait fields to character creation/update schemas
   - Implement API endpoints for viewing and managing character traits
   - Add validation to ensure only valid traits from CharacterTraitEnum are used
   - Create route for assigning traits to characters
   - Create route for reading a character's traits

2. **Trait Service Layer** - ⬜️ NOT STARTED:
   - Add trait methods to CharacterService
   - Implement methods for adding/removing traits
   - Create utility methods for checking trait compatibility
   - Add methods to get characters with specific traits
   - Create helper functions for trait-based calculations

3. **Settlement Leader Trait Analysis** - ⬜️ NOT STARTED:
   - Create TraitAnalysisService for leader behavior prediction
   - Implement trait-based priority scoring
   - Create methods to calculate leader preferences based on traits
   - Add trait weighting system for different decision types
   - Implement conflict resolution when traits suggest contradictory actions

4. **Settlement Worker Trait Integration** - ⬜️ NOT STARTED:
   - Update settlement worker to use leader traits for decisions
   - Modify expansion logic to account for leader preferences
   - Adjust resource allocation based on leader traits
   - Implement trait-based building selection logic
   - Create trait-influenced risk assessment for settlement actions
   - Add trait-based logging to document leader decisions

5. **Testing & Validation** - ⬜️ NOT STARTED:
   - Create unit tests for trait-based decisions
   - Test with different trait combinations to ensure balanced outcomes
   - Implement validation for trait decision weights
   - Add integration tests for end-to-end trait workflow

## Event System

1. **Event Framework** - ⬜️ NOT STARTED:
   - Create DB model for events
   - Add fields: event_id, event_type, name, description, duration, effects
   - Create migration script for events table
   - Create EventEntity, Repository, Manager, Service
   - Add effects storage using JSONB
   - Create API schema and routes for events

2. **Event Types** - ⬜️ NOT STARTED:
   - Create event categories:
     - Natural: weather, disasters, discoveries
     - Social: festivals, celebrations, unrest
     - Economic: trade opportunity, resource scarcity
     - Military: bandit raids, faction conflicts
   - Create seed data for base events

3. **Event Processing System** - ⬜️ NOT STARTED:
   - Create EventProcessorService
   - Implement event generation based on settlement properties
   - Add event resolution logic
   - Implement consequences (resource changes, population effects)
   - Create decision points for player/NPC leaders

4. **Integration with Leader Traits** - ⬜️ NOT STARTED:
   - Connect event response options to leader traits
   - Add trait-based outcome modifiers
   - Implement leader decision simulation for NPCs

5. **API & UI Integration** - ⬜️ NOT STARTED:
   - Create API endpoints for event system
   - Implement event notification system
   - Create endpoints for event responses

## Skills and Professions Implementation
SkillDefinition components are partially implemented, but still need:

1. **Create Core Directory Structure**:
   - Create app/game_state/skills/
   - Create app/game_state/professions/

2. **Consolidate Skill Definitions**:
   - Create app/game_state/skills/skill_definition.py
   - Implement the SkillDefinition dataclass and SKILL_DEFINITIONS registry
   - Populate with initial skills relevant to your themes

3. **Define Base Profession**:
   - Create app/game_state/professions/base.py
   - Implement BaseProfession abstract class with:
     - SKILL_REQUIREMENTS, THEMES
     - Methods: meets_requirements, is_available_in_theme
     - Abstract methods: perform_daily_task, get_available_services

4. **Database Integration**:
   - Update app/db/models/character.py with fields for:
     - skills (JSONB/TEXT)
     - learned_professions (JSONB/TEXT)
     - active_profession_names (JSONB/Array/TEXT)
     - max_active_professions (Integer)
   - Generate and run Alembic migration

5. **Profession Implementation**:
   - Create concrete profession classes
   - Implement profession factory
   - Define profession unlock conditions

6. **Character Integration**:
   - Update CharacterEntity with skill and profession fields
   - Implement skill methods: get_skill_level, set_skill_level, increase_skill
   - Implement profession methods: learn_profession, activate_profession

7. **API & Testing**:
   - Implement profession API endpoints
   - Write unit tests for skill/profession functionality
   - Create integration tests

## DB Model Restructuring

1. **Reorganize Models by Domain** - ⬜️ NOT STARTED:
   - Restructure the flat models directory into domain-based folders:
     ```
     app/db/models/
     ├── __init__.py
     ├── base.py
     ├── world/
     │   ├── __init__.py   # Export World, ThemeDB, Biome, Season
     │   ├── world.py
     │   ├── theme.py
     │   ├── biome.py
     │   └── season.py
     ├── settlement/
     │   ├── __init__.py   # Export Settlement, BuildingInstanceDB
     │   ├── settlement.py
     │   └── building_instance.py
     ```
   - Update import statements throughout the codebase
   - Create test migrations to verify structure integrity
   - Document new model organization in README or docs

2. **Standardize Model Patterns** - ⬜️ NOT STARTED:
   - Create consistent patterns for model relationships
   - Establish naming conventions for tables, columns, and relationships
   - Move association tables to appropriate domain folders
   - Review and fix any circular import issues

## Resource Nodes Implementation

### ✅ **COMPLETED:**
- ✅ **Database Model**: `app/db/models/resources/resource_node.py` exists
- ✅ **Pydantic Entities**: `app/game_state/entities/resource/resource_node_pydantic.py` with `ResourceNodeEntityPydantic` and `ResourceNodeResourceEntityPydantic`

### 🔄 **MISSING Components for API Routes:**

1. **Resource Node Repository** - ⬜️ NOT STARTED:
   - Create `app/game_state/repositories/resource_node_repository.py`
   - Extend `BaseRepository[ResourceNodeEntityPydantic, ResourceNode, UUID]`
   - Include CRUD operations and specialized queries for resource node discovery/production

2. **Resource Node Manager** - ⬜️ NOT STARTED:
   - Create `app/game_state/managers/resource_node_manager.py`
   - Business logic for creating/managing resource nodes
   - Node discovery mechanics, production calculations
   - Follow established manager patterns from building/character managers

3. **Resource Node Service** - ⬜️ NOT STARTED:
   - Create `app/game_state/services/resource_node_service.py`
   - Convert between entities and API schemas
   - Handle business operations (discovery, production, depletion)
   - Follow pattern from `BuildingBlueprintService`

4. **API Schemas** - ⬜️ NOT STARTED:
   - Create `app/api/schemas/resource_node_schema.py`
   - Define `ResourceNodeCreate`, `ResourceNodeRead`, `ResourceNodeUpdate`
   - Include nested resource entity schemas
   - Follow pattern from `building_blueprint_schema.py`

5. **API Routes** - ⬜️ NOT STARTED:
   - Create `app/api/routes/resource_node_routes.py`
   - Standard REST endpoints (GET, POST, PUT, DELETE)
   - Include specialized endpoints for discovery/production operations
   - Follow established routing patterns

6. **Route Registration** - ⬜️ NOT STARTED:
   - Add resource node router to `app/api/fastapi.py`
   - Register endpoints with proper tags and documentation

**Priority**: Resource Node API components should be implemented in dependency order: Repository → Manager → Service → Schemas → Routes → Registration

## Zone Entity Implementation

1. **Zone Model** - ⬜️ NOT STARTED:
   - Create DB model in `app/db/models/world/zone.py`:
     ```python
     class Zone(Base):
         __tablename__ = "zones"
         
         id = Column(pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
         world_id = Column(pgUUID(as_uuid=True), ForeignKey("worlds.id"), nullable=False)
         name = Column(String(100), nullable=False)
         description = Column(Text, nullable=True)
         zone_type = Column(String(50), nullable=False)  # forest, mountain, plains, etc.
         biome_id = Column(pgUUID(as_uuid=True), ForeignKey("biomes.id"), nullable=True)
         difficulty = Column(Integer, nullable=False, default=1)
         discovered = Column(Boolean, nullable=False, default=False)
         coordinates = Column(JSONB, nullable=True)  # Store x, y coordinates
         size = Column(Integer, nullable=False, default=100)  # Size in arbitrary units
         created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
         updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
     ```
   - Create ZoneEntity, Repository, Service, and API components
   - Add relationship to resource nodes (zones contain resource nodes)
   - Create exploration and discovery mechanics

2. **Zone-Settlement Relationship** - ⬜️ NOT STARTED:
   - Create association table for settlements' zone control
   - Implement mechanics for zone influence and control
   - Add zone-based events and encounters

## Repository Improvements

1. **Base Repository Enhancements** - ⬜️ NOT STARTED:
   - Add common lookup methods to BaseRepository to reduce code duplication:
     - `find_by_name(name: str) -> Optional[EntityType]`
     - `find_all_by_name(name: str) -> List[EntityType]` (for partial matches)
     - `find_by_field_list(field_name: str, values: List[Any]) -> List[EntityType]`
     - `find_by_multiple_fields(field_values: Dict[str, Any]) -> List[EntityType]`
   - Add bulk operation methods:
     - `bulk_save(entities: List[EntityType]) -> List[EntityType]`
     - `bulk_delete(entity_ids: List[PrimaryKeyType]) -> int` (returns count deleted)
   - Implement caching mechanisms for frequently accessed entities
   - Add better error handling and detailed logging
   - Create utility methods for common repository operations
   - Add query builder methods to construct complex queries

2. **Repository Unit Tests** - ⬜️ NOT STARTED:
   - Create comprehensive test suite for BaseRepository
   - Test all CRUD operations with various entity types
   - Test edge cases like missing fields and invalid data
   - Add performance tests for bulk operations
   - Test caching mechanisms

## Future Tasks
- Build MCTS (Monte Carlo Tree Search) Base for decision making
- Implement factions and inter-settlement relations
- Create trade routes and economy simulation
- Add diplomacy and alliance systems
- Probalistic Yield Modelling