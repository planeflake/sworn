# app/game_state/actions/base/action_executor.py

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.ai.base.action_interface import PossibleAction
from app.game_state.ai.base.game_context import GameContext
from .action_types import ActionExecutionResult

logger = logging.getLogger(__name__)


class ActionExecutor(ABC):
    """
    Base class for executing actions on game entities.
    Handles the common patterns of action execution while allowing
    entity-specific implementations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logger
    
    @abstractmethod
    async def execute_action(
        self, 
        action: PossibleAction, 
        context: GameContext
    ) -> ActionExecutionResult:
        """
        Execute a specific action for an entity.
        
        Args:
            action: The action to execute
            context: Current game state context
            
        Returns:
            Result of the action execution
        """
        pass
    
    async def validate_action_execution(
        self, 
        action: PossibleAction, 
        context: GameContext
    ) -> tuple[bool, list[str]]:
        """
        Validate that an action can be executed right now.
        
        Args:
            action: The action to validate
            context: Current game state context
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        # Check basic validation
        if not action.is_valid:
            errors.extend(action.validation_errors)
        
        # Check prerequisites
        prerequisites_met = await self._check_prerequisites(action, context)
        if not prerequisites_met:
            errors.append("Prerequisites not met")
        
        # Check resource costs
        resources_available = await self._check_resource_availability(action, context)
        if not resources_available:
            errors.append("Insufficient resources")
        
        # Entity-specific validation
        entity_validation = await self._validate_entity_specific(action, context)
        if not entity_validation[0]:
            errors.extend(entity_validation[1])
        
        return len(errors) == 0, errors
    
    async def _check_prerequisites(self, action: PossibleAction, context: GameContext) -> bool:
        """Check if action prerequisites are met."""
        # Default implementation - override in subclasses
        return True
    
    async def _check_resource_availability(self, action: PossibleAction, context: GameContext) -> bool:
        """Check if required resources are available."""
        # Default implementation - override in subclasses
        return True
    
    async def _validate_entity_specific(
        self, 
        action: PossibleAction, 
        context: GameContext
    ) -> tuple[bool, list[str]]:
        """Perform entity-specific validation."""
        # Default implementation - override in subclasses
        return True, []
    
    async def _consume_resources(
        self, 
        action: PossibleAction, 
        context: GameContext
    ) -> Dict[str, int]:
        """
        Consume resources required for the action.
        
        Returns:
            Dictionary of actually consumed resources
        """
        # Default implementation - override in subclasses
        return action.costs.copy()
    
    async def _apply_action_effects(
        self, 
        action: PossibleAction, 
        context: GameContext
    ) -> Dict[str, Any]:
        """
        Apply the effects of the action to the game world.
        
        Returns:
            Dictionary of actual outcomes
        """
        # Default implementation - override in subclasses
        return action.estimated_outcomes.copy()
    
    async def _calculate_efficiency(
        self, 
        action: PossibleAction, 
        context: GameContext,
        actual_outcomes: Dict[str, Any]
    ) -> float:
        """Calculate the efficiency of the action execution."""
        # Default implementation - can be overridden
        return 1.0
    
    async def _calculate_quality(
        self, 
        action: PossibleAction, 
        context: GameContext,
        actual_outcomes: Dict[str, Any]
    ) -> float:
        """Calculate the quality of the action results."""
        # Default implementation - can be overridden
        return 1.0
    
    async def _get_triggered_actions(
        self, 
        action: PossibleAction, 
        context: GameContext,
        outcomes: Dict[str, Any]
    ) -> list[str]:
        """Get list of actions triggered by this action."""
        # Default implementation - override in subclasses
        return []
    
    def _create_execution_result(
        self,
        action: PossibleAction,
        success: bool,
        started_at: datetime,
        completed_at: Optional[datetime] = None,
        outcomes: Optional[Dict[str, Any]] = None,
        resources_consumed: Optional[Dict[str, int]] = None,
        error_details: Optional[str] = None,
        **kwargs
    ) -> ActionExecutionResult:
        """Helper method to create standardized execution results."""
        
        duration = None
        if started_at and completed_at:
            duration = (completed_at - started_at).total_seconds()
        
        return ActionExecutionResult(
            success=success,
            action_id=action.action_id,
            entity_id=action.entity_id,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration,
            outcomes=outcomes or {},
            resources_consumed=resources_consumed or {},
            error_details=error_details,
            **kwargs
        )
    
    async def execute_action_safely(
        self, 
        action: PossibleAction, 
        context: GameContext
    ) -> ActionExecutionResult:
        """
        Execute an action with comprehensive error handling and logging.
        
        Args:
            action: The action to execute
            context: Current game state context
            
        Returns:
            Result of the action execution
        """
        started_at = datetime.utcnow()
        
        try:
            # Log action start
            self.logger.info(
                f"Starting action {action.action_id} for entity {action.entity_id} "
                f"(type: {action.action_type})"
            )
            
            # Validate action can be executed
            is_valid, errors = await self.validate_action_execution(action, context)
            if not is_valid:
                error_message = f"Action validation failed: {', '.join(errors)}"
                self.logger.warning(error_message)
                return self._create_execution_result(
                    action=action,
                    success=False,
                    started_at=started_at,
                    error_details=error_message
                )
            
            # Execute the action
            result = await self.execute_action(action, context)
            
            # Log completion
            if result.success:
                self.logger.info(
                    f"Successfully completed action {action.action_id} for entity {action.entity_id}"
                )
            else:
                self.logger.warning(
                    f"Action {action.action_id} failed: {result.error_details}"
                )
            
            return result
            
        except Exception as e:
            # Handle unexpected errors
            error_message = f"Unexpected error executing action {action.action_id}: {str(e)}"
            self.logger.error(error_message, exc_info=True)
            
            return self._create_execution_result(
                action=action,
                success=False,
                started_at=started_at,
                completed_at=datetime.utcnow(),
                error_details=error_message
            )