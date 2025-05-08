from dataclasses import dataclass

@dataclass
class Stat:
    def __init__(self, name: str, level: int):
        self.name = name
        self.level = level