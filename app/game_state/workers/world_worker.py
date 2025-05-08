# app/game_state/workers/world_worker.py
import logging
from typing import Optional, List, Dict, Any
import asyncio
import uuid
from redis.exceptions import LockError

from app.core.celery_app import app
from app.core.redis import create_task_lock
from app.db.async_session import get_db_session, get_session
from app.game_state.services.world_service import WorldService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.task
def advance_game_day(world_id=None):
    """Task entry point - uses a persistent event loop for the worker"""
    print("TASK: advance_game_day - STARTED")
    
    # Generate a task ID for logging
    task_id = str(uuid.uuid4())
    
    # Get a lock using the helper function from our centralized Redis module
    lock = create_task_lock(
        task_name="advance_game_day",
        resource_id=world_id,
        timeout=3660
    )
    
    have_lock = False
    
    try:
        # Try to acquire lock - non-blocking to prevent queue buildup
        have_lock = lock.acquire(blocking=False)
        
        if not have_lock:
            print(f"Task {task_id}: Lock already held for world: {world_id or 'ALL'}, skipping execution")
            return {
                "success": False, 
                "skipped": True, 
                "reason": "Another task is already processing this world"
            }
            
        print(f"Task {task_id}: Acquired lock for world: {world_id or 'ALL'}, proceeding with execution")
        
        # Get or create an event loop - don't close it after use
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # No event loop in current thread, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            print(f"Task {task_id}: Created new event loop")
        
        # Run the async implementation
        return loop.run_until_complete(_advance_game_day_async(world_id, task_id))
        
    except Exception as e:
        logger.exception(f"Task {task_id}: Error in advance_game_day: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        # Always release the lock if we have it, even if an exception occurred
        if have_lock:
            try:
                lock.release()
                print(f"Task {task_id}: Released lock for world: {world_id or 'ALL'}")
            except LockError:
                # Lock might have expired
                logger.warning(f"Task {task_id}: Failed to release lock - it may have expired")

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