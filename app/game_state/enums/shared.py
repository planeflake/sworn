import enum

class RarityEnum(enum.Enum):
    """Enum for item rarity levels."""
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    EPIC = "Epic"
    LEGENDARY = "Legendary"
    MYTHICAL = "Mythical"
    HEAVENLY = "Heavenly"

class StatusEnum(enum.Enum):
    """Enum for item status."""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"
    ARCHIVED = "Archived"