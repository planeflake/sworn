#!/usr/bin/env python3
"""
COMPREHENSIVE Location Subtypes for ALL Themes and Location Types
Complete matrix coverage of theme/location type combinations
"""

# Your theme IDs (from your database)
THEMES = {
    "sci_fi": "104275ef-4ae9-4364-86f1-2cbeb886c3ad",
    "post_apocalyptic": "1265b705-778e-4df1-b7ac-2a3f7a01ac22",
    "lovecraftian": "72aab8f1-2e04-45aa-8075-6936e716f09b",
    "warhammer_40k": "7cdd3506-4828-4269-a96e-e7fea047132b",
    "fantasy_medieval": "b2494b91-f7d1-4c8d-9da2-c628816ed9de",  # Already done for Area
    "runeslicer": "c0d8944d-4ebf-42bc-b7ad-8e5edf9c296e",
    "warhammer_fantasy": "cdef42d5-6d3a-4773-bb34-0668e0dea89e"
}

# Your location type IDs (from your database)
LOCATION_TYPES = {
    "dimension": "f76847fe-05ef-4b84-892e-d2c87d8894b6",
    "cosmos": "59df72e8-3b86-4b6b-a435-f891fa31a2ea",
    "galaxy": "503879ac-acc4-43d6-afa4-29d4a5bb2348",
    "star_system": "14852fa2-b3b3-43b9-8e79-e96e8b717f29",
    "world": "a6a0d734-8de1-4a6a-bb7b-fdef23236fdd",
    "celestial_body": "cabcc823-46fa-437d-b91f-d70f06df022f",
    "constructed_habitat": "3d1c462a-eeb4-436b-aa8c-34944762bfd6",
    "elemental_plane": "899ea475-99e2-4a59-9f02-bf460a7314a8",
    "zone": "87e024f8-6e82-4f91-aa65-e9cf5cec464e",
    "area": "f1df65be-0db7-40d9-952f-3f8ff3b803c1",
    "point_of_interest": "1e93492f-4630-49aa-99f2-b714a590c600"
}

# ==============================================================================
# AREA SUBTYPES - All Non-Fantasy Themes (Fantasy already done)
# ==============================================================================

# SCI-FI AREAS
sci_fi_areas = [
    {
        "code": "space_port_scifi",
        "name": "Space Port",
        "description": "A bustling hub for interstellar travel and trade with advanced docking facilities.",
        "location_type_id": LOCATION_TYPES["area"],
        "theme_id": THEMES["sci_fi"],
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of inhabitants",
                "min_value": 1000,
                "max_value": 500000
            },
            {
                "name": "docking_bays",
                "type": "integer",
                "description": "Number of spacecraft docking bays",
                "min_value": 5,
                "max_value": 500
            }
        ],
        "optional_attributes": [
            {
                "name": "max_ship_class",
                "type": "string",
                "enum": ["fighter", "corvette", "frigate", "cruiser", "battleship"],
                "description": "Largest ship class that can dock"
            }
        ],
        "tags": ["sci-fi", "settlement", "transport", "trade"],
        "rarity": "common",
        "generation_weight": 1.3
    },
    {
        "code": "research_station_scifi",
        "name": "Research Station",
        "description": "A scientific outpost dedicated to advanced research and experimentation.",
        "location_type_id": LOCATION_TYPES["area"],
        "theme_id": THEMES["sci_fi"],
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of researchers and support staff",
                "min_value": 50,
                "max_value": 10000
            },
            {
                "name": "research_focus",
                "type": "string",
                "enum": ["physics", "biology", "xenology", "weapons", "FTL", "AI"],
                "description": "Primary research discipline"
            }
        ],
        "optional_attributes": [
            {
                "name": "security_level",
                "type": "string",
                "enum": ["open", "restricted", "classified", "black_site"],
                "description": "Access restrictions"
            }
        ],
        "tags": ["sci-fi", "settlement", "research", "technology"],
        "rarity": "uncommon",
        "generation_weight": 0.8
    },
    {
        "code": "colony_dome_scifi",
        "name": "Colony Dome",
        "description": "A enclosed settlement with artificial atmosphere on hostile worlds.",
        "location_type_id": LOCATION_TYPES["area"],
        "theme_id": THEMES["sci_fi"],
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of colonists",
                "min_value": 500,
                "max_value": 100000
            },
            {
                "name": "dome_integrity",
                "type": "string",
                "enum": ["perfect", "good", "damaged", "critical"],
                "description": "Structural condition of the dome"
            }
        ],
        "optional_attributes": [
            {
                "name": "life_support_years",
                "type": "number",
                "description": "Years of life support remaining"
            }
        ],
        "tags": ["sci-fi", "settlement", "colony", "enclosed"],
        "rarity": "common",
        "generation_weight": 1.1
    }
]

# POST-APOCALYPTIC AREAS
post_apocalyptic_areas = [
    {
        "code": "vault_settlement",
        "name": "Vault Settlement",
        "description": "An underground bunker community that survived the apocalypse.",
        "location_type_id": LOCATION_TYPES["area"],
        "theme_id": THEMES["post_apocalyptic"],
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of vault dwellers",
                "min_value": 50,
                "max_value": 2000
            },
            {
                "name": "vault_condition",
                "type": "string",
                "enum": ["pristine", "good", "damaged", "failing", "abandoned"],
                "description": "Current state of vault systems"
            }
        ],
        "optional_attributes": [
            {
                "name": "years_sealed",
                "type": "integer",
                "description": "How many years the vault was sealed"
            }
        ],
        "tags": ["post-apocalyptic", "settlement", "underground", "survival"],
        "rarity": "uncommon",
        "generation_weight": 0.6
    },
    {
        "code": "scavenger_town",
        "name": "Scavenger Town",
        "description": "A settlement built around salvaging and trading pre-war technology.",
        "location_type_id": LOCATION_TYPES["area"],
        "theme_id": THEMES["post_apocalyptic"],
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of inhabitants",
                "min_value": 100,
                "max_value": 5000
            },
            {
                "name": "tech_level",
                "type": "string",
                "enum": ["primitive", "scavenged", "jury_rigged", "restored"],
                "description": "Technological sophistication"
            }
        ],
        "optional_attributes": [
            {
                "name": "trade_specialty",
                "type": "string",
                "description": "What the town specializes in trading"
            }
        ],
        "tags": ["post-apocalyptic", "settlement", "scavenging", "trade"],
        "rarity": "common",
        "generation_weight": 1.2
    },
    {
        "code": "raider_stronghold",
        "name": "Raider Stronghold",
        "description": "A fortified base where hostile wasteland gangs gather and plan raids.",
        "location_type_id": LOCATION_TYPES["area"],
        "theme_id": THEMES["post_apocalyptic"],
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of raiders",
                "min_value": 20,
                "max_value": 500
            },
            {
                "name": "threat_level",
                "type": "string",
                "enum": ["minor", "moderate", "dangerous", "lethal"],
                "description": "How dangerous the raiders are"
            }
        ],
        "optional_attributes": [
            {
                "name": "leader_name",
                "type": "string",
                "description": "Name of the raider boss"
            }
        ],
        "tags": ["post-apocalyptic", "settlement", "hostile", "raiders"],
        "rarity": "common",
        "generation_weight": 1.0
    }
]

# WARHAMMER 40K AREAS
warhammer_40k_areas = [
    {
        "code": "hive_city_40k",
        "name": "Hive City",
        "description": "A massive arcology housing billions in towering spires reaching into the sky.",
        "location_type_id": LOCATION_TYPES["area"],
        "theme_id": THEMES["warhammer_40k"],
        "required_attributes": [
            {
                "name": "population_billions",
                "type": "number",
                "description": "Population in billions",
                "min_value": 1,
                "max_value": 100
            },
            {
                "name": "spire_count",
                "type": "integer",
                "description": "Number of major hive spires",
                "min_value": 1,
                "max_value": 20
            }
        ],
        "optional_attributes": [
            {
                "name": "underhive_threat",
                "type": "string",
                "enum": ["minimal", "contained", "significant", "critical"],
                "description": "Danger level in the underhive"
            }
        ],
        "tags": ["warhammer-40k", "settlement", "hive", "urban", "imperial"],
        "rarity": "uncommon",
        "generation_weight": 0.5
    },
    {
        "code": "imperial_outpost_40k",
        "name": "Imperial Outpost",
        "description": "A frontier garrison maintaining Imperial authority in remote sectors.",
        "location_type_id": LOCATION_TYPES["area"],
        "theme_id": THEMES["warhammer_40k"],
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of Imperial personnel",
                "min_value": 100,
                "max_value": 10000
            },
            {
                "name": "regiment_type",
                "type": "string",
                "enum": ["astra_militarum", "planetary_defense", "arbites", "naval"],
                "description": "Type of Imperial forces stationed"
            }
        ],
        "optional_attributes": [
            {
                "name": "astropath_present",
                "type": "boolean",
                "description": "Whether an astropath is stationed here"
            }
        ],
        "tags": ["warhammer-40k", "settlement", "military", "imperial"],
        "rarity": "common",
        "generation_weight": 0.9
    }
]

# LOVECRAFTIAN AREAS
lovecraftian_areas = [
    {
        "code": "eldritch_town",
        "name": "Eldritch Town",
        "description": "A seemingly normal town where cosmic horrors lurk beneath mundane life.",
        "location_type_id": LOCATION_TYPES["area"],
        "theme_id": THEMES["lovecraftian"],
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of inhabitants",
                "min_value": 500,
                "max_value": 20000
            },
            {
                "name": "corruption_level",
                "type": "string",
                "enum": ["subtle", "noticeable", "obvious", "overwhelming"],
                "description": "How apparent the eldritch influence is"
            }
        ],
        "optional_attributes": [
            {
                "name": "cult_active",
                "type": "boolean",
                "description": "Whether an active cult operates here"
            }
        ],
        "tags": ["lovecraftian", "settlement", "horror", "cosmic"],
        "rarity": "uncommon",
        "generation_weight": 0.7
    },
    {
        "code": "isolated_mansion",
        "name": "Isolated Mansion",
        "description": "A remote estate where terrible secrets and ancient horrors reside.",
        "location_type_id": LOCATION_TYPES["area"],
        "theme_id": THEMES["lovecraftian"],
        "required_attributes": [
            {
                "name": "population",
                "type": "integer",
                "description": "Number of residents and staff",
                "min_value": 1,
                "max_value": 50
            },
            {
                "name": "age_years",
                "type": "integer",
                "description": "Age of the mansion",
                "min_value": 50,
                "max_value": 500
            }
        ],
        "optional_attributes": [
            {
                "name": "library_present",
                "type": "boolean",
                "description": "Whether it contains a library of forbidden knowledge"
            }
        ],
        "tags": ["lovecraftian", "settlement", "mansion", "isolated", "horror"],
        "rarity": "rare",
        "generation_weight": 0.3
    }
]

# ==============================================================================
# GALAXY SUBTYPES - Multiple Themes
# ==============================================================================

galaxy_subtypes = [
    # Sci-Fi Galaxies
    {
        "code": "spiral_galaxy_scifi",
        "name": "Spiral Galaxy",
        "description": "A classic spiral galaxy containing billions of star systems and spacefaring civilizations.",
        "location_type_id": LOCATION_TYPES["galaxy"],
        "theme_id": THEMES["sci_fi"],
        "required_attributes": [
            {
                "name": "galaxy_type",
                "type": "string",
                "enum": ["spiral"],
                "description": "Type of galaxy"
            },
            {
                "name": "arm_count",
                "type": "integer",
                "description": "Number of spiral arms",
                "min_value": 2,
                "max_value": 8
            }
        ],
        "optional_attributes": [
            {
                "name": "dominant_species",
                "type": "string",
                "description": "Most influential spacefaring species"
            }
        ],
        "tags": ["sci-fi", "galaxy", "spiral", "spacefaring"],
        "rarity": "common",
        "generation_weight": 1.5
    },
    # Warhammer 40K Galaxy
    {
        "code": "galaxy_40k",
        "name": "War-Torn Galaxy",
        "description": "A galaxy consumed by endless war, where only war exists in the grim darkness.",
        "location_type_id": LOCATION_TYPES["galaxy"],
        "theme_id": THEMES["warhammer_40k"],
        "required_attributes": [
            {
                "name": "galaxy_type",
                "type": "string",
                "enum": ["spiral"],
                "description": "Type of galaxy"
            },
            {
                "name": "warp_storm_intensity",
                "type": "string",
                "enum": ["calm", "turbulent", "violent", "impassable"],
                "description": "Current state of warp travel"
            }
        ],
        "optional_attributes": [
            {
                "name": "major_threats",
                "type": "array",
                "description": "Primary galactic threats",
                "items": {"type": "string"}
            }
        ],
        "tags": ["warhammer-40k", "galaxy", "war", "grimdark"],
        "rarity": "rare",
        "generation_weight": 0.2
    }
]

# ==============================================================================
# STAR SYSTEM SUBTYPES
# ==============================================================================

star_system_subtypes = [
    # Sci-Fi Star Systems
    {
        "code": "binary_system_scifi",
        "name": "Binary Star System",
        "description": "A system with two stars creating unique planetary conditions and trade routes.",
        "location_type_id": LOCATION_TYPES["star_system"],
        "theme_id": THEMES["sci_fi"],
        "required_attributes": [
            {
                "name": "primary_star_class",
                "type": "string",
                "enum": ["O", "B", "A", "F", "G", "K", "M"],
                "description": "Spectral class of primary star"
            },
            {
                "name": "secondary_star_class",
                "type": "string",
                "enum": ["O", "B", "A", "F", "G", "K", "M"],
                "description": "Spectral class of secondary star"
            }
        ],
        "optional_attributes": [
            {
                "name": "habitable_worlds",
                "type": "integer",
                "description": "Number of potentially habitable planets"
            }
        ],
        "tags": ["sci-fi", "star-system", "binary", "astronomy"],
        "rarity": "common",
        "generation_weight": 1.2
    },
    # Post-Apocalyptic (Dead System)
    {
        "code": "dead_system_postapoc",
        "name": "Dead System",
        "description": "A star system where civilization once thrived but now lies in radioactive ruins.",
        "location_type_id": LOCATION_TYPES["star_system"],
        "theme_id": THEMES["post_apocalyptic"],
        "required_attributes": [
            {
                "name": "primary_star_class",
                "type": "string",
                "enum": ["G", "K", "M"],
                "description": "Spectral class of the star"
            },
            {
                "name": "apocalypse_type",
                "type": "string",
                "enum": ["nuclear_war", "plague", "AI_rebellion", "alien_invasion"],
                "description": "What destroyed this system"
            }
        ],
        "optional_attributes": [
            {
                "name": "years_since_fall",
                "type": "integer",
                "description": "Years since civilization collapsed"
            }
        ],
        "tags": ["post-apocalyptic", "star-system", "dead", "ruins"],
        "rarity": "uncommon",
        "generation_weight": 0.6
    }
]

# ==============================================================================
# CONSTRUCTED HABITAT SUBTYPES
# ==============================================================================

constructed_habitat_subtypes = [
    # Sci-Fi Habitats
    {
        "code": "o_neill_cylinder",
        "name": "O'Neill Cylinder",
        "description": "A massive rotating space habitat providing artificial gravity through centrifugal force.",
        "location_type_id": LOCATION_TYPES["constructed_habitat"],
        "theme_id": THEMES["sci_fi"],
        "required_attributes": [
            {
                "name": "length_km",
                "type": "number",
                "description": "Length in kilometers",
                "min_value": 1,
                "max_value": 100
            },
            {
                "name": "population",
                "type": "integer",
                "description": "Number of inhabitants",
                "min_value": 10000,
                "max_value": 10000000
            }
        ],
        "optional_attributes": [
            {
                "name": "artificial_gravity_g",
                "type": "number",
                "description": "Gravity as fraction of Earth gravity"
            }
        ],
        "tags": ["sci-fi", "habitat", "space-station", "artificial-gravity"],
        "rarity": "uncommon",
        "generation_weight": 0.8
    },
    # Warhammer 40K Habitat
    {
        "code": "space_hulk_40k",
        "name": "Space Hulk",
        "description": "A massive conglomeration of fused starships drifting through the warp.",
        "location_type_id": LOCATION_TYPES["constructed_habitat"],
        "theme_id": THEMES["warhammer_40k"],
        "required_attributes": [
            {
                "name": "ship_count",
                "type": "integer",
                "description": "Number of fused vessels",
                "min_value": 5,
                "max_value": 100
            },
            {
                "name": "threat_level",
                "type": "string",
                "enum": ["minimal", "moderate", "high", "extreme"],
                "description": "Danger to boarding parties"
            }
        ],
        "optional_attributes": [
            {
                "name": "genestealer_infestation",
                "type": "boolean",
                "description": "Whether genestealers are present"
            }
        ],
        "tags": ["warhammer-40k", "habitat", "space-hulk", "dangerous"],
        "rarity": "rare",
        "generation_weight": 0.3
    }
]

# ==============================================================================
# CELESTIAL BODY SUBTYPES
# ==============================================================================

celestial_body_subtypes = [
    # Sci-Fi Planets
    {
        "code": "terran_world_scifi",
        "name": "Terran World",
        "description": "An Earth-like planet capable of supporting human life without artificial support.",
        "location_type_id": LOCATION_TYPES["celestial_body"],
        "theme_id": THEMES["sci_fi"],
        "required_attributes": [
            {
                "name": "atmosphere_type",
                "type": "string",
                "enum": ["terran", "thin", "thick", "toxic", "none"],
                "description": "Atmospheric composition and pressure"
            },
            {
                "name": "biosphere_level",
                "type": "string",
                "enum": ["dead", "primitive", "complex", "garden"],
                "description": "Complexity of native life"
            }
        ],
        "optional_attributes": [
            {
                "name": "native_sentients",
                "type": "boolean",
                "description": "Whether intelligent life evolved here"
            }
        ],
        "tags": ["sci-fi", "planet", "terran", "habitable"],
        "rarity": "uncommon",
        "generation_weight": 0.7
    },
    # Post-Apocalyptic Planet
    {
        "code": "irradiated_world",
        "name": "Irradiated World",
        "description": "A planet devastated by nuclear war, its surface scarred by radiation and mutation.",
        "location_type_id": LOCATION_TYPES["celestial_body"],
        "theme_id": THEMES["post_apocalyptic"],
        "required_attributes": [
            {
                "name": "radiation_level",
                "type": "string",
                "enum": ["background", "elevated", "dangerous", "lethal"],
                "description": "Surface radiation intensity"
            },
            {
                "name": "survivor_population",
                "type": "integer",
                "description": "Estimated remaining population",
                "min_value": 0,
                "max_value": 100000000
            }
        ],
        "optional_attributes": [
            {
                "name": "years_since_war",
                "type": "integer",
                "description": "Years since the nuclear exchange"
            }
        ],
        "tags": ["post-apocalyptic", "planet", "irradiated", "wasteland"],
        "rarity": "uncommon",
        "generation_weight": 0.6
    }
]

# ==============================================================================
# COMBINE ALL SUBTYPES
# ==============================================================================

all_comprehensive_subtypes = []

# Area subtypes for all non-fantasy themes
all_comprehensive_subtypes.extend(sci_fi_areas)
all_comprehensive_subtypes.extend(post_apocalyptic_areas)
all_comprehensive_subtypes.extend(warhammer_40k_areas)
all_comprehensive_subtypes.extend(lovecraftian_areas)

# Other location types
all_comprehensive_subtypes.extend(galaxy_subtypes)
all_comprehensive_subtypes.extend(star_system_subtypes)
all_comprehensive_subtypes.extend(constructed_habitat_subtypes)
all_comprehensive_subtypes.extend(celestial_body_subtypes)

# Summary
print(f"📊 COMPREHENSIVE COVERAGE SUMMARY:")
print(f"📍 Total subtypes: {len(all_comprehensive_subtypes)}")
print(f"🎭 Themes covered: {len(set(item['theme_id'] for item in all_comprehensive_subtypes))}")
print(f"🏗️ Location types covered: {len(set(item['location_type_id'] for item in all_comprehensive_subtypes))}")
print()
print("📋 BREAKDOWN BY LOCATION TYPE:")
location_type_names = {v: k for k, v in LOCATION_TYPES.items()}
for loc_type_id in set(item['location_type_id'] for item in all_comprehensive_subtypes):
    count = len([item for item in all_comprehensive_subtypes if item['location_type_id'] == loc_type_id])
    print(f"   {location_type_names[loc_type_id]}: {count} subtypes")

print()
print("🎨 BREAKDOWN BY THEME:")
theme_names = {v: k for k, v in THEMES.items()}
for theme_id in set(item['theme_id'] for item in all_comprehensive_subtypes):
    count = len([item for item in all_comprehensive_subtypes if item['theme_id'] == theme_id])
    print(f"   {theme_names[theme_id]}: {count} subtypes")

# Collections for targeted imports
area_subtypes_only = [item for item in all_comprehensive_subtypes if item['location_type_id'] == LOCATION_TYPES['area']]
sci_fi_only = [item for item in all_comprehensive_subtypes if item['theme_id'] == THEMES['sci_fi']]
warhammer_40k_only = [item for item in all_comprehensive_subtypes if item['theme_id'] == THEMES['warhammer_40k']]

print(f"\n🎯 READY FOR IMPORT:")
print(f"   all_comprehensive_subtypes: {len(all_comprehensive_subtypes)} items")
print(f"   area_subtypes_only: {len(area_subtypes_only)} items")
print(f"   sci_fi_only: {len(sci_fi_only)} items")
print(f"   warhammer_40k_only: {len(warhammer_40k_only)} items")