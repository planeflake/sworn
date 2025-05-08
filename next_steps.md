# Development Plan

## Settlement Management
1. **Build Components**:
   - Settlement Manager - Done (base)
   - Settlement Repository - Done (base)
   - Settlement Service - Done (base)

2. **Develop Routes**:
   - Settlement Routes - Done (base)
   

3. **Test**:
   - Assign Theme to World Route - Done

4. **Create Building Framework**
   - Manager,Service,Repo,Entity
   - Import base buildings for fantasy and post apoc

5. **Create Resource Framework**
   - Manager,Service,Repo,Entity
   - Import base resources for fantasy and post apoc

6. **Create NPC Framework**
   - Manager,Service,Repo,Entity
   - Import base npcs for fantasy and post apoc

## Settlement Details
Flesh out a settlement with:
- Leader
- Buildings
- Resources

## Dependencies
### Required Chains:
- NPC Entity Chain
- Resource Chain
- Building Chain

### Workers:
- NPC Worker
- Settlement Worker

#### Example Worker Methods:
- `npc.find_action`
- `settlement.check_expansion`
- `settlement.check_resources`
- `settlement.find_threats`

## Future Tasks
- Build MCTS (Monte Carlo Tree Search) Base.

Create Core Directories:
Create app/game_state/skills/
Create app/game_state/professions/
Define Skill Definitions:
Create app/game_state/skills/skill_definition.py.
Implement the SkillDefinition dataclass and the SKILL_DEFINITIONS registry as designed previously. Populate with some initial skills relevant to your themes.
Define Base Profession:
Create app/game_state/professions/base.py.
Implement the BaseProfession abstract class, including SKILL_REQUIREMENTS, THEMES, meets_requirements, is_available_in_theme, meets_requirements_from_data and abstract methods like perform_daily_task, get_available_services, get_profession_specific_data, load_profession_specific_data.
Database Schema & Models:
Define ORM Models:
(Optional) If storing skill definitions in DB: Create app/db/models/skill.py (or update existing) for SkillDefinitionModel.
Create app/db/models/profession.py for ProfessionDefinitionModel (name, description, themes, skill_requirements_json, archetype_handler, python_class_override, configuration_data_json).
Create app/db/models/profession_unlock_condition.py for ProfessionUnlockConditionModel (profession_id, unlock_type, unlock_target_id).
Update app/db/models/character.py: Add columns for skills (JSONB/TEXT), learned_professions (JSONB/TEXT), active_profession_names (JSONB/Array/TEXT), max_active_professions (Integer).
Generate Alembic Migration:
Run poetry run alembic revision --autogenerate -m "Add skills and professions tables and character fields" (adjust command as needed for your setup).
Review the generated migration script in app/db/alembic/versions/ to ensure it correctly creates the tables and alters the characters table.
Run poetry run alembic upgrade head to apply the migration.
Populate Profession Definitions (DB or Code):
Decide if profession definitions (requirements, themes, unlock methods, configuration for generic handlers) will live primarily in the database or be defined alongside their Python classes.
If DB: Create initial data for the professions and profession_unlock_conditions tables (e.g., using a data migration script or manually).
If Code: Define these attributes directly on the concrete profession classes (Step 7).
Phase 2: Domain Entity Integration
Update Character Entity:
Modify app/game_state/entities/character.py.
Add the skills: Dict[str, int] field.
Add the learned_professions, active_profession_names, _active_professions_instances, max_active_professions fields.
Implement skill methods: get_skill_level, set_skill_level, increase_skill.
Implement profession methods: learn_profession (including unlock checks), activate_profession, deactivate_profession, forget_profession, perform_daily_duties, get_all_offered_services.
Update __post_init__ to handle deserialization of active professions.
Update get_save_data and from_load_data (or your equivalent serialization/deserialization logic) to handle the new fields.
Create Concrete Professions & Factory:
In app/game_state/professions/, create Python files for specific professions (e.g., innkeeper.py, blacksmith.py).
Implement the classes, inheriting from BaseProfession. Define NAME, DESCRIPTION, SKILL_REQUIREMENTS, THEMES. Implement the abstract methods.
(If definitions are in code) Define unlock conditions/config here too.
Create app/game_state/professions/factory.py. Implement PROFESSION_REGISTRY and the create_profession factory function (consider the hybrid approach using DB data). Register your concrete classes.
Phase 3: Infrastructure & Services
Update/Create Repositories:
Update app/game_state/repositories/character_repository.py's conversion methods (_convert_to_model, _convert_to_entity or similar) to correctly serialize/deserialize the new JSON/Array fields (skills, learned_professions, active_profession_names) between the domain entity and the ORM model.
Create app/game_state/repositories/profession_definition_repository.py to fetch profession definition data (including unlock conditions) from the database.
Update/Create Services:
Create app/game_state/services/profession_definition_service.py. Inject the new repository and provide methods like async get_definition(profession_name).
Update app/game_state/services/character_service.py:
Inject ProfessionDefinitionService.
Add methods like learn_profession, activate_profession, etc. These methods should:
Load the character entity using CharacterRepository.
Call the corresponding method on the character entity (passing necessary context like learn_method, learn_target_id, world_theme_id, db_session).
Save the updated character entity using CharacterRepository.
Return the result (e.g., updated character API model, boolean success).
Phase 4: API & Testing
Update/Create API Endpoints:
Update app/api/routes/character_routes.py:
Add endpoints for learning, activating, deactivating professions (e.g., POST /characters/{char_id}/professions/{prof_name}/learn).
These endpoints should call the relevant methods in CharacterService.
Consider how unlock context (learn_method, learn_target_id) is passed (e.g., query parameters, request body).
(Optional) Create app/api/routes/profession_routes.py for endpoints like GET /professions (potentially filtered by theme).
Write Unit & Integration Tests:
Test the new methods on the Character entity.
Test the ProfessionDefinitionService and Repository.
Test the new methods in CharacterService (mocking repositories and other services).
Write integration tests for the new API endpoints.
Documentation:
Update any relevant documentation (READMEs, API docs) to reflect the new skill and profession systems.