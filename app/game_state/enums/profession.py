import enum

class ProfessionCategory(enum.Enum):
    """Categories/types of professions."""
    CRAFTING = "CRAFTING"
    GATHERING = "GATHERING"
    COMBAT = "COMBAT"
    SOCIAL = "SOCIAL"
    SERVICE = "SERVICE"
    MANAGEMENT = "MANAGEMENT"

class ProfessionUnlockType(enum.Enum):
    """Methods for unlocking professions."""
    NPC_TEACHER = "npc_teacher"
    ITEM_MANUAL = "item_manual"
    WORLD_OBJECT = "world_object"
    QUEST_COMPLETION = "quest_completion"
    SKILL_THRESHOLD = "skill_threshold"