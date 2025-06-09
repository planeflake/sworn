# app/game_state/actions/base/action_types.py

from enum import Enum
from typing import Dict, Any, Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime


class SettlementActionType(Enum):
    """Categories of actions a settlement can perform."""
    
    # Construction & Development
    BUILD_STRUCTURE = "build_structure"
    UPGRADE_BUILDING = "upgrade_building"
    DEMOLISH_BUILDING = "demolish_building"
    EXPAND_TERRITORY = "expand_territory"

    
    # Resource Management
    GATHER_RESOURCES = "gather_resources"
    STOCKPILE_RESOURCES = "stockpile_resources"
    TRADE_RESOURCES = "trade_resources"
    SELL_RESOURCES = "sell_resources"
    
    # Population & Labor
    RECRUIT_WORKERS = "recruit_workers"
    ASSIGN_WORKERS = "assign_workers"
    TRAIN_SPECIALISTS = "train_specialists"
    RECRUIT_SPECIALISTS = "recruit_specialists"
    RELOCATE_POPULATION = "relocate_population"
    
    # Military & Defense
    BUILD_DEFENSES = "build_defenses"
    RECRUIT_GUARDS = "recruit_guards"
    FORTIFY_SETTLEMENT = "fortify_settlement"
    PATROL_BORDERS = "patrol_borders"
    
    # Diplomacy & Trade
    ESTABLISH_TRADE_ROUTE = "establish_trade_route"
    NEGOTIATE_ALLIANCE = "negotiate_alliance"
    SEND_DIPLOMAT = "send_diplomat"
    HOST_DELEGATION = "host_delegation"
    
    # Research & Technology
    RESEARCH_TECHNOLOGY = "research_technology"
    ADOPT_INNOVATION = "adopt_innovation"
    SHARE_KNOWLEDGE = "share_knowledge"
    
    # Exploration & Expansion
    SEND_EXPEDITION = "send_expedition"
    ESTABLISH_OUTPOST = "establish_outpost"
    SURVEY_TERRITORY = "survey_territory"
    
    # Special Actions
    HOLD_FESTIVAL = "hold_festival"
    EMERGENCY_RESPONSE = "emergency_response"
    DISASTER_RECOVERY = "disaster_recovery"


class CharacterActionType(Enum):
    """Categories of actions a character can perform."""
    
    # Movement & Exploration
    TRAVEL_TO_LOCATION = "travel_to_location"
    EXPLORE_AREA = "explore_area"
    SCOUT_TERRITORY = "scout_territory"
    
    # Skill Development
    PRACTICE_SKILL = "practice_skill"
    LEARN_FROM_TEACHER = "learn_from_teacher"
    TEACH_OTHERS = "teach_others"
    
    # Resource Activities
    GATHER_RESOURCES = "gather_resources"
    CRAFT_ITEMS = "craft_items"
    MINE_RESOURCES = "mine_resources"
    HUNT_WILDLIFE = "hunt_wildlife"
    
    # Social Actions
    SOCIALIZE = "socialize"
    NEGOTIATE = "negotiate"
    LEAD_GROUP = "lead_group"
    INSPIRE_OTHERS = "inspire_others"
    
    # Combat & Defense
    PATROL_AREA = "patrol_area"
    GUARD_LOCATION = "guard_location"
    FIGHT_THREATS = "fight_threats"
    TRAIN_COMBAT = "train_combat"
    
    # Research & Knowledge
    RESEARCH_TOPIC = "research_topic"
    STUDY_ARTIFACT = "study_artifact"
    DOCUMENT_KNOWLEDGE = "document_knowledge"
    
    # Rest & Recovery
    REST = "rest"
    RECUPERATE = "recuperate"
    MEDITATE = "meditate"


class BuildingActionType(Enum):
    """Categories of actions a building can perform."""
    
    # Production
    PRODUCE_RESOURCES = "produce_resources"
    PROCESS_MATERIALS = "process_materials"
    MANUFACTURE_GOODS = "manufacture_goods"
    
    # Maintenance
    PERFORM_MAINTENANCE = "perform_maintenance"
    REPAIR_DAMAGE = "repair_damage"
    UPGRADE_EFFICIENCY = "upgrade_efficiency"
    
    # Storage & Distribution
    STORE_RESOURCES = "store_resources"
    DISTRIBUTE_GOODS = "distribute_goods"
    ORGANIZE_INVENTORY = "organize_inventory"
    
    # Services
    PROVIDE_SERVICE = "provide_service"
    TRAIN_WORKERS = "train_workers"
    RESEARCH_IMPROVEMENTS = "research_improvements"
    
    # Automation
    AUTOMATE_PROCESS = "automate_process"
    OPTIMIZE_PRODUCTION = "optimize_production"
    SCHEDULE_OPERATIONS = "schedule_operations"


class ActionExecutionResult(BaseModel):
    """Result of executing an action."""
    
    # Execution Status
    success: bool = Field(..., description="Whether the action was executed successfully")
    action_id: str = Field(..., description="ID of the action that was executed")
    entity_id: UUID = Field(..., description="ID of the entity that performed the action")
    
    # Timing
    started_at: datetime = Field(..., description="When the action started")
    completed_at: Optional[datetime] = Field(None, description="When the action completed")
    duration_seconds: Optional[float] = Field(None, description="How long the action took")
    
    # Results
    outcomes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Actual outcomes of the action"
    )
    resources_consumed: Dict[str, int] = Field(
        default_factory=dict,
        description="Resources that were actually consumed"
    )
    resources_produced: Dict[str, int] = Field(
        default_factory=dict,
        description="Resources that were produced"
    )
    
    # Status Information
    status_message: str = Field("", description="Human-readable status message")
    error_details: Optional[str] = Field(None, description="Error details if execution failed")
    warnings: List[str] = Field(
        default_factory=list,
        description="Non-fatal warnings during execution"
    )
    
    # Follow-up Actions
    triggered_actions: List[str] = Field(
        default_factory=list,
        description="Action IDs that were triggered as a result of this action"
    )
    prerequisites_unlocked: List[str] = Field(
        default_factory=list,
        description="Prerequisites that were unlocked by this action"
    )
    
    # Analytics Data
    efficiency: Optional[float] = Field(
        None,
        ge=0.0,
        le=2.0,
        description="Efficiency of the action execution (1.0 = normal, >1.0 = better than expected)"
    )
    quality: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Quality of the action results (0.0 = poor, 1.0 = excellent)"
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional execution metadata"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "action_id": "build_lumber_mill_001",
                "entity_id": "123e4567-e89b-12d3-a456-426614174000",
                "started_at": "2023-10-28T14:30:00Z",
                "completed_at": "2023-10-29T14:30:00Z",
                "duration_seconds": 86400,
                "outcomes": {
                    "building_created": "lumber_mill_001",
                    "wood_production_increased": 5,
                    "employment_created": 2
                },
                "resources_consumed": {
                    "wood": 50,
                    "stone": 25
                },
                "resources_produced": {},
                "status_message": "Lumber mill constructed successfully",
                "efficiency": 1.1,
                "quality": 0.9,
                "triggered_actions": ["assign_workers_to_lumber_mill"],
                "metadata": {
                    "builder_skill_level": 3,
                    "weather_bonus": 0.1
                }
            }
        }