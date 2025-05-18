
import enum

class ItemRarity(enum.Enum):
    """Enum for item rarity levels."""
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    EPIC = "Epic"
    LEGENDARY = "Legendary"
    MYTHICAL = "Mythical"
    HEAVENLY = "Heavenly"  # Fixed capitalization

class ItemStatus(enum.Enum):
    """Enum for item condition status."""
    PRISTINE = "PRISTINE"
    USED = "USED"
    BROKEN = "BROKEN"

class ItemType(enum.Enum):
    """Enum for item types/categories."""
    WEAPON = "WEAPON"
    ARMOR = "ARMOR"
    CONSUMABLE = "CONSUMABLE"
    MATERIAL = "MATERIAL"
    QUEST = "QUEST"
    CURRENCY = "CURRENCY"
    MISC = "MISC"