import enum

class CharacterTypeEnum(enum.Enum):
    PLAYER = "PLAYER"
    NPC = "NPC"

class CharacterStatusEnum(enum.Enum):
    ALIVE = "ALIVE"
    DEAD = "DEAD"
    INACTIVE = "INACTIVE"

class CharacterTraitEnum(enum.Enum):
    DEFENSIVE = "DEFENSIVE"
    AGGRESSIVE = "AGGRESSIVE"
    SUPPORTIVE = "SUPPORTIVE"
    STRATEGIC = "STRATEGIC"
    ECONOMICAL = "ECONOMICAL"
    EXPANSIVE = "EXPANSIVE"
    CULTURAL = "CULTURAL"
    SPIRITUAL = "SPIRITUAL"

