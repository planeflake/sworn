import requests
import json
import uuid
import time
from typing import Optional

# --- Configuration ---
BASE_API_URL = "http://localhost:8000/api/v1"
UPGRADE_BLUEPRINTS_ENDPOINT = f"{BASE_API_URL}/building-upgrade-blueprints/"
RESOURCES_ENDPOINT = f"{BASE_API_URL}/resources/"
PROFESSIONS_ENDPOINT = f"{BASE_API_URL}/professions/"
THEMES_ENDPOINT = f"{BASE_API_URL}/themes/"
TECHNOLOGIES_ENDPOINT = f"{BASE_API_URL}/technologies/" # Placeholder

# --- Known UUIDs ---
FANTASY_THEME_ID = "dfba10ac-eaa7-4f83-977d-def25746dfb5"
FANTASY_THEME_NAME = "Fantasy Medieval" # Assuming this is the name associated with the ID

# --- Helper Function to Get or Create an Entity ---
def get_or_create_entity_id(
    endpoint: str,
    entity_name: str, # This is the value we'll search for in the 'name_field'
    payload_create_func,
    name_field: str = "name",
    id_field: str = "id", # The field name in the response that holds the ID
    target_id_for_creation: Optional[str] = None # If we want to suggest an ID during creation
) -> str:
    """
    Tries to find an entity by its name. If not found, creates it.
    Returns the entity's ID (UUID string).
    """
    try:
        print(f"  Ensuring '{entity_name}' ({name_field}) exists at {endpoint}...")
        # Attempt to find by name (more efficient if API supports it)
        # Example: response = requests.get(f"{endpoint}?name={entity_name}")
        # If not, get all and filter:
        response = requests.get(endpoint)
        response.raise_for_status()
        all_entities_data = response.json()

        entity_list = []
        # Adjust based on your list endpoint response structure
        for key_to_check in ["items", "resources", "professions", "themes", "technologies"]:
            if isinstance(all_entities_data, dict) and isinstance(all_entities_data.get(key_to_check), list):
                entity_list = all_entities_data[key_to_check]
                break
        if not entity_list and isinstance(all_entities_data, list): # Direct list response
            entity_list = all_entities_data

        found_entity = None
        for entity in entity_list:
            if entity.get(name_field) == entity_name:
                found_entity = entity
                break

        if found_entity:
            entity_id_val = found_entity.get(id_field)
            if entity_id_val:
                print(f"    Found '{entity_name}' with ID: {entity_id_val}")
                # If we have a target ID, verify it matches (especially for the theme)
                if target_id_for_creation and str(entity_id_val) != target_id_for_creation:
                    print(f"    WARNING: Found '{entity_name}' but ID {entity_id_val} does not match target {target_id_for_creation}.")
                    # Decide how to handle: raise error, use found, or try to update (complex)
                    # For now, we'll prefer the found ID if the name matches.
                return str(entity_id_val)
            else:
                print(f"    WARNING: Found '{entity_name}' but it has no '{id_field}' field. Data: {found_entity}")
        
        # If not found, create it
        print(f"    '{entity_name}' not found. Attempting to create...")
        create_payload = payload_create_func()
        
        # If a target_id_for_creation is provided, and your API supports it, include it
        # This is often NOT supported for user-facing create endpoints but useful for seeding.
        # For now, we assume the create payload function already includes it if needed.
        # If your POST endpoint allows specifying an ID (e.g., for the Theme):
        if target_id_for_creation and 'id' not in create_payload and endpoint == THEMES_ENDPOINT: # Special handling for theme
             print(f"    Attempting to create theme '{entity_name}' with specific ID: {target_id_for_creation}")
             # This part depends HEAVILY on whether your POST /themes/ endpoint accepts an 'id'
             # If it doesn't, you can't force the ID. You'd have to create it, then GET it by name to confirm its ID.
             # For simplicity, we'll assume we try and if it fails, we proceed without forcing ID.
             payload_with_id = {**create_payload, "id": target_id_for_creation}
             response_create = requests.post(endpoint, json=payload_with_id)
             if response_create.status_code != 201: # If creation with specific ID failed
                 print(f"    WARN: Creation of '{entity_name}' with specific ID {target_id_for_creation} failed (Status {response_create.status_code}). Trying without specific ID.")
                 response_create = requests.post(endpoint, json=create_payload) # Try without ID
        else:
            response_create = requests.post(endpoint, json=create_payload)


        if response_create.status_code == 201:
            created_data = response_create.json()
            entity_id_val = created_data.get(id_field)
            if entity_id_val:
                print(f"    Successfully created '{entity_name}' with ID: {entity_id_val}")
                if target_id_for_creation and str(entity_id_val) != target_id_for_creation:
                     print(f"    WARNING: Created '{entity_name}' but resulting ID {entity_id_val} does not match target {target_id_for_creation}.")
                return str(entity_id_val)
            else:
                raise Exception(f"Creation of '{entity_name}' succeeded but response lacked an '{id_field}'. Response: {created_data}")
        else:
            error_detail = response_create.json().get("detail", response_create.text) if response_create.content else "No content"
            raise Exception(f"Failed to create '{entity_name}' (Status {response_create.status_code}): {error_detail}")

    except requests.exceptions.RequestException as e:
        print(f"  ERROR connecting to API for '{entity_name}' at {endpoint}: {e}")
        raise
    except Exception as e:
        print(f"  ERROR processing '{entity_name}': {e}")
        raise

# --- Resource Payloads (now use FANTASY_THEME_ID) ---
resource_payloads = {
    "Wood": lambda: {"name": "Wood", "description": "Basic building material.", "rarity": "Common", "stack_size": 50, "theme_id": FANTASY_THEME_ID},
    "Stone": lambda: {"name": "Stone", "description": "Common stone.", "rarity": "Common", "stack_size": 50, "theme_id": FANTASY_THEME_ID},
    "Iron Ingot": lambda: {"name": "Iron Ingot", "description": "Refined iron.", "rarity": "Common", "stack_size": 30, "theme_id": FANTASY_THEME_ID},
    "Common Herbs": lambda: {"name": "Common Herbs", "description": "Basic herbs.", "rarity": "Common", "stack_size": 20, "theme_id": FANTASY_THEME_ID},
    "Rare Crystal": lambda: {"name": "Rare Crystal", "description": "A magical crystal.", "rarity": "Rare", "stack_size": 10, "theme_id": FANTASY_THEME_ID},
    "Food Supplies": lambda: {"name": "Food Supplies", "description": "Basic sustenance.", "rarity": "Common", "stack_size": 100, "theme_id": FANTASY_THEME_ID},
    "Cloth": lambda: {"name": "Cloth", "description": "Woven fabric.", "rarity": "Common", "stack_size": 40, "theme_id": FANTASY_THEME_ID},
}

# --- Profession Payloads (now use FANTASY_THEME_ID in available_theme_ids) ---
profession_payloads = {
    "Mason": lambda: {"name": "mason", "display_name": "Mason", "description": "Skilled in stonework.", "category": "CRAFTING", "available_theme_ids": [FANTASY_THEME_ID]},
    "Carpenter": lambda: {"name": "carpenter", "display_name": "Carpenter", "description": "Skilled in woodwork.", "category": "CRAFTING", "available_theme_ids": [FANTASY_THEME_ID]},
    "Engineer": lambda: {"name": "engineer", "display_name": "Engineer", "description": "Builds complex contraptions.", "category": "CRAFTING", "available_theme_ids": [FANTASY_THEME_ID]},
    "Alchemist": lambda: {"name": "alchemist", "display_name": "Alchemist", "description": "Brews potions.", "category": "CRAFTING", "available_theme_ids": [FANTASY_THEME_ID]},
    "Cook": lambda: {"name": "cook", "display_name": "Cook", "description": "Prepares food.", "category": "SERVICE", "available_theme_ids": [FANTASY_THEME_ID]},
    "Scholar": lambda: {"name": "scholar", "display_name": "Scholar", "description": "Researches knowledge.", "category": "KNOWLEDGE", "available_theme_ids": [FANTASY_THEME_ID]},
    "Farmer": lambda: {"name": "farmer", "display_name": "Farmer", "description": "Cultivates crops.", "category": "GATHERING", "available_theme_ids": [FANTASY_THEME_ID]},
}

# --- Technology Payloads (now use FANTASY_THEME_ID) ---
technology_payloads = {
    "Advanced Masonry": lambda: {"name": "Advanced Masonry", "description": "Improved stone working.", "theme_id": FANTASY_THEME_ID}, # Assuming tech has theme_id
    "Siege Engineering": lambda: {"name": "Siege Engineering", "description": "Building siege engines.", "theme_id": FANTASY_THEME_ID},
    "Culinary Arts": lambda: {"name": "Culinary Arts", "description": "Advanced cooking.", "theme_id": FANTASY_THEME_ID},
    "Basic Fortifications": lambda: {"name": "Basic Fortifications", "description": "Simple defenses.", "theme_id": FANTASY_THEME_ID},
    "Advanced Agriculture": lambda: {"name": "Advanced Agriculture", "description": "Better farming techniques.", "theme_id": FANTASY_THEME_ID}, # New
    "Alchemy Fundamentals": lambda: {"name": "Alchemy Fundamentals", "description": "Basic alchemical knowledge.", "theme_id": FANTASY_THEME_ID}, # New
}

# --- Building Blueprint Placeholders ---
# These should ideally also be fetched/created via API in a more complete seeder
WATCHTOWER_LVL1_BP_ID = str(uuid.uuid4()) # Keep as placeholder for now
WATCHTOWER_LVL2_BP_ID = str(uuid.uuid4())
STONE_TOWER_BP_ID = str(uuid.uuid4())
TAVERN_LVL1_BP_ID = str(uuid.uuid4())
TAVERN_LVL2_BP_ID = str(uuid.uuid4())
LIBRARY_BP_ID = str(uuid.uuid4())
FARM_BP_ID = str(uuid.uuid4())
MARKET_BP_ID = str(uuid.uuid4())
# Example of a blueprint that might use a tag for targeting upgrades
ALCHEMIST_LAB_BP_ID = str(uuid.uuid4()) # Assuming this exists and has a subtype tag "ALCHEMIST_LAB"

# --- Main Seeding Logic ---
def get_upgrade_blueprint_definitions(resource_ids, profession_ids, tech_ids):
    # (Same as before, using the fetched/created IDs)
    return [
        {
            "name": "wt_arrow_slits_wood", "display_name": "Wooden Arrow Slits",
            "description": "Adds basic arrow slits to a wooden watchtower.",
            "target_blueprint_criteria": {"base_blueprint_id": WATCHTOWER_LVL1_BP_ID},
            "prerequisites": {},
            "resource_cost": {resource_ids["Wood"]: 30, resource_ids["Iron Ingot"]: 5}, # Changed Iron to Iron Ingot
            "profession_cost": {profession_ids["Carpenter"]: 1},
            "duration_days": 1, "effects": {"defense_bonus": 3, "garrison_slots": 1}, "is_initial_choice": True,
        },
        # ... (rest of your upgrade definitions using keys from resource_ids, profession_ids, tech_ids)
        {
            "name": "wt_reinforced_structure_wood", "display_name": "Reinforced Wooden Structure",
            "description": "Strengthens the wooden frame of the watchtower.",
            "target_blueprint_criteria": {"base_blueprint_id": WATCHTOWER_LVL1_BP_ID, "min_instance_level": 1},
            "prerequisites": {},
            "resource_cost": {resource_ids["Wood"]: 75, resource_ids["Iron Ingot"]: 10},
            "profession_cost": {profession_ids["Carpenter"]: 2},
            "duration_days": 2, "effects": {"max_hp_bonus": 100}, "is_initial_choice": False,
        },
        {
            "name": "wt_stone_foundation", "display_name": "Stone Foundation",
            "description": "Replaces the wooden foundation with a sturdier stone one.",
            "target_blueprint_criteria": {"base_blueprint_id": WATCHTOWER_LVL2_BP_ID}, # Assumes WT Lvl 2 exists
            "prerequisites": {"required_tech_id": tech_ids.get("Advanced Masonry", str(uuid.uuid4()))},
            "resource_cost": {resource_ids["Stone"]: 100, resource_ids["Wood"]: 20},
            "profession_cost": {profession_ids["Mason"]: 2, profession_ids["Carpenter"]: 1},
            "duration_days": 3, "effects": {"max_hp_bonus": 150, "stability_increase": 1}, "is_initial_choice": False,
        },
        {
            "name": "wt_ballista_emplacement", "display_name": "Ballista Emplacement",
            "description": "Adds a mount for a light ballista on the watchtower.",
            "target_blueprint_criteria": {"base_blueprint_id": STONE_TOWER_BP_ID}, # For sturdier stone towers
            "prerequisites": {"required_tech_id": tech_ids.get("Siege Engineering", str(uuid.uuid4())), "min_instance_level": 2},
            "resource_cost": {resource_ids["Wood"]: 100, resource_ids["Iron Ingot"]: 50},
            "profession_cost": {profession_ids["Engineer"]: 1, profession_ids["Carpenter"]: 2},
            "duration_days": 5, "effects": {"unlocks_weapon_slot": "ballista", "area_control_bonus": 5}, "is_initial_choice": False,
        },
        {
            "name": "wt_signal_fire_beacon", "display_name": "Signal Fire Beacon",
            "description": "Installs a beacon for long-range communication.",
            "target_blueprint_criteria": {"blueprint_tag": "watchtower_type"},
            "prerequisites": {},
            "resource_cost": {resource_ids["Wood"]: 40, resource_ids["Rare Crystal"]: 1},
            "profession_cost": {profession_ids["Carpenter"]: 1},
            "duration_days": 1, "effects": {"unlocks_ability": "send_signal", "communication_range_increase": 100}, "is_initial_choice": True,
        },
        {
            "name": "tavern_expanded_seating", "display_name": "Expanded Seating",
            "description": "Adds more tables and chairs to the tavern's common room.",
            "target_blueprint_criteria": {"base_blueprint_id": TAVERN_LVL1_BP_ID},
            "prerequisites": {},
            "resource_cost": {resource_ids["Wood"]: 50},
            "profession_cost": {profession_ids["Carpenter"]: 1},
            "duration_days": 2, "effects": {"max_patron_capacity_increase": 10, "comfort_bonus": 1}, "is_initial_choice": True,
        },
        {
            "name": "tavern_sturdy_cellar", "display_name": "Sturdy Cellar",
            "description": "Reinforces the cellar for better storage of ales and provisions.",
            "target_blueprint_criteria": {"base_blueprint_id": TAVERN_LVL1_BP_ID, "min_instance_level": 1},
            "prerequisites": {},
            "resource_cost": {resource_ids["Stone"]: 70, resource_ids["Wood"]: 30},
            "profession_cost": {profession_ids["Mason"]: 1, profession_ids["Carpenter"]: 1},
            "duration_days": 3, "effects": {"storage_capacity_increase": {"ales": 50, "food": 20}, "preservation_bonus": 0.05}, "is_initial_choice": False,
        },
        {
            "name": "tavern_kitchen_upgrade", "display_name": "Improved Kitchen",
            "description": "Upgrades kitchen facilities, allowing for better quality food and more variety.",
            "target_blueprint_criteria": {"base_blueprint_id": TAVERN_LVL2_BP_ID},
            "prerequisites": {"required_tech_id": tech_ids.get("Culinary Arts", str(uuid.uuid4()))},
            "resource_cost": {resource_ids["Iron Ingot"]: 40, resource_ids["Wood"]: 20, resource_ids["Stone"]: 10},
            "profession_cost": {profession_ids["Cook"]: 1, profession_ids["Carpenter"]: 1},
            "duration_days": 4, "effects": {"unlocks_recipes": ["hearty_stew", "fine_ale"], "food_quality_bonus": 1}, "is_initial_choice": False,
        },
        {
            "name": "tavern_bard_stage", "display_name": "Bard's Stage",
            "description": "Constructs a small stage for performers, increasing renown.",
            "target_blueprint_criteria": {"base_blueprint_id": TAVERN_LVL1_BP_ID},
            "prerequisites": {"min_instance_level": 2},
            "resource_cost": {resource_ids["Wood"]: 60, resource_ids["Cloth"]: 20},
            "profession_cost": {profession_ids["Carpenter"]: 2},
            "duration_days": 2, "effects": {"renown_per_day_increase": 5, "entertainment_value": 10}, "is_initial_choice": True,
        },
        {
            "name": "library_expanded_archives", "display_name": "Expanded Archives",
            "description": "Increases the storage capacity for scrolls and books.",
            "target_blueprint_criteria": {"base_blueprint_id": LIBRARY_BP_ID},
            "prerequisites": {},
            "resource_cost": {resource_ids["Wood"]: 150, resource_ids["Cloth"]: 50},
            "profession_cost": {profession_ids["Carpenter"]: 2, profession_ids["Scholar"]: 1},
            "duration_days": 5, "effects": {"research_points_max_increase": 1000, "knowledge_storage_bonus": 1}, "is_initial_choice": True,
        },
        {
            "name": "library_alchemical_study", "display_name": "Alchemical Study Nook",
            "description": "Adds a dedicated area for alchemical research.",
            "target_blueprint_criteria": {"base_blueprint_id": LIBRARY_BP_ID},
            "prerequisites": {"required_tech_id": tech_ids.get("Alchemy Fundamentals", str(uuid.uuid4()))},
            "resource_cost": {resource_ids["Wood"]: 50, resource_ids["Rare Crystal"]: 5, resource_ids["Common Herbs"]: 20},
            "profession_cost": {profession_ids["Alchemist"]: 1, profession_ids["Scholar"]: 1},
            "duration_days": 4, "effects": {"unlocks_research_category": "alchemy", "research_speed_alchemy_bonus": 0.1}, "is_initial_choice": False,
        },
        {
            "name": "farm_irrigation_system", "display_name": "Basic Irrigation",
            "description": "Improves crop yield through a simple irrigation system.",
            "target_blueprint_criteria": {"base_blueprint_id": FARM_BP_ID},
            "prerequisites": {},
            "resource_cost": {resource_ids["Wood"]: 70, resource_ids["Iron Ingot"]: 15},
            "profession_cost": {profession_ids["Carpenter"]: 1, profession_ids["Farmer"]: 1},
            "duration_days": 3, "effects": {"crop_yield_bonus": 0.10}, "is_initial_choice": True,
        },
        {
            "name": "farm_larger_fields", "display_name": "Expand Fields",
            "description": "Increases the arable land of the farm.",
            "target_blueprint_criteria": {"base_blueprint_id": FARM_BP_ID},
            "prerequisites": {"required_tech_id": tech_ids.get("Advanced Agriculture", str(uuid.uuid4()))},
            "resource_cost": {resource_ids["Wood"]: 30, resource_ids["Food Supplies"]: 50},
            "profession_cost": {profession_ids["Farmer"]: 2},
            "duration_days": 4, "effects": {"production_slots_increase": 2, "food_output_base_increase": 10}, "is_initial_choice": False,
        },
        {
            "name": "market_additional_stalls", "display_name": "Additional Market Stalls",
            "description": "Builds more stalls, allowing more merchants or goods.",
            "target_blueprint_criteria": {"base_blueprint_id": MARKET_BP_ID},
            "prerequisites": {},
            "resource_cost": {resource_ids["Wood"]: 120, resource_ids["Cloth"]: 40},
            "profession_cost": {profession_ids["Carpenter"]: 2},
            "duration_days": 3, "effects": {"merchant_slots_increase": 3, "trade_volume_capacity_increase": 100}, "is_initial_choice": True,
        },
        {
            "name": "market_secure_vault", "display_name": "Secure Vault",
            "description": "Adds a secure vault for storing valuable trade goods and currency.",
            "target_blueprint_criteria": {"base_blueprint_id": MARKET_BP_ID, "min_instance_level": 2},
            "prerequisites": {"required_tech_id": tech_ids.get("Advanced Masonry", str(uuid.uuid4()))},
            "resource_cost": {resource_ids["Stone"]: 200, resource_ids["Iron Ingot"]: 75},
            "profession_cost": {profession_ids["Mason"]: 3, profession_ids["Engineer"]: 1},
            "duration_days": 7, "effects": {"asset_security_bonus": 10, "max_gold_storage_increase": 5000}, "is_initial_choice": False,
        }
    ]

def seed_data():
    print("--- Starting to Seed Building Upgrade Blueprints ---")
    

    # 1. Get/Create Resource IDs
    print("\n--- Ensuring Resources Exist ---")
    resource_ids = {}
    for name, payload_func in resource_payloads.items():
        try:
            # Use 'id' as the id_field for resources based on your ResourceRead schema
            resource_ids[name] = get_or_create_entity_id(RESOURCES_ENDPOINT, name, payload_func, name_field="name", id_field="resource_id")
        except Exception:
            print(f"    FATAL: Could not get or create resource '{name}'. Halting seed for upgrades.")
            return

    # 2. Get/Create Profession Definition IDs
    print("\n--- Ensuring Profession Definitions Exist ---")
    profession_ids = {}
    for name_key, payload_func in profession_payloads.items():
        internal_name = payload_func().get("name", name_key.lower())
        try:
            profession_ids[name_key] = get_or_create_entity_id(PROFESSIONS_ENDPOINT, internal_name, payload_func, name_field="name", id_field="id")
        except Exception:
            print(f"    FATAL: Could not get or create profession '{name_key}'. Halting seed for upgrades.")
            return

    # 3. Get/Create Technology IDs (Optional)
    print("\n--- Ensuring Technologies Exist (Optional) ---")
    tech_ids = {}
    for name, payload_func in technology_payloads.items():
        try:
            # Assuming tech endpoint is similar and returns 'id'
            tech_ids[name] = get_or_create_entity_id(TECHNOLOGIES_ENDPOINT, name, payload_func, name_field="name", id_field="id")
        except Exception as e:
            print(f"    INFO: Could not get or create tech '{name}': {e}. Placeholder UUIDs might be used in blueprints.")
            pass # Continue, allow blueprints to use placeholder UUIDs if tech creation fails

    # 4. Prepare and create upgrade blueprints
    upgrade_blueprints_to_create_data = get_upgrade_blueprint_definitions(resource_ids, profession_ids, tech_ids)

    print(f"\n--- Attempting to Create {len(upgrade_blueprints_to_create_data)} Building Upgrade Blueprints ---")
    successful_creations = 0
    failed_creations = []

    for i, blueprint_payload in enumerate(upgrade_blueprints_to_create_data):
        print(f"\nAttempting to create: {blueprint_payload.get('display_name', blueprint_payload.get('name'))}")
        try:
            response = requests.post(UPGRADE_BLUEPRINTS_ENDPOINT, json=blueprint_payload)
            if response.status_code == 201:
                created_data = response.json()
                print(f"  SUCCESS: {created_data.get('display_name')} created (ID: {created_data.get('id')})")
                successful_creations += 1
            else:
                error_detail = response.json().get("detail", response.text) if response.content else "No content"
                print(f"  FAILURE (Status {response.status_code}): {error_detail}")
                failed_creations.append({"name": blueprint_payload.get('name'), "status_code": response.status_code, "detail": error_detail})
        except requests.exceptions.ConnectionError as e:
            print(f"  ERROR: Could not connect to API: {e}. Is the server running at {UPGRADE_BLUEPRINTS_ENDPOINT}?")
            return
        except Exception as e:
            print(f"  ERROR: An unexpected error occurred: {e}")
            failed_creations.append({"name": blueprint_payload.get('name'), "error": str(e)})
        time.sleep(0.2)

    print(f"\n--- Seeding Complete ---")
    print(f"Successfully created upgrade blueprints: {successful_creations}")
    if failed_creations:
        print(f"Failed to create upgrade blueprints: {len(failed_creations)}")
        for failure in failed_creations:
            print(f"  - Name: {failure.get('name')}, Status: {failure.get('status_code', 'N/A')}, Detail: {failure.get('detail', failure.get('error'))}")

if __name__ == "__main__":
    seed_data()