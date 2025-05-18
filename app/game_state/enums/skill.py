import enum

class SkillStatus(enum.Enum):
    LOCKED = "LOCKED"
    AVAILABLE = "AVAILABLE"
    LEARNING = "LEARNING"
    MASTERED = "MASTERED"