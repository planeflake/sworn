# app/game_state/workers/settlement_worker.py
import logging
from typing import Optional, Dict, Any
import uuid
from uuid import UUID

from app.core.celery_app import app
from app.db.async_session import get_db_session
from app.game_state.services.settlement_service import SettlementService
#from app.api.schemas.settlement import SettlementBase
from app.api.schemas.settlement import SettlementRead
from app.game_state.workers.worker_utils import with_task_lock, run_async_task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.task
@with_task_lock(task_name="expand_settlement", timeout=20)
def expand_settlement(world_id=None, task_id=None):
    """Task entry point - uses a persistent event loop for the worker"""
    logging.info("TASK: expand_settlement - STARTED")
    
    # Run the async implementation using the utility function
    return run_async_task(_expand_settlement_async, world_id, task_id)

async def expand_settlement_async(settlement_id: UUID) -> SettlementRead:
    """
    Asynchronous function to expand a settlement.
    """
    # Get a database session
    async with get_db_session() as session:
        # Create an instance of SettlementService
        settlement_service = SettlementService(db=session)
        
        # Call the service method to expand the settlement
        result = await settlement_service.expand_settlement(settlement_id=settlement_id)
        
        return result
    
async def _expand_settlement_async(world_id: Optional[uuid], task_id: str) -> Dict[str, Any]:
    """
    Asynchronous function to expand a settlement based on leader traits.
    
    This worker:
    1. Gets settlements in the world
    2. For each settlement with a leader, evaluates building options
    3. Selects and constructs the highest-scoring building
    
    Args:
        world_id: Optional world ID to filter settlements
        task_id: Task identifier for logging
        
    Returns:
        Dict containing results of the settlement expansion
    """
    print(f"Task {task_id}: Starting expansion for world: {world_id or 'ALL WORLDS'}")
    
    # Get a database session
    async with get_db_session() as session:
        # Create service instances
        settlement_service = SettlementService(db=session)
        from app.game_state.services.building_evaluation_service import BuildingEvaluationService
        building_evaluation_service = BuildingEvaluationService(db=session)
        #from app.game_state.services.building_instance_service import BuildingInstanceService
        #building_service = BuildingInstanceService(db=session)
        
        # Get settlements to process
        #settlements = []
        if world_id:
            # Get settlements in specific world
            settlements = await settlement_service.get_settlements_by_world(world_id)
        else:
            # Get all settlements
            settlements = await settlement_service.get_all_settlements()
            
        print(f"Task {task_id}: Found {len(settlements)} settlements to process")
        
        # Process each settlement
        results = []
        for settlement in settlements:
            try:
                settlement_id = settlement.entity_id
                print(f"Task {task_id}: Processing settlement {settlement.name} (ID: {settlement_id})")
                
                # Skip settlements without a leader
                if not settlement.leader_id:
                    print(f"Task {task_id}: Settlement {settlement.name} has no leader, skipping")
                    results.append({
                        "settlement_id": str(settlement_id),
                        "name": settlement.name,
                        "action": "skipped",
                        "reason": "No leader assigned"
                    })
                    continue
                
                # Get building recommendations based on leader traits
                recommendations = await building_evaluation_service.get_recommended_building_ids(settlement_id)
                
                if not recommendations:
                    print(f"Task {task_id}: No recommended buildings for settlement {settlement.name}")
                    results.append({
                        "settlement_id": str(settlement_id),
                        "name": settlement.name,
                        "action": "skipped",
                        "reason": "No suitable buildings available"
                    })
                    continue
                
                # Select highest scored building
                top_blueprint_id, score = recommendations[0]
                
                print(f"Task {task_id}: Selected building blueprint {top_blueprint_id} with score {score}")
                
                # TODO: Check if settlement can afford this building
                # This would be added when the resource management system is completed
                
                # TODO: Create a new building instance
                # This would be added when the building construction system is completed
                
                results.append({
                    "settlement_id": str(settlement_id),
                    "name": settlement.name,
                    "action": "identified",
                    "building_blueprint_id": str(top_blueprint_id),
                    "score": score,
                    "status": "Identified optimal building, but construction not yet implemented"
                })
                
            except Exception as e:
                print(f"Task {task_id}: Error processing settlement {settlement.name if settlement else 'Unknown'}: {e}")
                results.append({
                    "settlement_id": str(settlement.entity_id) if settlement else "unknown",
                    "name": settlement.name if settlement else "Unknown",
                    "action": "error",
                    "error": str(e)
                })
        
        return {
            "success": True,
            "processed_settlements": len(settlements),
            "pending_construction": len([r for r in results if r.get("action") == "identified"]),
            "skipped_settlements": len([r for r in results if r.get("action") == "skipped"]),
            "error_settlements": len([r for r in results if r.get("action") == "error"]),
            "results": results
        }