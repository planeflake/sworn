from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from app.game_state.entities.action.character_action_pydantic import (
    CharacterActionPydantic, ActionStatus, ActionType
)
from app.game_state.repositories.action_repository import ActionRepository

class ActionManager:
    """Handles business logic for character actions - follows your manager pattern."""
    
    def __init__(self, action_repository: ActionRepository):
        self.action_repository = action_repository
    
    @staticmethod
    def create_action(
        name: str,
        character_id: UUID,
        action_type: ActionType,
        location_id: UUID,
        duration: int,
        target_id: Optional[UUID] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> CharacterActionPydantic:
        """Create a new action entity - follows your static create pattern."""
        return CharacterActionPydantic(
            name=name,
            character_id=character_id,
            action_type=action_type,
            target_id=target_id,
            location_id=location_id,
            duration=duration,
            parameters=parameters or {}
        )
    
    @staticmethod
    def update_action_progress(
        action: CharacterActionPydantic, 
        progress: float, 
        status: Optional[ActionStatus] = None
    ) -> CharacterActionPydantic:
        """Update action progress - follows your static update pattern."""
        update_data = {
            'progress': progress,
            'updated_at': datetime.now()
        }
        
        if status:
            update_data['status'] = status
            
        if progress >= 1.0 and not status:
            update_data['status'] = ActionStatus.COMPLETED
            update_data['end_time'] = datetime.now()
            
        # Use base manager update if available, or manual update
        for key, value in update_data.items():
            setattr(action, key, value)
            
        return action
    
    def estimate_action_duration(
        self,
        character_id: UUID,
        action_type: ActionType,
        parameters: Dict[str, Any]
    ) -> int:
        """
        Calculate how long an action should take based on character stats/skills.
        Returns duration in seconds.
        """
        # Base durations by action type
        base_durations = {
            ActionType.GATHER: 300,  # 5 minutes
            ActionType.BUILD: 1800,  # 30 minutes  
            ActionType.CRAFT: 600,   # 10 minutes
            ActionType.TRADE: 60,    # 1 minute
            ActionType.MOVE: 120,    # 2 minutes
            ActionType.REST: 480     # 8 minutes
        }
        
        base_duration = base_durations.get(action_type, 300)
        
        # TODO: Apply character skill modifiers
        # skill_modifier = self.get_character_skill_modifier(character_id, action_type)
        # duration = base_duration * skill_modifier
        
        return base_duration