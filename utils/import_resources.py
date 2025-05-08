import requests
import json
import time

# Your API endpoint
url = "http://localhost:8000/api/v1/resources/"

# Headers
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

# Resources list (from above)
resources = [
    # Common Building Materials
    {
        "name": "Oak Wood",
        "description": "Sturdy wood from oak trees, perfect for basic construction.",
        "rarity": "Common",
        "stack_size": 50,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    },
    {
        "name": "Stone",
        "description": "Basic building material quarried from mountains.",
        "rarity": "Common",
        "stack_size": 50,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    },
    {
        "name": "Clay",
        "description": "Moldable earth material used for pottery and brick making.",
        "rarity": "Common",
        "stack_size": 30,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    },
    
    # Basic Metals
    {
        "name": "Iron Ore",
        "description": "Raw iron ore that can be smelted into iron ingots.",
        "rarity": "Common",
        "stack_size": 40,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    },
    {
        "name": "Copper Ore",
        "description": "Raw copper ore that can be smelted into copper ingots.",
        "rarity": "Common",
        "stack_size": 40,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    },
    
    # Processed Materials
    {
        "name": "Iron Ingot",
        "description": "Refined iron metal used in crafting weapons and tools.",
        "rarity": "Common",
        "stack_size": 30,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    },
    {
        "name": "Steel Ingot",
        "description": "Alloy of iron and carbon, stronger than pure iron.",
        "rarity": "Uncommon",
        "stack_size": 25,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    },
    
    # Food Resources
    {
        "name": "Wheat",
        "description": "Basic grain that can be milled into flour.",
        "rarity": "Common",
        "stack_size": 64,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    },
    {
        "name": "Apple",
        "description": "Fresh fruit that restores a small amount of health.",
        "rarity": "Common",
        "stack_size": 16,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    },
    
    # Rare Resources
    {
        "name": "Gold Nugget",
        "description": "Precious metal used for currency and luxury items.",
        "rarity": "Uncommon",
        "stack_size": 20,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    },
    {
        "name": "Diamond",
        "description": "Rare gemstone with exceptional hardness and brilliance.",
        "rarity": "Rare",
        "stack_size": 10,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    },
    
    # Magical Components
    {
        "name": "Mana Crystal",
        "description": "A crystal infused with magical energy.",
        "rarity": "Uncommon",
        "stack_size": 15,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    },
    {
        "name": "Phoenix Feather",
        "description": "A vibrant feather that radiates heat, shed by a phoenix.",
        "rarity": "Rare",
        "stack_size": 5,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    },
    {
        "name": "Dragon Scale",
        "description": "An extremely durable scale from a dragon's hide.",
        "rarity": "Epic",
        "stack_size": 3,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    },
    
    # Legendary Items
    {
        "name": "Star Fragment",
        "description": "A shard of a fallen star with immense magical potential.",
        "rarity": "Legendary",
        "stack_size": 1,
        "status": "Active",
        "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
    }
]

# Send requests for each resource
for resource in resources:
    response = requests.post(url, headers=headers, data=json.dumps(resource))
    
    # Print results
    print(f"Creating {resource['name']}...")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200 or response.status_code == 201:
        print("Success!")
    else:
        print(f"Error: {response.text}")
    
    # Add a short delay to prevent overwhelming the server
    time.sleep(0.5)

print("Resource creation complete!")