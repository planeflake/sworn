# app/game_state/workers/world_worker.py
import logging
from typing import Dict, Any

from app.core.celery_app import app
from app.db.async_session import get_session
from app.game_state.services.core.world_service import WorldService
from app.game_state.workers.worker_utils import with_task_lock, run_async_task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.task
@with_task_lock(task_name="advance_game_day", timeout=3660)
def advance_game_day(world_id=None, task_id=None):
    """Task entry point - uses a persistent event loop for the worker"""
    print("TASK: advance_game_day - STARTED")
    
    # Run the async implementation using the utility function
    return run_async_task(_advance_game_day_async, world_id, task_id)

async def _advance_game_day_async(world_id=None, task_id=None) -> Dict[str, Any]:
    """Async implementation of the task"""
    # Log that we're starting
    print(f"Task {task_id}: Processing advance game day for world: {world_id or 'ALL'}")
    print(f"Task {task_id}: Creating fresh DB session...")
    
    # Get a fresh session for this specific task execution
    # This creates a new session bound to the current event loop
    session = await get_session()
    
    try:
        print(f"Task {task_id}: DB session {session} acquired. Calling WorldService...")
        
        # Create service with the session
        world_service = WorldService(session)
        
        # Process a single world if ID is provided
        if world_id:
            print(f"Task {task_id}: Advancing world {world_id}...")
            result = await world_service.advance_game_day(world_id)
            if result:
                return {
                    "success": True, 
                    "results": [{
                        "world_id": result.id, 
                        "day": result.day, 
                        "success": True
                    }]
                }
            else:
                return {"success": False, "error": f"World {world_id} not found or could not be advanced."}
        
        # Otherwise process all worlds
        print(f"Task {task_id}: No world_id provided. Loading all worlds...")
        worlds = await world_service.get_all_world_ids(session)
        
        if not worlds:
            print(f"Task {task_id}: No worlds found to advance.")
            return {"success": False, "error": "No worlds found to advance."}
        
        results = []
        for world_id in worlds:
            print(f"Task {task_id}: Advancing world {world_id}...")
            updated_world = await world_service.advance_game_day(world_id=world_id)
            if updated_world:
                results.append({
                    "world_id": updated_world.id,
                    "day": updated_world.day,
                    "success": True
                })
        
        print(f"Task {task_id}: All worlds advanced. Task finished.")
        return {"success": True, "results": results}
    finally:
        # Ensure the session is properly closed
        await session.close()
        print(f"Task {task_id}: DB session closed")