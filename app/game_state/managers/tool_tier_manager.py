import uuid
from typing import Optional, List
from datetime import datetime

from app.game_state.entities.core.tool_tier_pydantic import ToolTierPydantic
from .base_manager import BaseManager


class ToolTierManager(BaseManager[ToolTierPydantic]):
    """Manager for tool tier business logic and creation."""
    
    @staticmethod
    def create_tool_tier(
        name: str,
        theme_id: uuid.UUID,
        tier_name: str,
        tier_level: int,
        effectiveness_multiplier: float = 1.0,
        description: str = "",
        icon: Optional[str] = None,
        required_tech_level: int = 0,
        required_materials: Optional[List[uuid.UUID]] = None,
        flavor_text: Optional[str] = None,
        color_hex: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None,
        **kwargs
    ) -> ToolTierPydantic:
        """Create a new tool tier."""
        create_params = {
            "name": name,
            "theme_id": theme_id,
            "tier_name": tier_name,
            "tier_level": tier_level,
            "effectiveness_multiplier": effectiveness_multiplier,
            "description": description,
            "icon": icon,
            "required_tech_level": required_tech_level,
            "required_materials": required_materials or [],
            "flavor_text": flavor_text,
            "color_hex": color_hex,
            **kwargs
        }
        
        if entity_id:
            create_params["entity_id"] = entity_id
            
        return ToolTierManager.create(ToolTierPydantic, **create_params)
    
    @staticmethod
    def create_theme_progression(theme_id: uuid.UUID, theme_name: str) -> List[ToolTierPydantic]:
        """Create a complete tool tier progression for a theme."""
        progressions = {
            "fantasy": [
                ("Basic Tools", "Basic", 1, 1.0, "#8B4513", "Simple handmade tools"),
                ("Iron Tools", "Iron", 2, 1.2, "#708090", "Forged iron implements"),
                ("Steel Tools", "Steel", 3, 1.5, "#4682B4", "High-quality steel craftsmanship"),
                ("Masterwork Tools", "Masterwork", 4, 2.0, "#DAA520", "Perfectly crafted tools"),
                ("Magical Tools", "Magical", 5, 3.0, "#9370DB", "Enchanted with mystical power"),
                ("Legendary Tools", "Legendary", 6, 5.0, "#FFD700", "Tools of legend and myth")
            ],
            "sci-fi": [
                ("Basic Tools", "Basic", 1, 1.0, "#696969", "Standard polymer tools"),
                ("Alloy Tools", "Alloy", 2, 1.2, "#778899", "Advanced metal composites"),
                ("Plasma Tools", "Plasma", 3, 1.5, "#FF6347", "Plasma-edge cutting tools"),
                ("Quantum Tools", "Quantum", 4, 2.0, "#40E0D0", "Quantum-enhanced precision"),
                ("Nano Tools", "Nano", 5, 3.0, "#00CED1", "Nanotechnology integrated"),
                ("Cosmic Tools", "Cosmic", 6, 5.0, "#9932CC", "Harvesting cosmic energy")
            ],
            "post-apocalyptic": [
                ("Scrap Tools", "Scrap", 1, 1.0, "#8B7355", "Cobbled together from debris"),
                ("Salvaged Tools", "Salvaged", 2, 1.2, "#A0522D", "Carefully restored equipment"),
                ("Reinforced Tools", "Reinforced", 3, 1.5, "#2F4F4F", "Jury-rigged improvements"),
                ("Military Tools", "Military", 4, 2.0, "#556B2F", "Pre-war military grade"),
                ("Experimental Tools", "Experimental", 5, 3.0, "#800080", "Mad scientist creations"),
                ("Artifact Tools", "Artifact", 6, 5.0, "#B8860B", "Mysterious pre-war relics")
            ],
            "lovecraftian": [
                ("Mundane Tools", "Mundane", 1, 1.0, "#696969", "Ordinary worldly implements"),
                ("Crafted Tools", "Crafted", 2, 1.2, "#8B4513", "Skillfully made tools"),
                ("Blessed Tools", "Blessed", 3, 1.5, "#F0E68C", "Sanctified by ritual"),
                ("Cursed Tools", "Cursed", 4, 2.0, "#8B0000", "Tainted by dark forces"),
                ("Eldritch Tools", "Eldritch", 5, 3.0, "#4B0082", "Touched by otherworldly power"),
                ("Cosmic Tools", "Cosmic", 6, 5.0, "#000080", "Beyond mortal comprehension")
            ]
        }
        
        theme_lower = theme_name.lower()
        if theme_lower not in progressions:
            theme_lower = "fantasy"  # Default fallback
        
        tiers = []
        for tier_data in progressions[theme_lower]:
            name, tier_name, level, multiplier, color, flavor = tier_data
            tier = ToolTierManager.create_tool_tier(
                name=name,
                theme_id=theme_id,
                tier_name=tier_name,
                tier_level=level,
                effectiveness_multiplier=multiplier,
                color_hex=color,
                flavor_text=flavor,
                required_tech_level=level - 1  # Tech requirement scales with tier
            )
            tiers.append(tier)
        
        return tiers
    
    @staticmethod
    def calculate_harvest_compatibility(tool_tier_level: int, required_tier_level: int) -> bool:
        """Check if a tool tier can harvest materials requiring a specific tier."""
        return tool_tier_level >= required_tier_level
    
    @staticmethod
    def get_efficiency_multiplier(tool_tier_level: int) -> float:
        """Get efficiency multiplier based on tier level."""
        # Base formula: each tier provides increasing efficiency
        multipliers = {1: 1.0, 2: 1.2, 3: 1.5, 4: 2.0, 5: 3.0, 6: 5.0}
        return multipliers.get(tool_tier_level, 1.0)