# app/game_state/ai/base/__init__.py

"""
Base interfaces and classes for AI decision-making systems.
"""

from .action_interface import PossibleAction, ActionCapable
from .game_context import GameContext

__all__ = [
    "PossibleAction",
    "ActionCapable", 
    "GameContext"
]