"""
Seed script for creating tool tier progressions for different themes.
Run this after themes are populated in the database.
"""
import asyncio
import uuid
from typing import Dict, List, Tuple

from app.core.database import get_async_db_session
from app.game_state.repositories.tool_tier_repository import ToolTierRepository
from app.game_state.managers.tool_tier_manager import ToolTierManager


# Define tool tier progressions for each theme type
THEME_PROGRESSIONS: Dict[str, List[Tuple[str, str, int, float, str, str]]] = {
    "fantasy": [
        ("Basic Tools", "Basic", 1, 1.0, "#8B4513", "Simple handmade tools crafted from wood and stone"),
        ("Iron Tools", "Iron", 2, 1.2, "#708090", "Forged iron implements, durable and reliable"),
        ("Steel Tools", "Steel", 3, 1.5, "#4682B4", "High-quality steel craftsmanship with excellent edge retention"),
        ("Masterwork Tools", "Masterwork", 4, 2.0, "#DAA520", "Perfectly crafted tools by master artisans"),
        ("Magical Tools", "Magical", 5, 3.0, "#9370DB", "Enchanted with mystical power, defying natural limits"),
        ("Legendary Tools", "Legendary", 6, 5.0, "#FFD700", "Tools of legend and myth, forged by gods themselves")
    ],
    "sci-fi": [
        ("Basic Tools", "Basic", 1, 1.0, "#696969", "Standard polymer construction tools"),
        ("Alloy Tools", "Alloy", 2, 1.2, "#778899", "Advanced metal composite construction"),
        ("Plasma Tools", "Plasma", 3, 1.5, "#FF6347", "Plasma-edge cutting technology"),
        ("Quantum Tools", "Quantum", 4, 2.0, "#40E0D0", "Quantum-enhanced precision instruments"),
        ("Nano Tools", "Nano", 5, 3.0, "#00CED1", "Nanotechnology integrated molecular assembly"),
        ("Cosmic Tools", "Cosmic", 6, 5.0, "#9932CC", "Harvesting cosmic energy and dark matter")
    ],
    "post-apocalyptic": [
        ("Scrap Tools", "Scrap", 1, 1.0, "#8B7355", "Cobbled together from debris and salvage"),
        ("Salvaged Tools", "Salvaged", 2, 1.2, "#A0522D", "Carefully restored pre-war equipment"),
        ("Reinforced Tools", "Reinforced", 3, 1.5, "#2F4F4F", "Jury-rigged improvements with metal plating"),
        ("Military Tools", "Military", 4, 2.0, "#556B2F", "Pre-war military grade equipment"),
        ("Experimental Tools", "Experimental", 5, 3.0, "#800080", "Mad scientist creations and jury-rigged tech"),
        ("Artifact Tools", "Artifact", 6, 5.0, "#B8860B", "Mysterious pre-war relics of unknown origin")
    ],
    "lovecraftian": [
        ("Mundane Tools", "Mundane", 1, 1.0, "#696969", "Ordinary worldly implements made by human hands"),
        ("Crafted Tools", "Crafted", 2, 1.2, "#8B4513", "Skillfully made tools with careful attention"),
        ("Blessed Tools", "Blessed", 3, 1.5, "#F0E68C", "Sanctified by ritual and divine blessing"),
        ("Cursed Tools", "Cursed", 4, 2.0, "#8B0000", "Tainted by dark forces and forbidden knowledge"),
        ("Eldritch Tools", "Eldritch", 5, 3.0, "#4B0082", "Touched by otherworldly power beyond understanding"),
        ("Cosmic Tools", "Cosmic", 6, 5.0, "#000080", "Beyond mortal comprehension, reality-warping")
    ],
    "steampunk": [
        ("Brass Tools", "Brass", 1, 1.0, "#CD7F32", "Basic brass and copper construction"),
        ("Steam Tools", "Steam", 2, 1.2, "#B87333", "Steam-powered mechanical assistance"),
        ("Clockwork Tools", "Clockwork", 3, 1.5, "#DAA520", "Precision clockwork mechanisms"),
        ("Pneumatic Tools", "Pneumatic", 4, 2.0, "#4682B4", "Compressed air powered efficiency"),
        ("Aetheric Tools", "Aetheric", 5, 3.0, "#9370DB", "Powered by mysterious aetheric energy"),
        ("Analytical Tools", "Analytical", 6, 5.0, "#FFD700", "Difference engine calculated perfection")
    ],
    "cyberpunk": [
        ("Street Tools", "Street", 1, 1.0, "#2F2F2F", "Improvised street-level tech"),
        ("Corporate Tools", "Corporate", 2, 1.2, "#4169E1", "Mass-produced corporate equipment"),
        ("Modded Tools", "Modded", 3, 1.5, "#FF6347", "Black market modifications and upgrades"),
        ("Military Tools", "Military", 4, 2.0, "#556B2F", "Restricted military-grade hardware"),
        ("Prototype Tools", "Prototype", 5, 3.0, "#9932CC", "Cutting-edge experimental technology"),
        ("AI Tools", "AI", 6, 5.0, "#00BFFF", "AI-integrated adaptive smart tools")
    ]
}


async def seed_tool_tiers_for_theme(theme_id: uuid.UUID, theme_name: str) -> List[uuid.UUID]:
    """Create tool tier progression for a specific theme."""
    async with get_async_db_session() as db_session:
        repository = ToolTierRepository(db_session)
        
        # Check if theme already has tool tiers
        existing_tiers = await repository.get_by_theme(theme_id)
        if existing_tiers:
            print(f"Tool tiers already exist for theme {theme_name}, skipping...")
            return [tier.entity_id for tier in existing_tiers]
        
        theme_key = theme_name.lower().replace(" ", "-").replace("_", "-")
        if theme_key not in THEME_PROGRESSIONS:
            print(f"No progression defined for theme '{theme_name}', using fantasy fallback")
            theme_key = "fantasy"
        
        progression = THEME_PROGRESSIONS[theme_key]
        created_tier_ids = []
        
        print(f"Creating {len(progression)} tool tiers for theme: {theme_name}")
        
        for name, tier_name, level, multiplier, color, flavor in progression:
            tier_entity = ToolTierManager.create_tool_tier(
                name=name,
                theme_id=theme_id,
                tier_name=tier_name,
                tier_level=level,
                effectiveness_multiplier=multiplier,
                description=f"{tier_name} tier tools for {theme_name} theme",
                required_tech_level=max(0, level - 1),
                flavor_text=flavor,
                color_hex=color
            )
            
            created_tier = await repository.create(tier_entity)
            created_tier_ids.append(created_tier.entity_id)
            print(f"  Created: {name} (Level {level}, {multiplier}x efficiency)")
        
        await db_session.commit()
        return created_tier_ids


async def seed_all_theme_tool_tiers():
    """Seed tool tiers for all available themes in the database."""
    print("Starting tool tier seeding for all themes...")
    
    # Note: This is a simplified version. In practice, you'd query the themes table
    # to get actual theme IDs and names from the database
    
    sample_themes = [
        ("fantasy", "Fantasy"),
        ("sci-fi", "Sci-Fi"),
        ("post-apocalyptic", "Post-Apocalyptic"),
        ("lovecraftian", "Lovecraftian"),
        ("steampunk", "Steampunk"),
        ("cyberpunk", "Cyberpunk")
    ]
    
    print("WARNING: This is using sample theme IDs. In production, fetch real theme IDs from database.")
    print("Sample progression creation for demonstration:")
    
    for theme_key, theme_name in sample_themes:
        print(f"\n=== {theme_name} Theme Tool Progression ===")
        progression = THEME_PROGRESSIONS[theme_key]
        for name, tier_name, level, multiplier, color, flavor in progression:
            print(f"  {level}. {name} ({tier_name}) - {multiplier}x efficiency")
            print(f"     Color: {color} | {flavor}")
    
    print("\nTo actually seed data, update this script with real theme IDs from your database.")


if __name__ == "__main__":
    asyncio.run(seed_all_theme_tool_tiers())