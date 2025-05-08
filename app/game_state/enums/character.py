import enum

class CharacterTypeEnum(enum.Enum):
    PLAYER = "PLAYER"
    NPC = "NPC"

class CharacterStatusEnum(enum.Enum):
    ALIVE = "ALIVE"
    DEAD = "DEAD"
    INACTIVE = "INACTIVE"