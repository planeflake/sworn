from pydantic import Field
from typing import Optional, List
from uuid import UUID

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic


class ToolTierPydantic(BaseEntityPydantic):
    """
    Represents a tool tier within a specific theme progression.
    Different themes have different tool tier progressions:
    - Fantasy: Basic → Iron → Steel → Masterwork → Magical → Legendary
    - Sci-Fi: Basic → Alloy → Plasma → Quantum → Nano → Cosmic
    - Post-Apocalyptic: Scrap → Salvaged → Reinforced → Military → Experimental → Artifact
    - Lovecraftian: Mundane → Crafted → Blessed → Cursed → Eldritch → Cosmic
    """
    theme_id: UUID
    tier_name: str = ""  # "Basic", "Plasma", "Eldritch", etc.
    tier_level: int = 1  # 1-6 for progression order
    effectiveness_multiplier: float = 1.0
    description: str = ""
    icon: Optional[str] = None
    
    # Unlock requirements
    required_tech_level: int = 0
    required_materials: List[UUID] = Field(default_factory=list)  # Material resource UUIDs
    
    # Theme-specific flavor
    flavor_text: Optional[str] = None
    color_hex: Optional[str] = None  # UI theming
    
    def can_harvest_tier(self, required_tier_level: int) -> bool:
        """Check if this tool tier can harvest materials requiring the specified tier level."""
        return self.tier_level >= required_tier_level
    
    def get_efficiency_bonus(self, base_duration: int) -> int:
        """Calculate effective duration with tool efficiency."""
        return max(int(base_duration / self.effectiveness_multiplier), 5)
    
    def is_basic_tier(self) -> bool:
        """Check if this is the starting tier for the theme."""
        return self.tier_level == 1
    
    def is_max_tier(self) -> bool:
        """Check if this is the highest tier (assuming 6 tiers max)."""
        return self.tier_level == 6