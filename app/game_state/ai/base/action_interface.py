# app/game_state/ai/base/action_interface.py

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from uuid import UUID

from app.game_state.enums.character import CharacterTraitEnum
from app.game_state.ai.base.game_context import GameContext

class PossibleAction(BaseModel):
    """
    Represents a possible action that an entity can take.
    Used by MCTS and other AI systems to evaluate and execute decisions.
    """
    
    # Action Identity
    entity_id: UUID = Field(..., description="ID of the entity that can perform this action")
    entity_type: str = Field(..., description="Type of entity (settlement, character, building, etc.)")
    action_type: str = Field(..., description="Category of action (build, trade, explore, etc.)")
    action_id: str = Field(..., description="Unique identifier for this specific action")
    
    # Action Description
    name: str = Field(..., description="Human-readable name of the action")
    description: str = Field(..., description="Detailed description of what this action does")
    
    # Action Requirements
    prerequisites: Dict[str, Any] = Field(
        default_factory=dict,
        description="Requirements that must be met to perform this action"
    )
    costs: Dict[str, int] = Field(
        default_factory=dict,
        description="Resource costs (resource_id -> amount)"
    )
    
    # Action Outcomes
    estimated_outcomes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Expected results of performing this action"
    )
    duration: Optional[int] = Field(
        None,
        description="Time in game ticks/hours this action takes to complete"
    )
    
    # AI Scoring Data
    base_priority: float = Field(
        1.0,
        ge=0.0,
        description="Base priority score for this action"
    )
    trait_modifiers: Dict[CharacterTraitEnum, float] = Field(
        default_factory=dict,
        description="How character traits modify the appeal of this action"
    )
    
    # Context Data
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context-specific data for this action"
    )
    
    # Validation
    is_valid: bool = Field(
        True,
        description="Whether this action can currently be performed"
    )
    validation_errors: List[str] = Field(
        default_factory=list,
        description="Reasons why this action cannot be performed"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "entity_id": "123e4567-e89b-12d3-a456-426614174000",
                "entity_type": "settlement",
                "action_type": "build_structure",
                "action_id": "build_lumber_mill_001",
                "name": "Build Lumber Mill",
                "description": "Construct a lumber mill to increase wood production",
                "prerequisites": {
                    "technology_required": "basic_construction",
                    "space_available": True,
                    "population_minimum": 10
                },
                "costs": {
                    "wood": 50,
                    "stone": 25,
                    "population": 2
                },
                "estimated_outcomes": {
                    "wood_production_per_hour": 5,
                    "employment_slots": 2,
                    "settlement_growth": 0.1
                },
                "duration": 24,
                "base_priority": 1.2,
                "trait_modifiers": {
                    "industrious": 1.3,
                    "lazy": 0.7
                },
                "metadata": {
                    "building_blueprint_id": "lumber_mill_blueprint_001"
                },
                "is_valid": True,
                "validation_errors": []
            }
        }


class ActionCapable(ABC):
    """
    Mixin interface for entities that can perform actions.
    Entities implementing this can participate in AI decision-making systems.
    """
    
    @abstractmethod
    async def get_possible_actions(self, context: 'GameContext') -> List[PossibleAction]:
        """
        Discover all actions this entity can currently perform.
        
        Args:
            context: Current game state context for action discovery
            
        Returns:
            List of possible actions with their costs, requirements, and expected outcomes
        """
        pass
    
    async def get_actions_by_type(self, action_type: str, context: 'GameContext') -> List[PossibleAction]:
        """
        Get all possible actions of a specific type.
        
        Args:
            action_type: Type of actions to filter for
            context: Current game state context
            
        Returns:
            Filtered list of possible actions
        """
        all_actions = await self.get_possible_actions(context)
        return [action for action in all_actions if action.action_type == action_type]

    @staticmethod
    async def can_perform_action(action: PossibleAction, context: 'GameContext') -> bool:
        """
        Check if this entity can currently perform a specific action.
        
        Args:
            action: The action to validate
            context: Current game state context
            
        Returns:
            True if the action can be performed, False otherwise
        """
        # Default implementation - can be overridden by entities
        return action.is_valid and len(action.validation_errors) == 0

    @staticmethod
    async def validate_action(action: PossibleAction, context: 'GameContext') -> PossibleAction:
        """
        Validate an action and update its validation status.
        
        Args:
            action: The action to validate
            context: Current game state context
            
        Returns:
            Updated action with validation results
        """
        # This method should be implemented by specific entities
        # Default implementation just returns the action as-is
        return action