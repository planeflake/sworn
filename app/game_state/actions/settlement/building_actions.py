# app/game_state/actions/settlement/building_actions.py

from uuid import UUID, uuid4
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.game_state.ai.base.action_interface import PossibleAction
from app.game_state.ai.base.game_context import GameContext
from app.game_state.actions.base.action_types import SettlementActionType
from app.game_state.enums.character import CharacterTraitEnum


class ConstructBuildingAction:
    """
    Generic building construction action that works with any building blueprint.
    This creates actions dynamically based on building blueprint data.
    """
    
    @staticmethod
    def create_action(
        settlement_id: UUID, 
        building_blueprint_id: UUID,
        context: GameContext
    ) -> PossibleAction:
        """
        Create a PossibleAction for constructing any building from a blueprint.
        
        Args:
            settlement_id: ID of the settlement that would perform this action
            building_blueprint_id: ID of the building blueprint to construct
            context: Current game context for validation and cost calculation
            
        Returns:
            PossibleAction representing the building construction
        """
        
        # Get building blueprint data (in real implementation, fetch from database)
        blueprint = ConstructBuildingAction._get_blueprint_data(building_blueprint_id, context)
        if not blueprint:
            raise ValueError(f"Building blueprint {building_blueprint_id} not found")
        
        # Calculate dynamic costs based on context and blueprint
        adjusted_costs = ConstructBuildingAction._calculate_adjusted_costs(blueprint["base_costs"], context)
        
        # Calculate expected outcomes based on blueprint and context
        expected_outcomes = ConstructBuildingAction._calculate_expected_outcomes(blueprint, context)
        
        # Create the action
        action = PossibleAction(
            entity_id=settlement_id,
            entity_type="settlement",
            action_type=SettlementActionType.BUILD_STRUCTURE.value,
            action_id=f"construct_{blueprint['building_type']}_{settlement_id}_{context.game_tick}",
            name=f"Build {blueprint['name']}",
            description=blueprint["description"],
            
            prerequisites=blueprint.get("prerequisites", {}),
            costs=adjusted_costs,
            estimated_outcomes=expected_outcomes,
            
            duration=blueprint.get("construction_time", 24),
            base_priority=blueprint.get("base_priority", 1.0),
            trait_modifiers=blueprint.get("trait_modifiers", {}),
            
            metadata={
                "building_blueprint_id": str(building_blueprint_id),
                "building_type": blueprint["building_type"],
                "building_category": blueprint.get("category", "unknown"),
                **blueprint.get("metadata", {})
            }
        )
        
        # Validate the action based on current context
        action = ConstructBuildingAction._validate_action(action, blueprint, context)
        
        return action
    
    @staticmethod
    def _get_blueprint_data(blueprint_id: UUID, context: GameContext) -> Optional[Dict[str, Any]]:
        """
        Get building blueprint data. In real implementation, this would query the database.
        For now, return example data based on blueprint_id.
        """
        
        # Check if blueprint data is cached in context
        cached_blueprint = context.get_cached_entity("building_blueprint", blueprint_id)
        if cached_blueprint:
            return cached_blueprint
        
        # Simulate different building types (in real implementation, fetch from database)
        blueprint_examples = {
            "lumber_mill": {
                "name": "Lumber Mill",
                "building_type": "lumber_mill",
                "category": "production",
                "description": "Processes wood resources and provides employment",
                "base_costs": {
                    "wood": 50,
                    "stone": 25,
                    "population": 2
                },
                "prerequisites": {
                    "technology_required": ["basic_construction"],
                    "population_minimum": 10,
                    "resource_requirements": ["nearby_forest"],
                    "unique_building": True  # Only one per settlement
                },
                "base_outcomes": {
                    "wood_production_per_hour": 5,
                    "employment_slots": 2,
                    "settlement_growth": 0.1,
                    "building_maintenance_cost": 1
                },
                "construction_time": 24,
                "base_priority": 1.2,
                "trait_modifiers": {
                    CharacterTraitEnum.INDUSTRIOUS: 1.4,
                    CharacterTraitEnum.LAZY: 0.6,
                    CharacterTraitEnum.ENVIRONMENTALIST: 0.8,
                    CharacterTraitEnum.PRAGMATIC: 1.2
                },
                "metadata": {
                    "can_upgrade": True,
                    "pollution_factor": 0.05,
                    "seasonal_preference": "spring"
                }
            },
            "blacksmith": {
                "name": "Blacksmith",
                "building_type": "blacksmith", 
                "category": "crafting",
                "description": "Crafts tools and weapons from metal resources",
                "base_costs": {
                    "wood": 30,
                    "stone": 40,
                    "iron": 20,
                    "population": 1
                },
                "prerequisites": {
                    "technology_required": ["metalworking"],
                    "population_minimum": 15,
                    "resource_requirements": ["iron_source"]
                },
                "base_outcomes": {
                    "tool_production_per_hour": 2,
                    "weapon_production_per_hour": 1,
                    "employment_slots": 1,
                    "settlement_growth": 0.15
                },
                "construction_time": 36,
                "base_priority": 1.3,
                "trait_modifiers": {
                    CharacterTraitEnum.INDUSTRIOUS: 1.3,
                    CharacterTraitEnum.MILITARISTIC: 1.5,
                    CharacterTraitEnum.PEACEFUL: 0.7
                }
            },
            "farm": {
                "name": "Farm",
                "building_type": "farm",
                "category": "food_production", 
                "description": "Produces food to sustain the settlement population",
                "base_costs": {
                    "wood": 20,
                    "stone": 10,
                    "population": 3
                },
                "prerequisites": {
                    "technology_required": ["agriculture"],
                    "population_minimum": 5,
                    "resource_requirements": ["fertile_land"]
                },
                "base_outcomes": {
                    "food_production_per_hour": 8,
                    "employment_slots": 3,
                    "settlement_growth": 0.2
                },
                "construction_time": 18,
                "base_priority": 1.5,  # High priority - everyone needs food
                "trait_modifiers": {
                    CharacterTraitEnum.NURTURING: 1.4,
                    CharacterTraitEnum.PRAGMATIC: 1.3,
                    CharacterTraitEnum.LAZY: 0.8
                }
            }
        }
        
        # Try to match blueprint_id to a known type (simplified lookup)
        # In real implementation, you'd query your building_blueprint table
        for building_type, data in blueprint_examples.items():
            if building_type in str(blueprint_id) or context.metadata.get("requested_building_type") == building_type:
                context.cache_entity("building_blueprint", blueprint_id, data)
                return data
        
        return None
    
    @staticmethod
    def _calculate_adjusted_costs(base_costs: Dict[str, int], context: GameContext) -> Dict[str, int]:
        """Calculate costs adjusted for current game context."""
        adjusted_costs = {}
        
        for resource, base_cost in base_costs.items():
            if resource == "population":
                # Population costs don't scale with scarcity
                adjusted_costs[resource] = base_cost
            else:
                # Adjust resource costs based on scarcity and market prices
                scarcity_factor = context.get_resource_scarcity(resource, 0.0)
                price_factor = context.get_resource_price(resource, 1.0)
                
                # Cost increases with scarcity and market price
                adjustment = 1.0 + (scarcity_factor * 0.5) + ((price_factor - 1.0) * 0.3)
                adjusted_costs[resource] = int(base_cost * adjustment)
        
        # Add time cost
        base_time = base_costs.get("time_hours", 24)
        season = context.metadata.get("current_season", "spring")
        
        # Winter construction takes longer
        time_multiplier = 1.2 if season == "winter" else 1.0
        adjusted_costs["time_hours"] = int(base_time * time_multiplier)
        
        return adjusted_costs
    
    @staticmethod
    def _calculate_expected_outcomes(blueprint: Dict[str, Any], context: GameContext) -> Dict[str, Any]:
        """Calculate expected outcomes based on blueprint and context."""
        base_outcomes = blueprint.get("base_outcomes", {})
        adjusted_outcomes = base_outcomes.copy()
        
        # Apply technology bonuses
        for tech in context.available_technologies:
            if "improved" in tech and blueprint["building_type"] in tech:
                # Improved technology increases efficiency
                for outcome_key, outcome_value in adjusted_outcomes.items():
                    if "production" in outcome_key and isinstance(outcome_value, (int, float)):
                        adjusted_outcomes[outcome_key] = outcome_value * 1.2
        
        # Apply seasonal effects
        season = context.metadata.get("current_season", "spring")
        if blueprint["building_type"] == "farm":
            # Farms are more productive in spring/summer
            seasonal_bonus = {"spring": 1.2, "summer": 1.1, "autumn": 1.0, "winter": 0.8}
            food_production = adjusted_outcomes.get("food_production_per_hour", 0)
            adjusted_outcomes["food_production_per_hour"] = int(food_production * seasonal_bonus.get(season, 1.0))
        
        return adjusted_outcomes
    
    @staticmethod
    def _validate_action(action: PossibleAction, blueprint: Dict[str, Any], context: GameContext) -> PossibleAction:
        """Validate whether this construction action can be performed."""
        errors = []
        
        # Check technology prerequisites
        required_techs = blueprint.get("prerequisites", {}).get("technology_required", [])
        for tech in required_techs:
            if not context.is_technology_available(tech):
                errors.append(f"Required technology '{tech}' not available")
        
        # Check population requirements
        min_population = blueprint.get("prerequisites", {}).get("population_minimum", 0)
        current_population = context.metadata.get("settlement_population", 0)
        if current_population < min_population:
            errors.append(f"Insufficient population (need {min_population}, have {current_population})")
        
        # Check resource availability
        settlement_resources = context.metadata.get("settlement_resources", {})
        for resource, cost in action.costs.items():
            if resource != "time_hours" and resource != "population":
                available = settlement_resources.get(resource, 0)
                if available < cost:
                    errors.append(f"Insufficient {resource} (need {cost}, have {available})")
        
        # Check unique building constraint
        if blueprint.get("prerequisites", {}).get("unique_building", False):
            existing_buildings = context.metadata.get("settlement_buildings", [])
            if blueprint["building_type"] in existing_buildings:
                errors.append(f"{blueprint['name']} already exists in this settlement")
        
        # Check resource requirements (nearby resources)
        required_resources = blueprint.get("prerequisites", {}).get("resource_requirements", [])
        nearby_resources = context.metadata.get("nearby_resource_types", [])
        for req_resource in required_resources:
            if req_resource not in nearby_resources:
                errors.append(f"Required resource '{req_resource}' not available nearby")
        
        # Update action validation
        action.is_valid = len(errors) == 0
        action.validation_errors = errors
        
        return action
    
    @staticmethod
    def get_all_available_constructions(settlement_id: UUID, context: GameContext) -> List[PossibleAction]:
        """
        Get all building construction actions available to a settlement.
        This is what would be called by the settlement's get_possible_actions() method.
        """
        available_actions = []
        
        # Get all building blueprints available to this settlement
        # In real implementation, query database for blueprints
        available_blueprints = ConstructBuildingAction._get_available_blueprints(context)
        
        for blueprint_id in available_blueprints:
            try:
                action = ConstructBuildingAction.create_action(settlement_id, blueprint_id, context)
                available_actions.append(action)
            except Exception as e:
                # Log error but continue with other blueprints
                print(f"Error creating action for blueprint {blueprint_id}: {e}")
        
        return available_actions
    
    @staticmethod
    def _get_available_blueprints(context: GameContext) -> List[UUID]:
        """Get list of building blueprint IDs available in current context."""
        # In real implementation, this would query your building_blueprint table
        # filtered by available technologies, settlement tier, etc.
        
        # For example purposes, return some mock blueprint IDs
        mock_blueprints = [
            UUID("11111111-1111-1111-1111-111111111111"),  # lumber_mill
            UUID("22222222-2222-2222-2222-222222222222"),  # blacksmith  
            UUID("33333333-3333-3333-3333-333333333333"),  # farm
        ]
        
        return mock_blueprints