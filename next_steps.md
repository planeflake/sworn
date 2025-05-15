# Development Plan

## Settlement Management
1. **Build Components**:
   - Settlement Manager - Done
   - Settlement Repository - Done
   - Settlement Service - Done

2. **Develop Routes**:
   - Settlement Routes - Done
   
3. **Test**:
   - Assign Theme to World Route - Done

4. **Create Building Framework** - Done
   - Manager, Service, Repo, Entity
   - Building Upgrade Blueprints also implemented

5. **Create Resource Framework** - Done
   - Manager, Service, Repo, Entity
   - Resource routes implemented

6. **Create NPC Framework** - Done
   - Manager, Service, Repo, Entity
   - Character routes implemented

## Settlement Details
Flesh out a settlement with:
- Leader
- Buildings
- Resources

## Dependencies
### Required Chains - All Done:
- NPC Entity Chain - Done
- Resource Chain - Done
- Building Chain - Done

### Workers:
- NPC Worker
- Settlement Worker - Partially Implemented

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

3. **Resource Management** - ⚠️ PARTIALLY IMPLEMENTED:
   - Settlement model has resources field
   - Next steps:
     - Extend `SettlementService` with specific resource tracking methods
     - Add `get_available_resources()` method
     - Add `can_afford_building()` method to check requirements

4. **Building Evaluation System** - ✅ COMPLETED:
   - Created `app/game_state/services/building_evaluation_service.py`
   - Implemented trait-based scoring algorithm
   - Created building recommendation system with weighted scoring

5. **Settlement Worker Implementation** - ⚠️ PARTIALLY IMPLEMENTED:
   - Extended `_expand_settlement_async()` to use BuildingEvaluationService
   - Added leader trait-based decision-making logic
   - Next steps:
     - Implement building construction process
     - Add resource deduction when buildings are constructed

6. **Testing & Integration** - ⬜️ NOT STARTED:
   - Next steps:
     - Create unit tests for trait-based decision making
     - Test with different leader trait combinations
     - Ensure expansion decisions align with leader traits
     - Validate resource management works correctly

**CURRENT PRIORITY:** Complete Building Categorization (#2) and start Building Evaluation Service (#4)

## Future Tasks
- Build MCTS (Monte Carlo Tree Search) Base.

### Skills and Professions Implementation
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