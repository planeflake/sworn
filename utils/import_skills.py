import requests
import json

# --- Configuration ---
API_BASE_URL = "http://localhost:8000/api/v1"
SKILLS_ENDPOINT = f"{API_BASE_URL}/skills/"

FANTASY_THEME_ID = "dfba10ac-eaa7-4f83-977d-def25746dfb5"
POST_APOC_THEME_ID = "7f867e0f-8632-4f1a-88d1-855ffee29ca3"

# --- Skill Definitions (Foundational Gathering Skills) ---
skills_to_create = [
    {
        "name": "Plant Foraging",
        "description": "Identifying and gathering edible or useful wild plants like berries, roots, nuts, and simple vegetables.",
        "max_level": 100,
        "themes": [FANTASY_THEME_ID, POST_APOC_THEME_ID],
        "metadata": {}
    },
    {
        "name": "Herb Gathering",
        "description": "Identifying and collecting specific herbs and fungi for medicinal, alchemical, or seasoning purposes.",
        "max_level": 100,
        "themes": [FANTASY_THEME_ID, POST_APOC_THEME_ID],
        "metadata": {}
    },
    {
        "name": "Woodcutting",
        "description": "Felling small trees and gathering fallen branches for firewood, basic construction, or tool handles.",
        "max_level": 100,
        "themes": [FANTASY_THEME_ID, POST_APOC_THEME_ID],
        "metadata": {}
    },
    {
        "name": "Stone Collection",
        "description": "Gathering loose stones, flint, or breaking off manageable pieces from rock outcroppings for tools or basic construction.",
        "max_level": 100,
        "themes": [FANTASY_THEME_ID, POST_APOC_THEME_ID],
        "metadata": {}
    },
    {
        "name": "Ore Prospecting",
        "description": "Identifying and collecting small surface deposits of common ores (e.g., iron, copper).",
        "max_level": 100,
        "themes": [FANTASY_THEME_ID, POST_APOC_THEME_ID],
        "metadata": {}
    },
    {
        "name": "Small Game Hunting",
        "description": "Actively pursuing and capturing small animals (rabbits, squirrels, birds) using simple methods like thrown rocks or basic snares.",
        "max_level": 100,
        "themes": [FANTASY_THEME_ID, POST_APOC_THEME_ID],
        "metadata": {}
    },
    {
        "name": "Fishing (Basic)",
        "description": "Catching fish using rudimentary methods like hand-lines, simple nets, or spearing in shallow waters.",
        "max_level": 100,
        "themes": [FANTASY_THEME_ID, POST_APOC_THEME_ID],
        "metadata": {}
    },
    {
        "name": "Skinning & Butchering",
        "description": "Processing killed animals to obtain meat, hides, sinew, and bones.",
        "max_level": 100,
        "themes": [FANTASY_THEME_ID, POST_APOC_THEME_ID],
        "metadata": {}
    },
    {
        "name": "Fiber Collection",
        "description": "Gathering plant fibers (e.g., from nettles, flax, certain tree barks) for making cordage or rough cloth.",
        "max_level": 100,
        "themes": [FANTASY_THEME_ID, POST_APOC_THEME_ID],
        "metadata": {}
    },
    {
        "name": "Water Sourcing",
        "description": "Identifying and collecting potable water from relatively safe natural sources like springs, clean streams, or rain collection.",
        "max_level": 100,
        "themes": [FANTASY_THEME_ID, POST_APOC_THEME_ID],
        "metadata": {}
    },
    {
        "name": "Salvaging (Basic)",
        "description": "Searching through readily accessible debris and abandoned, non-hazardous areas for simple, usable materials.",
        "max_level": 100,
        "themes": [POST_APOC_THEME_ID], # Primarily Post-Apoc for this basic version
        "metadata": {}
    }
]

# --- Headers for the request ---
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

# --- Function to post a single skill ---
def create_skill(skill_data):
    try:
        response = requests.post(SKILLS_ENDPOINT, headers=headers, data=json.dumps(skill_data), timeout=10)
        # Or using the json parameter which handles dump and content-type
        # response = requests.post(SKILLS_ENDPOINT, headers={'accept': 'application/json'}, json=skill_data, timeout=10)

        if response.status_code == 200 or response.status_code == 201: # 201 Created is common for POST
            print(f"Successfully created skill: {skill_data['name']} (Status: {response.status_code})")
            try:
                return response.json()
            except json.JSONDecodeError:
                print("  Response was not JSON, but status code was success.")
                return None
        else:
            print(f"Error creating skill: {skill_data['name']} (Status: {response.status_code})")
            try:
                print(f"  Error details: {response.json()}")
            except json.JSONDecodeError:
                print(f"  Error details (raw): {response.text}")
            return None
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error for skill '{skill_data['name']}': {e}")
        print(f"Is your server running at {API_BASE_URL}?")
        return None
    except requests.exceptions.Timeout:
        print(f"Request timed out for skill: {skill_data['name']}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred for skill '{skill_data['name']}': {e}")
        return None

# --- Main script execution ---
if __name__ == "__main__":
    print(f"Attempting to create {len(skills_to_create)} skills at {SKILLS_ENDPOINT}...\n")
    created_count = 0
    error_count = 0

    for skill in skills_to_create:
        result = create_skill(skill)
        if result:
            created_count += 1
        else:
            error_count += 1
        print("-" * 30) # Separator

    print(f"\n--- Import Summary ---")
    print(f"Successfully created: {created_count} skills")
    print(f"Failed to create:   {error_count} skills")

    # You can add the other skill lists (Common, Fantasy, Post-Apoc specific) here
    # as well, or call this script multiple times with different skill_lists.
    # For example:
    #
    # common_skills_from_previous_list = [ ... ]
    # fantasy_specific_skills = [ ... ]
    # post_apoc_specific_skills = [ ... ]
    #
    # all_skills = (
    #     skills_to_create +
    #     common_skills_from_previous_list +
    #     fantasy_specific_skills +
    #     post_apoc_specific_skills
    # )
    #
    # # (Remove duplicates if merging lists like this)
    # unique_skill_names = set()
    # unique_skills_to_create = []
    # for skill in all_skills:
    #     if skill['name'] not in unique_skill_names:
    #         unique_skills_to_create.append(skill)
    #         unique_skill_names.add(skill['name'])
    #     else:
    #         print(f"Skipping duplicate skill name: {skill['name']}")
    #
    # # Then loop through unique_skills_to_create