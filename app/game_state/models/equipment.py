from dataclasses import dataclass

@dataclass
class Equipment:
    def __init__(self, name: str, level: int):
        self.name = name
        self.level = level