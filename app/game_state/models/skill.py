from dataclasses import dataclass

@dataclass
class Skill:
    def __init__(self, name: str, level: int):
        self.name = name
        self.level = level