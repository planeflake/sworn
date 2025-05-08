# app/game_state/enums/race.py

import enum

class Race(enum.Enum):
    # Fantasy
    HUMAN      = "human"
    ELF        = "elf"
    ORC        = "orc"
    DWARF      = "dwarf"
    GNOME      = "gnome"
    # Post-apoc
    MUTANT     = "mutant"
    RAIDER     = "raider"
    SCAVENGER  = "scavenger"
    # Sci-fi
    CYBORG     = "cyborg"
    ANDROID    = "android"
    ALIEN       = "alien"
