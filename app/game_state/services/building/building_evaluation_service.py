"""
Building Evaluation Service for trait-based building recommendations.
This service evaluates buildings based on leader traits and settlement needs.
"""
import logging
from typing import List, Dict, Tuple, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.repositories.building_blueprint_repository import BuildingBlueprintRepository
from app.game_state.repositories.settlement_repository import SettlementRepository
from app.game_state.repositories.character_repository import CharacterRepository
from app.game_state.entities.building.building_blueprint_pydantic import BuildingBlueprintEntityPydantic
from app.game_state.entities.character.character_pydantic import CharacterEntityPydantic
from app.game_state.entities.geography.settlement_pydantic import SettlementEntityPydantic

class BuildingEvaluationService:
    """
    Service for evaluating buildings based on leader traits and settlement needs.
    Provides methods for scoring and recommending buildings.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the service with database session and repositories.
        
        Args:
            db: SQLAlchemy AsyncSession
        """
        self.db = db
        self.blueprint_repo = BuildingBlueprintRepository(db)
        self.settlement_repo = SettlementRepository(db)
        self.character_repo = CharacterRepository(db)
        self.logger = logging.getLogger(__name__)
        
    async def get_settlement_leader(self, settlement_id: UUID) -> Optional[CharacterEntityPydantic]:
        """
        Get the leader character for a settlement.
        
        Args:
            settlement_id: UUID of the settlement
            
        Returns:
            CharacterEntity of the leader or None if no leader
        """
        settlement = await self.settlement_repo.find_by_id(settlement_id)
        if not settlement or not settlement.leader_id:
            self.logger.warning(f"Settlement {settlement_id} has no leader")
            return None
            
        leader = await self.character_repo.find_by_id(settlement.leader_id)
        if not leader:
            self.logger.warning(f"Leader {settlement.leader_id} not found for settlement {settlement_id}")
            return None
            
        return leader
        
    async def get_leader_traits(self, settlement_id: UUID) -> List[str]:
        """
        Get the trait values for a settlement's leader.
        
        Args:
            settlement_id: UUID of the settlement
            
        Returns:
            List of trait values as strings
        """
        leader = await self.get_settlement_leader(settlement_id)
        if not leader:
            return []
            
        return [trait.value for trait in leader.traits]

    @staticmethod
    async def score_building_for_leader(
        blueprint: BuildingBlueprintEntityPydantic,
        leader_traits: List[str]
    ) -> float:
        """
        Score a building based on how well it matches the leader's traits.
        
        Args:
            blueprint: The BuildingBlueprintEntity to score
            leader_traits: List of trait values for the leader
            
        Returns:
            Float score between 0.0 and 1.0
        """
        if not leader_traits:
            return 0.0
            
        # Calculate trait affinity scores for each trait
        trait_scores = [blueprint.calculate_trait_affinity(trait) for trait in leader_traits]
        
        # Return average score
        if not trait_scores:
            return 0.0
            
        return sum(trait_scores) / len(trait_scores)

    @staticmethod
    async def score_building_for_resources(
        blueprint: BuildingBlueprintEntityPydantic,
        settlement_resources: Dict[str, int]
    ) -> float:
        """
        Score a building based on resource availability.
        
        Args:
            blueprint: The BuildingBlueprintEntity to score
            settlement_resources: Dict of resource IDs to amounts
            
        Returns:
            Float score between 0.0 and 1.0 (1.0 means all resources available)
        """
        # For now, this is a placeholder that always returns 1.0
        # In the future, this would check the blueprint's resource requirements
        # against the settlement's available resources

        if blueprint and settlement_resources:
            pass

        return 1.0

    @staticmethod
    async def score_building_for_settlement_needs(
        blueprint: BuildingBlueprintEntityPydantic,
        settlement: Settlement
    ) -> float:
        """
        Score a building based on the settlement's current needs.
        
        Args:
            blueprint: The BuildingBlueprintEntity to score
            settlement: The Settlement entity
            
        Returns:
            Float score between 0.0 and 1.0
        """
        # This is a placeholder that would be implemented based on 
        # settlement needs analysis

        if blueprint and settlement:
            pass


        return 0.5
        
    async def get_weighted_building_score(
        self,
        blueprint: BuildingBlueprintEntityPydantic,
        leader_traits: List[str],
        settlement_resources: Dict[str, int],
        settlement: Settlement,
        weights: Dict[str, float] = None
    ) -> float:
        """
        Calculate a weighted score for a building considering multiple factors.
        
        Args:
            blueprint: The BuildingBlueprintEntity to score
            leader_traits: List of leader trait values
            settlement_resources: Dict of resource IDs to amounts
            settlement: The Settlement entity
            weights: Dict of factor weights (defaults to equal weighting)
            
        Returns:
            Float score between 0.0 and 1.0
        """
        # Default weights
        if weights is None:
            weights = {
                "trait_affinity": 0.6,  # Leader traits are the primary factor
                "resource_availability": 0.2,
                "settlement_needs": 0.2
            }
            
        # Calculate individual scores
        trait_score = await self.score_building_for_leader(blueprint, leader_traits)
        resource_score = await self.score_building_for_resources(blueprint, settlement_resources)
        needs_score = await self.score_building_for_settlement_needs(blueprint, settlement)
        
        # Calculate weighted score
        weighted_score = (
            trait_score * weights["trait_affinity"] +
            resource_score * weights["resource_availability"] +
            needs_score * weights["settlement_needs"]
        )
        
        return weighted_score
        
    async def get_recommended_buildings(
        self,
        settlement_id: UUID,
        limit: int = 5
    ) -> List[Tuple[BuildingBlueprintEntityPydantic, float]]:
        """
        Get recommended buildings for a settlement ordered by score.
        
        Args:
            settlement_id: UUID of the settlement
            limit: Maximum number of recommendations to return
            
        Returns:
            List of tuples (BuildingBlueprintEntity, score) ordered by score
        """
        # Get settlement data
        settlement = await self.settlement_repo.find_by_id(settlement_id)
        if not settlement:
            self.logger.error(f"Settlement {settlement_id} not found")
            return []
            
        # Get leader traits
        leader_traits = await self.get_leader_traits(settlement_id)
        if not leader_traits:
            self.logger.warning(f"No leader traits found for settlement {settlement_id}")
            # Return empty list or a default recommendation strategy
            return []
            
        # Get settlement resources (placeholder)
        settlement_resources = {}  # This would be replaced with actual resource data
        
        # Get all available building blueprints
        blueprints = await self.blueprint_repo.find_all()
        
        # Score each blueprint
        scored_blueprints = []
        for blueprint in blueprints:
            score = await self.get_weighted_building_score(
                blueprint, 
                leader_traits, 
                settlement_resources, 
                settlement
            )
            scored_blueprints.append((blueprint, score))
            
        # Sort by score (highest first) and limit results
        scored_blueprints.sort(key=lambda x: x[1], reverse=True)
        return scored_blueprints[:limit]
        
    async def get_recommended_building_ids(
        self,
        settlement_id: UUID,
        limit: int = 5
    ) -> List[Tuple[UUID, float]]:
        """
        Get recommended building blueprint IDs for a settlement.
        
        Args:
            settlement_id: UUID of the settlement
            limit: Maximum number of recommendations to return
            
        Returns:
            List of tuples (blueprint_id, score) ordered by score
        """
        recommendations = await self.get_recommended_buildings(settlement_id, limit)
        return [(blueprint.entity_id, score) for blueprint, score in recommendations]