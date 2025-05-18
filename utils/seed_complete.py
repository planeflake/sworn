#!/usr/bin/env python3
"""
Comprehensive seed script for creating a complete game world with:
- Themes
- Characters (with traits)
- Resources
- Buildings (with resource requirements)
- Settlements (with leaders)

The script runs in two phases:
1. Phase 1: Create themes, world, characters, and resources
2. Phase 2: Create settlements with leaders and building blueprints

This two-phase approach ensures that characters are properly committed to the database
before they are assigned as settlement leaders, avoiding race conditions and
foreign key constraint violations.

Usage:
    python utils/seed_complete.py [--api-base-url http://localhost:8000] [--phase {1,2}] [--skip-truncate] [--force]
    
Arguments:
    --api-base-url URL    Base URL of the API server (default: http://localhost:8000)
    --phase {1,2}         Run only a specific phase (1 for foundation entities, 2 for settlements)
    --skip-truncate       Skip truncating tables before seeding
    --force               Continue seeding even if truncation fails
"""

import argparse
import logging
import requests
import time
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Theme data
THEMES = [
    {
        "theme_name": "Fantasy Medieval",
        "theme_description": "A world of magic, dragons, and medieval technology"
    },
    {
        "theme_name": "Post-Apocalyptic",
        "theme_description": "A world devastated by nuclear war, where survivors struggle to rebuild"
    },
    {
        "theme_name": "Sci-Fi",
        "theme_description": "A futuristic world with advanced technology, space travel, and alien civilizations"
    },
    {
        "theme_name": "Lovecraftian",
        "theme_description": "A world where cosmic horrors lurk beyond the veil of reality, threatening humanity's sanity"
    }
]

# Character template (theme_id and world_id will be filled in)
CHARACTER_TEMPLATES = [
    {
        "name": "Merlin the Wise",
        "description": "An ancient wizard with vast knowledge of arcane arts",
        "character_type": "NPC",
        "theme_name": "Fantasy Medieval",
        "traits": ["STRATEGIC", "CULTURAL"]
    },
    {
        "name": "Wasteland Warden",
        "description": "A hardened survivor with leadership skills and knowledge of the wastes",
        "character_type": "NPC",
        "theme_name": "Post-Apocalyptic",
        "traits": ["DEFENSIVE", "ECONOMICAL"]
    },
    {
        "name": "Captain Nova",
        "description": "A decorated starship captain with unparalleled tactical expertise",
        "character_type": "NPC",
        "theme_name": "Sci-Fi",
        "traits": ["STRATEGIC", "EXPANSIVE"]
    },
    {
        "name": "Professor Armitage",
        "description": "A paranoid scholar who has glimpsed the truth behind reality",
        "character_type": "NPC",
        "theme_name": "Lovecraftian",
        "traits": ["DEFENSIVE", "SPIRITUAL"]
    }
]

# Settlement templates (theme_id, leader_id, and world_id will be filled in)
SETTLEMENT_TEMPLATES = [
    {
        "name": "Mysteria",
        "description": "A magical town nestled in the enchanted forest",
        "theme_name": "Fantasy Medieval",
        "population": 1000,
        "leader_name": "Merlin the Wise"
    },
    {
        "name": "Fallout Haven",
        "description": "A settlement built among the ruins of an old city",
        "theme_name": "Post-Apocalyptic",
        "population": 500,
        "leader_name": "Wasteland Warden"
    },
    {
        "name": "New Horizons Colony",
        "description": "A space station orbiting a distant exoplanet",
        "theme_name": "Sci-Fi",
        "population": 2000,
        "leader_name": "Captain Nova"
    },
    {
        "name": "Innsmouth",
        "description": "A foggy coastal town with strange inhabitants and ancient secrets",
        "theme_name": "Lovecraftian",
        "population": 300,
        "leader_name": "Professor Armitage"
    }
]

# Resource templates by theme
RESOURCE_TEMPLATES = {
    "Fantasy Medieval": [
        {
            "name": "Oak Wood",
            "description": "Sturdy wood from oak trees, perfect for basic construction",
            "rarity": "Common",
            "stack_size": 50,
            "status": "Active"
        },
        {
            "name": "Stone",
            "description": "Basic building material quarried from mountains",
            "rarity": "Common",
            "stack_size": 50,
            "status": "Active"
        },
        {
            "name": "Iron Ore",
            "description": "Raw iron ore that can be smelted into iron ingots",
            "rarity": "Common",
            "stack_size": 40,
            "status": "Active"
        },
        {
            "name": "Iron Ingot",
            "description": "Refined iron metal used in crafting weapons and tools",
            "rarity": "Common",
            "stack_size": 30,
            "status": "Active"
        },
        {
            "name": "Mana Crystal",
            "description": "A crystal infused with magical energy",
            "rarity": "Rare",
            "stack_size": 15,
            "status": "Active"
        },
        {
            "name": "Dragon Scale",
            "description": "An extremely durable scale from a dragon's hide",
            "rarity": "Epic",
            "stack_size": 3,
            "status": "Active"
        }
    ],
    "Post-Apocalyptic": [
        {
            "name": "Scrap Metal",
            "description": "Salvaged metal from pre-war ruins",
            "rarity": "Common",
            "stack_size": 50,
            "status": "Active"
        },
        {
            "name": "Concrete Chunks",
            "description": "Pieces of concrete from collapsed buildings",
            "rarity": "Common",
            "stack_size": 40,
            "status": "Active"
        },
        {
            "name": "Electrical Components",
            "description": "Salvaged circuit boards and wiring",
            "rarity": "Uncommon",
            "stack_size": 25,
            "status": "Active"
        },
        {
            "name": "Purified Water",
            "description": "Clean, radiation-free water",
            "rarity": "Uncommon",
            "stack_size": 20,
            "status": "Active"
        },
        {
            "name": "Fusion Cell",
            "description": "A high-tech power source from before the apocalypse",
            "rarity": "Rare",
            "stack_size": 10,
            "status": "Active"
        }
    ],
    "Sci-Fi": [
        {
            "name": "Durasteel",
            "description": "Advanced alloy used in space construction",
            "rarity": "Common",
            "stack_size": 50,
            "status": "Active"
        },
        {
            "name": "Power Cells",
            "description": "Standard energy source for futuristic devices",
            "rarity": "Common",
            "stack_size": 30,
            "status": "Active"
        },
        {
            "name": "Synthetic Polymers",
            "description": "Advanced plastic-like materials with superior properties",
            "rarity": "Common",
            "stack_size": 40,
            "status": "Active"
        },
        {
            "name": "Quantum Processors",
            "description": "Advanced computing units that operate on quantum principles",
            "rarity": "Rare",
            "stack_size": 10,
            "status": "Active"
        },
        {
            "name": "Exotic Matter",
            "description": "Matter with negative mass used in FTL drives",
            "rarity": "Epic",
            "stack_size": 5,
            "status": "Active"
        }
    ],
    "Lovecraftian": [
        {
            "name": "Weathered Stone",
            "description": "Ancient stone darkened by time and the elements",
            "rarity": "Common",
            "stack_size": 50,
            "status": "Active"
        },
        {
            "name": "Old Growth Timber",
            "description": "Wood from ancient forests, saturated with damp",
            "rarity": "Common",
            "stack_size": 40,
            "status": "Active"
        },
        {
            "name": "Brass Fittings",
            "description": "Brass components for instruments and doors",
            "rarity": "Common",
            "stack_size": 30,
            "status": "Active"
        },
        {
            "name": "Strange Ichor",
            "description": "Mysterious fluid that seems to move with a mind of its own",
            "rarity": "Uncommon",
            "stack_size": 15,
            "status": "Active"
        },
        {
            "name": "Elder Sign",
            "description": "A protective symbol that wards against cosmic entities",
            "rarity": "Rare",
            "stack_size": 3,
            "status": "Active"
        }
    ]
}

# Building templates by theme with resource requirements
BUILDING_TEMPLATES = {
    "Fantasy Medieval": [
        {
            "name": "Watchtower",
            "description": "A tall tower for keeping watch over the surrounding area",
            "attributes": ["DEFENSIVE", "STRATEGIC"],
            "resource_requirements": {
                "Oak Wood": 30,
                "Stone": 50,
                "Iron Ingot": 10
            }
        },
        {
            "name": "Wizard Tower",
            "description": "A tall tower for magical research and spellcasting",
            "attributes": ["CULTURAL", "STRATEGIC"],
            "resource_requirements": {
                "Oak Wood": 20,
                "Stone": 40,
                "Mana Crystal": 5
            }
        },
        {
            "name": "Dwarven Forge",
            "description": "A sturdy forge for crafting weapons and armor",
            "attributes": ["ECONOMICAL", "PRODUCTIVE"],
            "resource_requirements": {
                "Stone": 60,
                "Iron Ingot": 20,
                "Mana Crystal": 2
            }
        }
    ],
    "Post-Apocalyptic": [
        {
            "name": "Bunker",
            "description": "A reinforced underground shelter",
            "attributes": ["DEFENSIVE", "RESIDENTIAL"],
            "resource_requirements": {
                "Scrap Metal": 40,
                "Concrete Chunks": 60
            }
        },
        {
            "name": "Watchtower",
            "description": "A lookout post made from scavenged materials",
            "attributes": ["DEFENSIVE", "STRATEGIC"],
            "resource_requirements": {
                "Scrap Metal": 30,
                "Concrete Chunks": 15
            }
        },
        {
            "name": "Water Purification Plant",
            "description": "Facility that cleans irradiated water",
            "attributes": ["ECONOMICAL", "PRODUCTIVE"],
            "resource_requirements": {
                "Scrap Metal": 50,
                "Electrical Components": 25,
                "Fusion Cell": 1
            }
        }
    ],
    "Sci-Fi": [
        {
            "name": "Research Lab",
            "description": "Advanced facility for scientific breakthroughs",
            "attributes": ["CULTURAL", "STRATEGIC"],
            "resource_requirements": {
                "Durasteel": 40,
                "Power Cells": 20,
                "Quantum Processors": 5
            }
        },
        {
            "name": "Defense Grid",
            "description": "Automated defense system to protect the settlement",
            "attributes": ["DEFENSIVE", "TECHNOLOGICAL"],
            "resource_requirements": {
                "Durasteel": 60,
                "Power Cells": 30,
                "Quantum Processors": 10
            }
        },
        {
            "name": "Quantum Fabricator",
            "description": "Advanced manufacturing facility using quantum principles",
            "attributes": ["ECONOMICAL", "PRODUCTIVE"],
            "resource_requirements": {
                "Durasteel": 50,
                "Synthetic Polymers": 40,
                "Quantum Processors": 15,
                "Exotic Matter": 1
            }
        }
    ],
    "Lovecraftian": [
        {
            "name": "Observatory",
            "description": "A place to monitor strange celestial phenomena",
            "attributes": ["CULTURAL", "STRATEGIC"],
            "resource_requirements": {
                "Weathered Stone": 40,
                "Old Growth Timber": 20,
                "Brass Fittings": 15
            }
        },
        {
            "name": "Warded Shelter",
            "description": "Living quarters protected by mystical symbols",
            "attributes": ["DEFENSIVE", "RESIDENTIAL"],
            "resource_requirements": {
                "Weathered Stone": 30,
                "Old Growth Timber": 50,
                "Elder Sign": 1
            }
        },
        {
            "name": "Occult Library",
            "description": "Repository of forbidden knowledge and arcane tomes",
            "attributes": ["CULTURAL", "SPIRITUAL"],
            "resource_requirements": {
                "Old Growth Timber": 40,
                "Brass Fittings": 20,
                "Strange Ichor": 5
            }
        }
    ]
}

def create_world(api_base_url: str, theme_id: str) -> Optional[str]:
    """Create a game world and return its ID"""
    # Use the new WorldCreateRequest format
    world_data = {
        "name": "Seed World",
        "theme_id": theme_id,
        "size": 1000,
        "description": "A world created by the seed script"
    }
    
    logger.info(f"Attempting to create world with theme_id: {theme_id}")
    response = requests.post(f"{api_base_url}/api/v1/worlds/", json=world_data)

    world_name = None

    if response.status_code == 200 or response.status_code == 201:
        result = response.json()
        logger.info(f"World creation response: {result}")
        
        # Check various response formats
        world_id = None
        
        # Option 1: Response has a nested 'world' object with id field
        if isinstance(result, dict) and "world" in result and isinstance(result["world"], dict):
            world_id = result["world"].get("id")
            world_name = result["world"].get("name")
            
        # Option 2: Direct ID in response
        elif isinstance(result, dict) and "id" in result:
            world_id = result.get("id")
            world_name = result.get("name", "Unknown")
            
        # Log success if we found an ID
        if world_id:
            logger.info(f"Created world: {world_name if 'world_name' in locals() else 'Unknown'} (ID: {world_id})")
            return world_id
        else:
            logger.error(f"Created world but couldn't extract ID from response: {result}")
            return None
    else:
        try:
            error_json = response.json() if response.content else {}
            error_detail = error_json.get("detail", response.text) if error_json else response.text
        except:
            error_detail = response.text if response.content else "Unknown error"
            
        logger.error(f"Failed to create world: {error_detail}")
        logger.error(f"Request data: {world_data}")
        
        # Let's try a different approach for debugging - fetch all worlds
        try:
            logger.info("Attempting to fetch existing worlds...")
            worlds_response = requests.get(f"{api_base_url}/api/v1/worlds/")
            if worlds_response.status_code == 200:
                worlds = worlds_response.json()
                logger.info(f"Found existing worlds: {worlds}")
                
                # If any worlds exist, return the first one's ID
                if isinstance(worlds, list) and len(worlds) > 0:
                    first_world = worlds[0]
                    if isinstance(first_world, dict) and "id" in first_world:
                        world_id = first_world["id"]
                        logger.info(f"Using existing world with ID: {world_id}")
                        return world_id
        except Exception as e:
            logger.error(f"Error fetching existing worlds: {e}")
        
        return None

def create_themes(api_base_url: str) -> Dict[str, str]:
    """Create themes and return a mapping of theme names to IDs"""
    theme_map = {}
    
    for theme_data in THEMES:
        theme_name = theme_data.get("theme_name")
        response = requests.post(f"{api_base_url}/api/v1/themes/", json=theme_data)
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            # Check if the API returns the ID directly or in a nested structure
            theme_id = None
            if isinstance(result, dict):
                theme_id = result.get("id") or result.get("theme_id")
                
                # If we still don't have an ID, try to log the response for debugging
                if theme_id is None:
                    logger.info(f"Received API response: {result}")
                    
                    # Maybe we need to get the ID from the created theme
                    if "theme" in result:
                        theme_id = result["theme"].get("id")
            
            logger.info(f"Created theme: {theme_name} (ID: {theme_id})")
            
            if theme_id and theme_name:
                theme_map[theme_name] = theme_id
            else:
                logger.warning(f"Theme '{theme_name}' was created but ID was not returned by API.")
        else:
            error_detail = response.json().get("detail", response.text) if response.content else "No content"
            logger.error(f"Failed to create theme '{theme_name}': {error_detail}")
        
        time.sleep(0.2)
    
    # If we didn't get any theme IDs from the API, try to fetch them
    if not theme_map:
        logger.info("No theme IDs returned during creation, attempting to fetch existing themes...")
        try:
            response = requests.get(f"{api_base_url}/api/v1/themes/")
            if response.status_code == 200:
                themes = response.json()
                # Check if it's a list or wrapped in another object
                if isinstance(themes, dict) and "items" in themes:
                    themes = themes["items"]
                    
                for theme in themes:
                    if isinstance(theme, dict):
                        name = theme.get("name")
                        theme_id = theme.get("id")
                        if name and theme_id:
                            theme_map[name] = theme_id
                            logger.info(f"Found existing theme: {name} (ID: {theme_id})")
        except Exception as e:
            logger.error(f"Error fetching existing themes: {e}")
    
    return theme_map

def create_characters(api_base_url: str, world_id: str, theme_map: Dict[str, str]) -> Dict[str, str]:
    """Create characters and return a mapping of character names to IDs"""
    character_map = {}
    logger.info("Creating characters with world_id: %s", world_id)
    
    for char_template in CHARACTER_TEMPLATES:
        # Make a copy of the template to avoid modifying the original
        char_template_copy = char_template.copy()
        theme_name = char_template_copy.pop("theme_name")
        traits = char_template_copy.pop("traits")
        char_name = char_template_copy.get("name")
        
        if theme_name in theme_map:
            char_data = {
                **char_template_copy,
                "world_id": world_id,
                "theme_id": theme_map[theme_name]
            }
            
            # Create character
            response = requests.post(f"{api_base_url}/api/v1/characters/", json=char_data)
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                char_id = result.get("id")
                if not char_id:
                    logger.error(f"Created character but no ID returned: {result}")
                    continue
                    
                logger.info(f"Created character: {char_name} (ID: {char_id})")
                character_map[char_name] = char_id
                # Print the character ID for debugging
                logger.info(f"Added character to map: {char_name} -> {char_id}")
                
                # Add traits - use the proper schema format for adding traits
                trait_data = {"traits": traits}
                
                # Try PUT first (replace all traits)
                trait_response = requests.put(
                    f"{api_base_url}/api/v1/characters/{char_id}/traits", 
                    json=trait_data
                )
                
                # If PUT fails, try POST (add traits)
                if trait_response.status_code >= 400:
                    trait_response = requests.post(
                        f"{api_base_url}/api/v1/characters/{char_id}/traits", 
                        json=trait_data
                    )
                
                if trait_response.status_code == 200 or trait_response.status_code == 201:
                    logger.info(f"Added traits to {char_name}: {traits}")
                else:
                    error_detail = trait_response.json().get("detail", trait_response.text) if trait_response.content else "No content"
                    logger.error(f"Failed to add traits to '{char_name}': {error_detail}")
                    logger.error(f"Trait data: {trait_data}")
            else:
                error_detail = response.json().get("detail", response.text) if response.content else "No content"
                logger.error(f"Failed to create character '{char_name}': {error_detail}")
                logger.error(f"Request data: {char_data}")
            
            time.sleep(0.2)
    
    # Explicitly verify characters are committed by fetching them
    logger.info("Verifying that characters have been committed to the database...")
    try:
        # Fetch all characters for the world to verify they exist
        response = requests.get(f"{api_base_url}/api/v1/characters/?world_id={world_id}")
        if response.status_code == 200:
            characters = response.json()
            
            # Check the response format and handle both list and dict with items key
            if isinstance(characters, dict) and 'items' in characters:
                characters = characters['items']
            
            if isinstance(characters, list):
                logger.info(f"Verified {len(characters)} characters in the database for world {world_id}")
                
                # Add any characters found that weren't in our map
                for char in characters:
                    if isinstance(char, dict):
                        char_id = char.get("id")
                        char_name = char.get("name")
                        if char_name and char_id and char_name not in character_map:
                            character_map[char_name] = char_id
                            logger.info(f"Added missing character from database to map: {char_name} -> {char_id}")
            else:
                logger.warning(f"Unexpected response format when verifying characters: {characters}")
        else:
            logger.warning(f"Failed to verify characters: {response.status_code}, {response.text}")
    except Exception as e:
        logger.warning(f"Error verifying characters: {e}")
    
    return character_map

def create_resources(api_base_url: str, theme_map: Dict[str, str]) -> Dict[str, str]:
    """Create resources for each theme and return a mapping of resource names to IDs"""
    resource_map = {}
    
    for theme_name, resources in RESOURCE_TEMPLATES.items():
        if theme_name in theme_map:
            theme_id = theme_map[theme_name]
            
            for resource_template in resources:
                resource_name = resource_template.get("name")
                resource_data = {
                    **resource_template,
                    "theme_id": theme_id
                }
                
                # First try to check if the resource already exists
                try:
                    search_response = requests.get(f"{api_base_url}/api/v1/resources/?name={resource_name}&theme_id={theme_id}")
                    if search_response.status_code == 200:
                        search_results = search_response.json()
                        
                        # Check if results are in a nested 'items' field
                        if isinstance(search_results, dict) and 'items' in search_results:
                            existing_resources = search_results.get('items', [])
                        else:
                            existing_resources = search_results if isinstance(search_results, list) else []
                        
                        # Look for matching resources
                        for resource in existing_resources:
                            if isinstance(resource, dict) and resource.get("name") == resource_name:
                                # Resource ID can be in "id" or "resource_id" field
                                resource_id = resource.get("id") or resource.get("resource_id")
                                if resource_id:
                                    logger.info(f"Resource '{resource_name}' already exists (ID: {resource_id}) for theme: {theme_name}")
                                    resource_map[resource_name] = resource_id
                                else:
                                    logger.warning(f"Resource '{resource_name}' found but has no ID!")
                                break
                        else:
                            # If we didn't break out of the loop, the resource doesn't exist
                            # Create a new resource
                            response = requests.post(f"{api_base_url}/api/v1/resources/", json=resource_data)
                            
                            if response.status_code == 200 or response.status_code == 201:
                                result = response.json()
                                # Resource ID can be in "id" or "resource_id" field depending on API response
                                resource_id = result.get("id") or result.get("resource_id")
                                if resource_id:
                                    logger.info(f"Created resource: {resource_name} (ID: {resource_id}) for theme: {theme_name}")
                                    resource_map[resource_name] = resource_id
                                else:
                                    logger.warning(f"Created resource '{resource_name}' but got no ID in response: {result}")
                            else:
                                error_detail = response.json().get("detail", response.text) if response.content else "No content"
                                logger.error(f"Failed to create resource '{resource_name}': {error_detail}")
                                logger.error(f"Request data: {resource_data}")
                except Exception as e:
                    logger.error(f"Error checking for existing resource '{resource_name}': {e}")
                    # Try to create it directly
                    try:
                        response = requests.post(f"{api_base_url}/api/v1/resources/", json=resource_data)
                        
                        if response.status_code == 200 or response.status_code == 201:
                            result = response.json()
                            resource_id = result.get("id")
                            logger.info(f"Created resource: {resource_name} (ID: {resource_id}) for theme: {theme_name}")
                            resource_map[resource_name] = resource_id
                        else:
                            error_detail = response.json().get("detail", response.text) if response.content else "No content"
                            logger.error(f"Failed to create resource '{resource_name}': {error_detail}")
                    except Exception as e2:
                        logger.error(f"Error creating resource '{resource_name}': {e2}")
                
                time.sleep(0.2)
    
    # Check if we found any resources, if not try fetching them all
    if not resource_map:
        try:
            logger.info("No resources created/found, attempting to fetch all existing resources...")
            response = requests.get(f"{api_base_url}/api/v1/resources/")
            if response.status_code == 200:
                resources_data = response.json()
                
                # Check if results are in a nested 'items' field
                if isinstance(resources_data, dict) and 'items' in resources_data:
                    resources = resources_data.get('items', [])
                else:
                    resources = resources_data if isinstance(resources_data, list) else []
                
                for resource in resources:
                    name = resource.get("name")
                    # Resource ID can be in "id" or "resource_id" field
                    resource_id = resource.get("id") or resource.get("resource_id")
                    if name and resource_id:
                        resource_map[name] = resource_id
                        logger.info(f"Found existing resource: {name} (ID: {resource_id})")
                    elif name and not resource_id:
                        logger.warning(f"Resource '{name}' found but has no ID!")
        except Exception as e:
            logger.error(f"Error fetching all resources: {e}")
    
    return resource_map

def create_buildings(api_base_url: str, theme_map: Dict[str, str], resource_map: Dict[str, str]) -> None:
    """Create building blueprints for each theme with resource requirements"""
    for theme_name, buildings in BUILDING_TEMPLATES.items():
        if theme_name in theme_map:
            theme_id = theme_map[theme_name]
            
            for building_template in buildings:
                building_name = building_template["name"]
                
                # Check if building already exists
                try:
                    search_response = requests.get(f"{api_base_url}/api/v1/building-blueprints/?name={building_name}&theme_id={theme_id}")
                    building_exists = False
                    
                    if search_response.status_code == 200:
                        search_results = search_response.json()
                        
                        # Check if results are in a nested 'items' field
                        if isinstance(search_results, dict) and 'items' in search_results:
                            existing_buildings = search_results.get('items', [])
                        else:
                            existing_buildings = search_results if isinstance(search_results, list) else []
                        
                        # Look for matching buildings
                        for building in existing_buildings:
                            if isinstance(building, dict) and building.get("name") == building_name:
                                building_id = building.get("id")
                                logger.info(f"Building '{building_name}' already exists (ID: {building_id}) for theme: {theme_name}")
                                building_exists = True
                                break
                        
                        if building_exists:
                            continue  # Skip to next building if it already exists
                except Exception as e:
                    logger.error(f"Error checking for existing building '{building_name}': {e}")
                
                # Make a copy of the template to avoid modifying the original
                building_template_copy = building_template.copy()
                
                # Get and remove the resource requirements 
                resource_requirements = building_template_copy.pop("resource_requirements")
                attributes = building_template_copy.pop("attributes", [])
                
                # Convert the building template into a proper blueprint with stages
                building_data = {
                    "name": building_template_copy["name"],
                    "description": building_template_copy["description"],
                    "theme_id": theme_id,
                    "is_unique_per_settlement": False,
                    "_metadata": {
                        "category": attributes[0] if attributes else "BASIC",
                        "attributes": attributes
                    },
                    # Create a single stage with all resource requirements
                    "stages": [
                        {
                            "stage_number": 1,
                            "name": f"Build {building_template_copy['name']}",
                            "description": f"Construction of {building_template_copy['name']}",
                            "duration_days": 3.0,
                            # Convert dictionary of resource name->amount to the required format
                            "resource_costs": [
                                {"resource_id": resource_map[res_name], "amount": res_amount}
                                for res_name, res_amount in resource_requirements.items()
                                if res_name in resource_map
                            ],
                            "profession_time_bonus": [],
                            "stage_completion_bonuses": [],
                            "optional_features": []
                        }
                    ]
                }
                
                # Remove created_at and updated_at if present in the request
                # Let the server handle setting these timestamps
                building_data.pop('created_at', None)
                building_data.pop('updated_at', None)
                
                # Also check and remove timestamps from stages
                for stage in building_data['stages']:
                    stage.pop('created_at', None)
                    stage.pop('updated_at', None)
                
                try:
                    response = requests.post(f"{api_base_url}/api/v1/building-blueprints/", json=building_data)
                    
                    if response.status_code == 200 or response.status_code == 201:
                        result = response.json()
                        building_id = result.get("id")
                        logger.info(f"Created building blueprint: {building_name} (ID: {building_id}) for theme: {theme_name}")
                        logger.info(f"Added resource requirements: {resource_requirements}")
                    else:
                        error_detail = response.json().get("detail", response.text) if response.content else "No content"
                        logger.error(f"Failed to create building blueprint '{building_name}': {error_detail}")
                        logger.error(f"Request data: {building_data}")
                except Exception as e:
                    logger.error(f"Exception creating building '{building_name}': {e}")
                
                time.sleep(0.2)

def create_settlements(api_base_url: str, world_id: str, theme_map: Dict[str, str], character_map: Dict[str, str], resource_map: Dict[str, str]) -> None:
    """Create settlements with leaders and resources"""
    # Double check character_map before starting
    logger.info(f"Character map at beginning of settlement creation: {character_map}")
    
    for settlement_template in SETTLEMENT_TEMPLATES:
        # Make a copy to avoid modifying the original
        settlement_template_copy = settlement_template.copy()
        
        theme_name = settlement_template_copy.pop("theme_name")
        leader_name = settlement_template_copy.pop("leader_name")
        settlement_name = settlement_template_copy.get("name")
        
        # Verify the character exists in our map
        if leader_name not in character_map:
            logger.error(f"Leader '{leader_name}' not found in character map for settlement '{settlement_name}'")
            # Try one more time to fetch the character from the database
            try:
                search_char_response = requests.get(f"{api_base_url}/api/v1/characters/?name={leader_name}&world_id={world_id}")
                if search_char_response.status_code == 200:
                    char_results = search_char_response.json()
                    if isinstance(char_results, dict) and 'items' in char_results:
                        char_results = char_results['items']
                    
                    for char in char_results:
                        if char.get("name") == leader_name:
                            char_id = char.get("id")
                            logger.info(f"Found character '{leader_name}' in database with ID: {char_id}")
                            character_map[leader_name] = char_id
                            break
            except Exception as e:
                logger.error(f"Error searching for character '{leader_name}': {e}")
        
        if theme_name in theme_map and leader_name in character_map:
            leader_id = character_map[leader_name]
            logger.info(f"Preparing settlement '{settlement_name}' with leader '{leader_name}' (ID: {leader_id})")
            
            # Check if settlement already exists
            try:
                search_response = requests.get(f"{api_base_url}/api/v1/settlements/?name={settlement_name}&world_id={world_id}")
                settlement_exists = False
                existing_settlement_id = None
                
                if search_response.status_code == 200:
                    search_results = search_response.json()
                    
                    # Check if results are in a nested 'items' field
                    if isinstance(search_results, dict) and 'items' in search_results:
                        existing_settlements = search_results.get('items', [])
                    else:
                        existing_settlements = search_results if isinstance(search_results, list) else []
                    
                    # Look for matching settlements
                    for settlement in existing_settlements:
                        if isinstance(settlement, dict) and settlement.get("name") == settlement_name:
                            existing_settlement_id = settlement.get("id")
                            logger.info(f"Settlement '{settlement_name}' already exists (ID: {existing_settlement_id})")
                            settlement_exists = True
                            break
                    
                    if settlement_exists:
                        # If settlement exists but has no leader, try to set it
                        if existing_settlement_id:
                            # Check if settlement already has a leader
                            if "leader_id" not in settlement or not settlement.get("leader_id"):
                                logger.info(f"Existing settlement '{settlement_name}' has no leader. Attempting to set leader.")
                                # Try to assign the leader to the existing settlement
                                # (Reuse leader assignment code later)
                                try_assign_leader(api_base_url, existing_settlement_id, leader_id, leader_name, settlement_name)
                        continue  # Skip to next settlement if it already exists
            except Exception as e:
                logger.error(f"Error checking for existing settlement '{settlement_name}': {e}")
            
            # Create settlement data that matches the API expectations
            # Add population and resources to the settlement
            population = settlement_template_copy.get("population", 10)
            
            # Get resources for this settlement based on its theme
            resources = {}
            if theme_name in RESOURCE_TEMPLATES:
                # Add initial quantities of each resource from the theme
                for i, resource_template in enumerate(RESOURCE_TEMPLATES[theme_name]):
                    resource_name = resource_template["name"]
                    if resource_name in resource_map:
                        resource_id = resource_map[resource_name]
                        
                        # Skip if resource_id is None
                        if resource_id is None:
                            logger.warning(f"Resource '{resource_name}' has None ID - skipping")
                            continue
                            
                        # Add varying quantities based on resource rarity
                        if resource_template["rarity"] == "Common":
                            quantity = 50 + (i * 10)  # Starting with 50, increasing by 10
                        elif resource_template["rarity"] == "Uncommon":
                            quantity = 25 + (i * 5)   # Starting with 25, increasing by 5
                        elif resource_template["rarity"] == "Rare":
                            quantity = 10 + (i * 2)   # Starting with 10, increasing by 2
                        else:  # Epic or Legendary
                            quantity = 5              # Fixed small amount for rare resources
                        
                        # Convert to string explicitly to ensure no None keys
                        if resource_id:
                            resource_id_str = str(resource_id)
                            resources[resource_id_str] = quantity
                            logger.debug(f"Added resource {resource_name} ({resource_id_str}) with quantity {quantity}")
            
            # Print debug information about resources
            logger.info(f"Resources for settlement '{settlement_template_copy['name']}': {resources}")
            logger.info(f"Resource keys type check: {[(k, type(k)) for k in resources.keys()]}")
            
            settlement_data = {
                "name": settlement_template_copy["name"],
                "description": settlement_template_copy["description"],
                "world_id": world_id,
                "population": population,
                "resources": resources
            }
            
            # Remove timestamps if present
            settlement_data.pop('created_at', None)
            settlement_data.pop('updated_at', None)
            
            try:
                # Step 1: Create the basic settlement
                logger.info(f"Creating settlement {settlement_name} with data: {settlement_data}")
                response = requests.post(f"{api_base_url}/api/v1/settlements/", json=settlement_data)
                
                if response.status_code == 200 or response.status_code == 201:
                    result = response.json()
                    # Check if the settlement is in a nested field
                    if isinstance(result, dict) and "settlement" in result:
                        settlement_info = result["settlement"]
                        settlement_id = settlement_info.get("id")
                    else:
                        settlement_id = result.get("id")
                        
                    if not settlement_id:
                        logger.error(f"Failed to get settlement ID from response: {result}")
                        continue
                        
                    logger.info(f"Created settlement: {settlement_name} (ID: {settlement_id})")
                    
                    # Step 2: Set the leader for the settlement
                    try_assign_leader(api_base_url, settlement_id, leader_id, leader_name, settlement_name)
                else:
                    error_detail = response.json().get("detail", response.text) if response.content else "No content"
                    logger.error(f"Failed to create settlement '{settlement_name}': {error_detail}")
                    logger.error(f"Request data: {settlement_data}")
            except Exception as e:
                logger.error(f"Exception creating settlement '{settlement_name}': {e}")
            
            time.sleep(0.5)  # Slightly longer delay to ensure settlement is committed
        else:
            if theme_name not in theme_map:
                logger.error(f"Theme '{theme_name}' not found for settlement '{settlement_name}'")
            if leader_name not in character_map:
                logger.error(f"Leader '{leader_name}' not found for settlement '{settlement_name}'")

def try_assign_leader(api_base_url: str, settlement_id: str, leader_id: str, leader_name: str, settlement_name: str) -> bool:
    """Helper function to attempt to assign a leader to a settlement with multiple fallback methods"""
    logger.info(f"Attempting to set leader: {leader_name} (ID: {leader_id}) for settlement: {settlement_name} (ID: {settlement_id})")
    
    # Verify the character exists first
    try:
        char_response = requests.get(f"{api_base_url}/api/v1/characters/{leader_id}")
        if char_response.status_code != 200:
            logger.error(f"Character {leader_name} (ID: {leader_id}) not found in database, cannot assign as leader")
            return False
        logger.info(f"Verified character {leader_name} (ID: {leader_id}) exists in database")
    except Exception as e:
        logger.error(f"Error verifying character {leader_id} exists: {e}")
        return False
        
    success = False
    leader_data = {"leader_id": leader_id}
    
    # Method 1: Try dedicated leader endpoint with PUT
    try:
        logger.info(f"Method 1: Trying PUT to /settlements/{settlement_id}/leader")
        leader_response = requests.put(
            f"{api_base_url}/api/v1/settlements/{settlement_id}/leader", 
            json=leader_data
        )
        
        if leader_response.status_code == 200 or leader_response.status_code == 201:
            logger.info(f"Successfully set leader {leader_name} (ID: {leader_id}) for settlement {settlement_name} using Method 1")
            return True
        else:
            logger.warning(f"Method 1 failed with status {leader_response.status_code}: {leader_response.text}")
    except Exception as e:
        logger.warning(f"Error in Method 1 for setting leader: {e}")
        
    # Method 2: Try dedicated leader endpoint with PATCH
    try:
        logger.info(f"Method 2: Trying PATCH to /settlements/{settlement_id}/leader")
        leader_response = requests.patch(
            f"{api_base_url}/api/v1/settlements/{settlement_id}/leader", 
            json=leader_data
        )
        
        if leader_response.status_code == 200 or leader_response.status_code == 201:
            logger.info(f"Successfully set leader {leader_name} (ID: {leader_id}) for settlement {settlement_name} using Method 2")
            return True
        else:
            logger.warning(f"Method 2 failed with status {leader_response.status_code}: {leader_response.text}")
    except Exception as e:
        logger.warning(f"Error in Method 2 for setting leader: {e}")
        
    # Method 3: Try updating the whole settlement with PATCH
    try:
        logger.info(f"Method 3: Trying PATCH to /settlements/{settlement_id}")
        leader_response = requests.patch(
            f"{api_base_url}/api/v1/settlements/{settlement_id}", 
            json={"leader_id": leader_id}
        )
        
        if leader_response.status_code == 200 or leader_response.status_code == 201:
            logger.info(f"Successfully set leader {leader_name} (ID: {leader_id}) for settlement {settlement_name} using Method 3")
            return True
        else:
            logger.warning(f"Method 3 failed with status {leader_response.status_code}: {leader_response.text}")
    except Exception as e:
        logger.warning(f"Error in Method 3 for setting leader: {e}")
    
    # Method 4: Try creating with leader_id directly
    try:
        logger.info(f"Method 4: Trying to update settlement {settlement_id} with direct leader_id attribute")
        settlement_response = requests.get(f"{api_base_url}/api/v1/settlements/{settlement_id}")
        if settlement_response.status_code == 200:
            settlement_data = settlement_response.json()
            settlement_data["leader_id"] = leader_id
            
            update_response = requests.put(
                f"{api_base_url}/api/v1/settlements/{settlement_id}",
                json=settlement_data
            )
            
            if update_response.status_code == 200 or update_response.status_code == 201:
                logger.info(f"Successfully set leader {leader_name} (ID: {leader_id}) for settlement {settlement_name} using Method 4")
                return True
            else:
                logger.warning(f"Method 4 failed with status {update_response.status_code}: {update_response.text}")
        else:
            logger.warning(f"Failed to get settlement data for Method 4: {settlement_response.status_code}")
    except Exception as e:
        logger.warning(f"Error in Method 4 for setting leader: {e}")
    
    logger.warning(f"All methods failed to assign leader {leader_name} to settlement {settlement_name}")
    return False

def truncate_tables() -> None:
    """Truncate database tables in the correct order to remove existing data"""
    import psycopg2
    import os
    import sys
    
    # Add the app directory to sys.path to import app modules
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        # Import config from the app to use the same connection parameters
        from app.core.config import settings
        
        # Get database connection info from app config
        db_name = settings.DBNAME
        db_user = settings.DBUSER
        db_password = settings.DBPASSWORD
        db_host = settings.DBHOST
        db_port = settings.DBPORT
        
        logger.info(f"Truncating database tables in {db_name} at {db_host}:{db_port}")
    except ImportError:
        logger.warning("Could not import app config, using environment variables instead")
        # Fall back to environment variables
        db_name = os.environ.get("DBNAME", "sworn")
        db_user = os.environ.get("DBUSER", "postgres")
        db_password = os.environ.get("DBPASSWORD", "postgres")
        db_host = os.environ.get("DBHOST", "10.0.0.200")
        db_port = os.environ.get("DBPORT", "5433")  # Update default port to 5433
        
        logger.info(f"Truncating database tables in {db_name} at {db_host}:{db_port}")
    
    # Initialize connection and cursor variables
    conn = None
    cursor = None
    
    # Database connection parameters
    db_params = {
        "dbname": db_name,
        "user": db_user,
        "password": db_password,
        "host": db_host,
        "port": db_port
    }
    
    # Tables in reverse dependency order (child tables first)
    tables_to_truncate = [
        # Child tables (many-to-one relationships)
        "character_skills",
        "building_instances",
        "settlements",
        "characters",
        "blueprint_stage_features",
        "blueprint_stages",
        "building_upgrade_blueprints",
        "building_blueprints",
        "resources",
        "skills",
        "profession_definitions",
        "locations",
        "worlds",
        # Parent tables
        "biomes",
        "themes"
    ]
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**db_params)
        conn.autocommit = False  # Start a transaction
        cursor = conn.cursor()
        
        # Disable all foreign key constraints temporarily
        cursor.execute("SET CONSTRAINTS ALL DEFERRED;")
        
        # Truncate each table
        for table in tables_to_truncate:
            try:
                cursor.execute(f'TRUNCATE TABLE "{table}" CASCADE;')
                logger.info(f"Truncated table: {table}")
            except Exception as e:
                logger.warning(f"Could not truncate {table}: {e}")
        
        # Commit the transaction
        conn.commit()
        logger.info("Successfully truncated all tables")
        
    except Exception as e:
        logger.error(f"Error truncating tables: {e}")
        # Try to rollback if possible
        try:
            if conn:
                conn.rollback()
        except:
            pass
        
        # If this was a connection error, continue with seeding without truncation
        logger.warning("Continuing without truncating tables due to database connection error")
    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def seed_world(api_base_url: str = "http://localhost:8000", skip_truncate: bool = False, force: bool = False) -> None:
    """
    Seed a complete game world with themes, characters, resources, buildings, and settlements
    using a two-phase approach to avoid leader assignment issues.
    
    Phase 1: Create themes, world, characters, and resources
    Phase 2: Create settlements with leaders and buildings
    
    Args:
        api_base_url: Base URL of the API server
        skip_truncate: Skip truncating tables before seeding
        force: Continue seeding even if truncation fails
    """
    logger.info(f"Starting world seeding using API at {api_base_url}")
    
    # Check if API server is running
    try:
        response = requests.get(f"{api_base_url}/status")
        if response.status_code != 200:
            logger.error(f"API server at {api_base_url} returned status code {response.status_code}")
            return
        logger.info(f"API server is running at {api_base_url}")
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to API server at {api_base_url}. Is the server running?")
        return
    
    # Truncate tables before seeding
    truncation_successful = True
    if not skip_truncate:
        try:
            truncate_tables()
        except Exception as e:
            truncation_successful = False
            logger.error(f"Error during table truncation: {e}")
            
            if not force:
                logger.error("Aborting seeding process. Use --force to continue anyway or --skip-truncate to skip truncation.")
                return
            else:
                logger.warning("Continuing with seeding despite truncation failure (--force was specified)")
    else:
        logger.info("Skipping table truncation (--skip-truncate was specified)")
    
    # Phase 1: Create foundation - themes, world, characters, and resources
    logger.info("====== Starting Phase 1: Creating foundation entities ======")
    theme_map, world_id, character_map, resource_map = phase1_create_foundation(api_base_url)
    
    if not all([theme_map, world_id, character_map, resource_map]):
        logger.error("Phase 1 failed. Aborting seeding process.")
        return
        
    logger.info("Phase 1 completed successfully. Foundation entities created.")
    
    # Add a short pause to ensure database transactions are fully committed
    logger.info("Pausing for 2 seconds to ensure database transactions are fully committed...")
    time.sleep(2)
    
    # Phase 2: Create settlements with leaders and buildings
    logger.info("====== Starting Phase 2: Creating settlements and buildings ======")
    phase2_create_settlements_and_buildings(api_base_url, world_id, theme_map, character_map, resource_map)
    
    logger.info("World seeding completed successfully.")

def phase1_create_foundation(api_base_url: str):
    """
    Phase 1 of the seeding process: Create all foundation entities
    
    Returns:
        tuple: (theme_map, world_id, character_map, resource_map)
    """
    # Step 1: Create themes first
    theme_map = create_themes(api_base_url)
    if not theme_map:
        logger.error("Failed to create themes. Phase 1 failed.")
        return None, None, None, None
    
    # Step 2: Create a world (requires a theme_id)
    default_theme_id = next(iter(theme_map.values())) if theme_map else None
    if not default_theme_id:
        logger.error("No themes available to use for world creation. Phase 1 failed.")
        return theme_map, None, None, None
        
    world_id = create_world(api_base_url, default_theme_id)
    if not world_id:
        logger.error("Failed to create world. Phase 1 failed.")
        return theme_map, None, None, None
    
    # Step 3: Create characters with traits
    character_map = create_characters(api_base_url, world_id, theme_map)
    if not character_map:
        logger.error("Failed to create characters. Phase 1 failed.")
        return theme_map, world_id, None, None
        
    logger.info(f"Character map after creation: {character_map}")
    
    # Step 4: Create resources for each theme
    resource_map = create_resources(api_base_url, theme_map)
    if not resource_map:
        logger.error("Failed to create resources. Phase 1 failed.")
        return theme_map, world_id, character_map, None
    
    return theme_map, world_id, character_map, resource_map

def phase2_create_settlements_and_buildings(api_base_url: str, world_id: str, theme_map: Dict[str, str], 
                                           character_map: Dict[str, str], resource_map: Dict[str, str]):
    """
    Phase 2 of the seeding process: Create settlements with leaders and buildings
    
    Args:
        api_base_url: Base URL of the API server
        world_id: ID of the world to create settlements in
        theme_map: Mapping of theme names to IDs
        character_map: Mapping of character names to IDs
        resource_map: Mapping of resource names to IDs
    """
    # Verify that we have everything we need
    if not world_id or not theme_map or not character_map or not resource_map:
        logger.error("Missing required data for Phase 2. Cannot proceed.")
        return
    
    # Double-check that character_map contains all the characters we need
    required_characters = [template["leader_name"] for template in SETTLEMENT_TEMPLATES]
    missing_characters = [name for name in required_characters if name not in character_map]
    
    # Print debug information about all the characters we have
    logger.info(f"Character map before creating settlements: {character_map}")
    logger.info(f"Required characters for leaders: {required_characters}")
    
    # One more verification - fetch all characters from the database to ensure they exist
    try:
        response = requests.get(f"{api_base_url}/api/v1/characters/?world_id={world_id}")
        if response.status_code == 200:
            characters = response.json()
            if isinstance(characters, dict) and 'items' in characters:
                characters = characters['items']
            
            if isinstance(characters, list):
                logger.info(f"Database contains {len(characters)} characters for world {world_id}")
                db_character_ids = {char['name']: char['id'] for char in characters if isinstance(char, dict) and 'name' in char}
                logger.info(f"Characters in database: {db_character_ids}")
                
                # Update character_map with database values
                for name, db_id in db_character_ids.items():
                    if name in required_characters and name not in character_map:
                        logger.info(f"Found missing character in database: {name} -> {db_id}")
                        character_map[name] = db_id
        else:
            logger.warning(f"Failed to verify characters in database: {response.status_code}, {response.text}")
    except Exception as e:
        logger.warning(f"Error verifying characters in database: {e}")
    
    # Check again after database verification
    missing_characters = [name for name in required_characters if name not in character_map]
    
    if missing_characters:
        logger.error(f"Missing required characters for settlements: {', '.join(missing_characters)}")
        logger.error("Cannot create settlements without their leaders. Phase 2 failed.")
        return
    
    # Step 1: Create building blueprints for each theme with resource requirements
    logger.info("Creating building blueprints...")
    create_buildings(api_base_url, theme_map, resource_map)
    
    # Step 2: Create settlements with leaders
    logger.info("Creating settlements with leaders...")
    create_settlements(api_base_url, world_id, theme_map, character_map, resource_map)
    
    logger.info("Phase 2 completed successfully.")

def main():
    """Parse arguments and run the seeding script."""
    parser = argparse.ArgumentParser(description="Seed a complete game world.")
    parser.add_argument("--api-base-url", default="http://localhost:8000", help="Base URL of the API server")
    parser.add_argument("--skip-truncate", action="store_true", help="Skip truncating tables before seeding")
    parser.add_argument("--force", action="store_true", help="Continue seeding even if truncation fails")
    parser.add_argument("--phase", type=int, choices=[1, 2], help="Run only a specific phase (1 for foundation, 2 for settlements)")
    args = parser.parse_args()
    
    if args.phase == 1:
        # Run only phase 1
        logger.info("Running only Phase 1: Creating foundation entities")
        api_base_url = args.api_base_url
        
        # Truncate if needed
        if not args.skip_truncate:
            try:
                truncate_tables()
            except Exception as e:
                logger.error(f"Error during table truncation: {e}")
                if not args.force:
                    logger.error("Aborting seeding process. Use --force to continue anyway.")
                    return
        
        # Run phase 1
        theme_map, world_id, character_map, resource_map = phase1_create_foundation(api_base_url)
        if all([theme_map, world_id, character_map, resource_map]):
            logger.info("Phase 1 completed successfully.")
            # Print important IDs for reference when running phase 2 separately
            logger.info(f"World ID for phase 2: {world_id}")
            logger.info(f"Character map for reference: {character_map}")
        else:
            logger.error("Phase 1 failed.")
    elif args.phase == 2:
        logger.error("Running only Phase 2 directly is not supported yet.")
        logger.error("Please run Phase 1 first, then modify this script to use the generated IDs for Phase 2.")
    else:
        # Run the full seeding process
        seed_world(api_base_url=args.api_base_url, skip_truncate=args.skip_truncate, force=args.force)

if __name__ == "__main__":
    main()