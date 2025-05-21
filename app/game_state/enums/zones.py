from enum import Enum, unique

@unique
class ZonalStateEnum(Enum):
    PEACEFUL = "peaceful"
    HARMONIOUS = "harmonious"
    CHAOTIC = "chaotic"
    DESTROYED = "destroyed"
    UNDEFINED = "undefined"
    def __str__(self):
        return self.value