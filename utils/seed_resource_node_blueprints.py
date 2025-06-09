#!/usr/bin/env python3
"""
Seed script to create resource node blueprints for existing resources via API.
"""

import asyncio
import httpx
import json
from typing import List, Dict, Any

# Base API URL
BASE_URL = "http://localhost:8000/api/v1"

# Resource node blueprint data based on your resources
RESOURCE_NODE_BLUEPRINTS = [
    # Fantasy Medieval Resources
    {
        "name": "Oak Grove",
        "description": "A grove of oak trees that can be harvested for wood",
        "resource_id": "e19473f6-f9bd-4b0c-9ea7-dba8ca221e97",  # Oak Wood
        "base_extraction_rate": 10,
        "max_extraction_rate": 20,
        "depletion_rate": 0.01,
        "respawn_rate": 0.05,
        "rarity": "common",
        "biome_types": ["forest", "plains"],
        "required_tech": [],
        "extraction_difficulty": 1
    },
    {
        "name": "Stone Quarry",
        "description": "A rocky outcrop that provides building stone",
        "resource_id": "2f8ddd22-6199-480a-87c0-c38f4911c0cf",  # Stone
        "base_extraction_rate": 8,
        "max_extraction_rate": 15,
        "depletion_rate": 0.008,
        "respawn_rate": 0.02,
        "rarity": "common",
        "biome_types": ["mountains", "hills"],
        "required_tech": [],
        "extraction_difficulty": 2
    },
    {
        "name": "Iron Deposit",
        "description": "An underground vein of iron ore",
        "resource_id": "6e3b2395-b499-430d-9eb9-4e512a096023",  # Iron Ore
        "base_extraction_rate": 5,
        "max_extraction_rate": 12,
        "depletion_rate": 0.015,
        "respawn_rate": 0.01,
        "rarity": "common",
        "biome_types": ["mountains", "hills"],
        "required_tech": ["basic_mining"],
        "extraction_difficulty": 3
    },
    {
        "name": "Mana Crystal Formation",
        "description": "A natural crystal formation that generates magical energy",
        "resource_id": "69aff814-514c-4cf4-b1db-28665d10078e",  # Mana Crystal
        "base_extraction_rate": 2,
        "max_extraction_rate": 5,
        "depletion_rate": 0.02,
        "respawn_rate": 0.008,
        "rarity": "rare",
        "biome_types": ["mountains", "forest"],
        "required_tech": ["magical_sensing"],
        "extraction_difficulty": 4
    },
    {
        "name": "Dragon Lair Remnant",
        "description": "Ancient dragon scales can be found in old lairs",
        "resource_id": "593d211b-5fce-4681-addb-e934a6ba4bc3",  # Dragon Scale
        "base_extraction_rate": 1,
        "max_extraction_rate": 2,
        "depletion_rate": 0.05,
        "respawn_rate": 0.001,
        "rarity": "epic",
        "biome_types": ["mountains", "cave"],
        "required_tech": ["dragon_lore"],
        "extraction_difficulty": 5
    },
    
    # Post-Apocalyptic Resources
    {
        "name": "Scrap Heap",
        "description": "A pile of salvageable metal from pre-war ruins",
        "resource_id": "993330e8-d90a-46c5-a5fa-8f22f4707101",  # Scrap Metal
        "base_extraction_rate": 12,
        "max_extraction_rate": 25,
        "depletion_rate": 0.02,
        "respawn_rate": 0.0,  # No respawn for scrap
        "rarity": "common",
        "biome_types": ["urban_ruins", "wasteland"],
        "required_tech": [],
        "extraction_difficulty": 1
    },
    {
        "name": "Rubble Site",
        "description": "Collapsed buildings that can be salvaged for concrete",
        "resource_id": "073948bb-6a92-4e59-840f-72d116fb230c",  # Concrete Chunks
        "base_extraction_rate": 10,
        "max_extraction_rate": 20,
        "depletion_rate": 0.015,
        "respawn_rate": 0.0,  # No respawn for concrete
        "rarity": "common",
        "biome_types": ["urban_ruins"],
        "required_tech": [],
        "extraction_difficulty": 2
    },
    {
        "name": "Electronics Cache",
        "description": "Hidden stash of pre-war electronic components",
        "resource_id": "1418db41-fef7-4471-8f9e-d8ddb7a1e307",  # Electrical Components
        "base_extraction_rate": 3,
        "max_extraction_rate": 8,
        "depletion_rate": 0.03,
        "respawn_rate": 0.0,  # No respawn for electronics
        "rarity": "uncommon",
        "biome_types": ["urban_ruins", "industrial"],
        "required_tech": ["electronics_knowledge"],
        "extraction_difficulty": 3
    },
    {
        "name": "Fusion Reactor Ruins",
        "description": "Remnants of a pre-war fusion reactor with salvageable cells",
        "resource_id": "5b56f9d5-b304-40ba-afed-d64e2d768618",  # Fusion Cell
        "base_extraction_rate": 1,
        "max_extraction_rate": 3,
        "depletion_rate": 0.1,
        "respawn_rate": 0.0,  # No respawn for fusion cells
        "rarity": "rare",
        "biome_types": ["industrial", "wasteland"],
        "required_tech": ["fusion_technology"],
        "extraction_difficulty": 5
    },
    
    # Sci-Fi Resources
    {
        "name": "Durasteel Fabricator",
        "description": "Automated facility that produces durasteel alloy",
        "resource_id": "b93c2227-f690-491a-8d8d-4ab006933c72",  # Durasteel
        "base_extraction_rate": 8,
        "max_extraction_rate": 16,
        "depletion_rate": 0.005,
        "respawn_rate": 0.02,  # Automated production
        "rarity": "common",
        "biome_types": ["space_station", "industrial"],
        "required_tech": ["advanced_metallurgy"],
        "extraction_difficulty": 3
    },
    {
        "name": "Power Cell Array",
        "description": "Solar collection array that generates power cells",
        "resource_id": "1d2541cc-dcad-45f0-98b6-68ee666af414",  # Power Cells
        "base_extraction_rate": 6,
        "max_extraction_rate": 12,
        "depletion_rate": 0.01,
        "respawn_rate": 0.03,  # Solar powered
        "rarity": "common",
        "biome_types": ["space_station", "planet_surface"],
        "required_tech": ["energy_systems"],
        "extraction_difficulty": 2
    },
    {
        "name": "Quantum Laboratory",
        "description": "Research facility that produces quantum processors",
        "resource_id": "58420cc6-61fe-4040-9464-9a46b7ffbc67",  # Quantum Processors
        "base_extraction_rate": 2,
        "max_extraction_rate": 4,
        "depletion_rate": 0.02,
        "respawn_rate": 0.01,
        "rarity": "rare",
        "biome_types": ["space_station", "research_facility"],
        "required_tech": ["quantum_physics"],
        "extraction_difficulty": 5
    },
    
    # Cosmic Horror Resources
    {
        "name": "Ancient Stonework",
        "description": "Weathered stones from pre-human civilizations",
        "resource_id": "f6f2749d-3074-4706-a04e-0592fd2a9a2a",  # Weathered Stone
        "base_extraction_rate": 6,
        "max_extraction_rate": 12,
        "depletion_rate": 0.005,
        "respawn_rate": 0.001,  # Very slow respawn
        "rarity": "common",
        "biome_types": ["ancient_ruins", "coast"],
        "required_tech": [],
        "extraction_difficulty": 2
    },
    {
        "name": "Cursed Grove",
        "description": "Ancient forest where strange ichor seeps from the trees",
        "resource_id": "7a2b7bcb-b241-4642-99b0-046c1fbf2df8",  # Strange Ichor
        "base_extraction_rate": 1,
        "max_extraction_rate": 3,
        "depletion_rate": 0.03,
        "respawn_rate": 0.005,
        "rarity": "uncommon",
        "biome_types": ["dark_forest", "swamp"],
        "required_tech": ["occult_knowledge"],
        "extraction_difficulty": 4
    },
    {
        "name": "Elder Shrine",
        "description": "Ancient shrine where protective elder signs can be crafted",
        "resource_id": "6c6f6507-e65c-4159-82bb-fd27007541b2",  # Elder Sign
        "base_extraction_rate": 1,
        "max_extraction_rate": 1,
        "depletion_rate": 0.1,
        "respawn_rate": 0.001,
        "rarity": "rare",
        "biome_types": ["ancient_ruins", "mountains"],
        "required_tech": ["elder_lore"],
        "extraction_difficulty": 5
    }
]

async def create_resource_node_blueprint(client: httpx.AsyncClient, blueprint_data: Dict[str, Any]) -> bool:
    """Create a single resource node blueprint via API."""
    try:
        response = await client.post(
            f"{BASE_URL}/resource-node-blueprints/",
            json=blueprint_data
        )
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Created blueprint: {blueprint_data['name']} (ID: {result.get('id', 'unknown')})")
            return True
        else:
            print(f"❌ Failed to create {blueprint_data['name']}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating {blueprint_data['name']}: {e}")
        return False

async def seed_resource_node_blueprints():
    """Main function to seed all resource node blueprints."""
    print("🌱 Starting resource node blueprint seeding...")
    print(f"📡 API Base URL: {BASE_URL}")
    print(f"📦 Total blueprints to create: {len(RESOURCE_NODE_BLUEPRINTS)}")
    print("-" * 60)
    
    success_count = 0
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test API connectivity
        try:
            health_response = await client.get(f"{BASE_URL.replace('/api/v1', '')}/status")
            if health_response.status_code != 200:
                print(f"❌ API health check failed: {health_response.status_code}")
                return
            print("✅ API connectivity confirmed")
            print("-" * 60)
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            return
        
        # Create each blueprint
        for blueprint in RESOURCE_NODE_BLUEPRINTS:
            success = await create_resource_node_blueprint(client, blueprint)
            if success:
                success_count += 1
            
            # Small delay between requests
            await asyncio.sleep(0.1)
    
    print("-" * 60)
    print(f"🎉 Seeding complete! {success_count}/{len(RESOURCE_NODE_BLUEPRINTS)} blueprints created successfully")
    
    if success_count < len(RESOURCE_NODE_BLUEPRINTS):
        failed_count = len(RESOURCE_NODE_BLUEPRINTS) - success_count
        print(f"⚠️  {failed_count} blueprints failed to create")

if __name__ == "__main__":
    asyncio.run(seed_resource_node_blueprints())