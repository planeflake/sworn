# app/game_state/ai/action_selector.py

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.ai.base.action_interface import ActionCapable, PossibleAction
from app.game_state.ai.base.game_context import GameContext
from app.game_state.actions.base.action_types import ActionExecutionResult

logger = logging.getLogger(__name__)


class ActionSelector:
    """
    Generic action selector that works with any ActionCapable entity.
    Handles action discovery, evaluation, and selection for AI decision-making.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logger
    
    async def get_possible_actions(
        self, 
        entity: ActionCapable, 
        context: GameContext
    ) -> List[PossibleAction]:
        """
        Get all possible actions for an entity.
        
        Args:
            entity: Any entity that implements ActionCapable
            context: Current game context
            
        Returns:
            List of possible actions the entity can perform
        """
        try:
            self.logger.debug(f"Getting possible actions for entity {getattr(entity, 'entity_id', 'unknown')}")
            
            # Get actions from the entity
            actions = await entity.get_possible_actions(context)
            
            # Apply universal trait processing to each action
            processed_actions = []
            for action in actions:
                processed_action = await self._apply_trait_modifiers(entity, action, context)
                processed_actions.append(processed_action)
            
            # Filter out invalid actions
            valid_actions = [action for action in processed_actions if action.is_valid]
            
            self.logger.info(
                f"Found {len(actions)} total actions, {len(valid_actions)} valid actions "
                f"for entity {getattr(entity, 'entity_id', 'unknown')}"
            )
            
            return valid_actions
            
        except Exception as e:
            self.logger.error(f"Error getting possible actions: {e}", exc_info=True)
            return []
    
    async def select_best_action(
        self, 
        entity: ActionCapable, 
        context: GameContext,
        strategy: str = "trait_based"
    ) -> Optional[PossibleAction]:
        """
        Select the best action for an entity to perform.
        
        Args:
            entity: The entity making the decision
            context: Current game context
            strategy: Selection strategy ("trait_based", "random", "highest_priority")
            
        Returns:
            The best action to perform, or None if no valid actions
        """
        try:
            # Get all possible actions
            possible_actions = await self.get_possible_actions(entity, context)
            
            if not possible_actions:
                self.logger.info(f"No valid actions available for entity {getattr(entity, 'entity_id', 'unknown')}")
                return None
            
            # Select action based on strategy
            if strategy == "trait_based":
                best_action = await self._select_trait_based(entity, possible_actions, context)
            elif strategy == "highest_priority":
                best_action = await self._select_highest_priority(possible_actions)
            elif strategy == "random":
                best_action = await self._select_random(possible_actions)
            else:
                raise ValueError(f"Unknown selection strategy: {strategy}")
            
            self.logger.info(
                f"Selected action '{best_action.name}' with priority {best_action.base_priority:.2f} "
                f"for entity {getattr(entity, 'entity_id', 'unknown')}"
            )
            
            return best_action
            
        except Exception as e:
            self.logger.error(f"Error selecting best action: {e}", exc_info=True)
            return None
    
    async def evaluate_action_appeal(
        self, 
        entity: ActionCapable, 
        action: PossibleAction, 
        context: GameContext
    ) -> float:
        """
        Calculate how appealing an action is to a specific entity.
        
        Args:
            entity: The entity evaluating the action
            action: The action to evaluate
            context: Current game context
            
        Returns:
            Appeal score (higher = more appealing)
        """
        try:
            # Start with base priority
            appeal = action.base_priority
            
            # Apply trait modifiers using the entity's all_traits property
            if hasattr(entity, 'all_traits'):
                for trait in entity.all_traits:
                    # Convert trait to string if it's an enum
                    trait_key = trait.value if hasattr(trait, 'value') else str(trait)
                    modifier = action.trait_modifiers.get(trait_key, 1.0)
                    appeal *= modifier
            
            # Apply context-based modifiers
            appeal = await self._apply_context_modifiers(appeal, action, context)
            
            return max(0.0, appeal)  # Ensure non-negative
            
        except Exception as e:
            self.logger.error(f"Error evaluating action appeal: {e}")
            return action.base_priority  # Fallback to base priority
    
    async def _apply_trait_modifiers(
        self, 
        entity: ActionCapable, 
        action: PossibleAction, 
        context: GameContext
    ) -> PossibleAction:
        """Apply trait-based modifications to an action."""
        try:
            # Calculate new appeal based on traits
            new_appeal = await self.evaluate_action_appeal(entity, action, context)
            
            # Update action priority
            action.base_priority = new_appeal
            
            # Add trait context to action metadata
            if hasattr(entity, 'all_traits'):
                action.metadata["applied_traits"] = entity.all_traits
                action.metadata["trait_modified_priority"] = new_appeal
            
            return action
            
        except Exception as e:
            self.logger.error(f"Error applying trait modifiers: {e}")
            return action
    
    async def _apply_context_modifiers(
        self, 
        base_appeal: float, 
        action: PossibleAction, 
        context: GameContext
    ) -> float:
        """Apply context-based modifiers to action appeal."""
        appeal = base_appeal
        
        # Resource scarcity modifiers
        for resource, cost in action.costs.items():
            if resource in context.resource_scarcity:
                scarcity = context.resource_scarcity[resource]
                # Higher scarcity makes resource-consuming actions less appealing
                appeal *= (1.0 - scarcity * 0.3)
        
        # Threat level modifiers
        if action.action_type == "build_defenses":
            # Defense actions more appealing when threats are high
            appeal *= (1.0 + context.threat_level)
        elif action.action_type == "build_structure" and context.threat_level > 0.5:
            # Construction less appealing during high threat
            appeal *= 0.8
        
        # Economic condition modifiers
        if "prosperity" in context.economic_conditions:
            prosperity = context.economic_conditions["prosperity"]
            if action.action_type == "trade_resources":
                # Trade more appealing in prosperous times
                appeal *= (1.0 + prosperity * 0.5)
        
        return appeal
    
    async def _select_trait_based(
        self, 
        entity: ActionCapable, 
        actions: List[PossibleAction], 
        context: GameContext
    ) -> PossibleAction:
        """Select action based on trait-modified priorities."""
        # Actions are already trait-modified from get_possible_actions
        return max(actions, key=lambda a: a.base_priority)
    
    async def _select_highest_priority(self, actions: List[PossibleAction]) -> PossibleAction:
        """Select action with highest base priority (ignoring traits)."""
        return max(actions, key=lambda a: a.base_priority)
    
    async def _select_random(self, actions: List[PossibleAction]) -> PossibleAction:
        """Select a random action (weighted by priority)."""
        import random
        
        # Create weighted list
        weights = [max(0.1, action.base_priority) for action in actions]
        
        # Random weighted selection
        return random.choices(actions, weights=weights)[0]
    
    # Future: Add MCTS-based selection
    async def _select_mcts(
        self, 
        entity: ActionCapable, 
        actions: List[PossibleAction], 
        context: GameContext
    ) -> PossibleAction:
        """Select action using Monte Carlo Tree Search (future implementation)."""
        # TODO: Implement MCTS algorithm
        # For now, fall back to trait-based selection
        return await self._select_trait_based(entity, actions, context)