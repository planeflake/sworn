# app/game_state/workers/world_worker.py
import logging
from typing import Optional, List, Dict, Any
import asyncio
import uuid
from redis.exceptions import LockError

from app.core.celery_app import app
from app.core.redis import create_task_lock
from app.db.async_session import get_db_session, get_session
from app.game_state.services.settlement_service import SettlementService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.task
def expand_settlement(world_id=None):
    """Task entry point - uses a persistent event loop for the worker"""
    print("TASK: expand_settlement - STARTED")
    
    # Generate a task ID for logging
    task_id = str(uuid.uuid4())
    
    # Get a lock using the helper function from our centralized Redis module
    lock = create_task_lock(
        task_name="expand_settlement",
        resource_id=world_id,
        timeout=20
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
        return loop.run_until_complete(_expand_settlement_async(world_id, task_id))
        
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

async def expand_settlement_async(settlement_id: str) -> Dict[str, Any]:
    """
    Asynchronous function to expand a settlement.
    """
    # Get a database session
    async with get_db_session() as session:
        # Create an instance of WorldService
        settlement_esrvice = SettlementService(db=session)
        
        # Call the service method to expand the settlement
        result = await settlement_esrvice.expand_settlement(settlement_id=settlement_id)
        
        return result
    
async def _expand_settlement_async(world_id: Optional[str], task_id: str) -> Dict[str, Any]:    
    """
    Asynchronous function to expand a settlement.
    """
    # Get a database session
    async with get_db_session() as session:
        # Create an instance of WorldService
        settlement_esrvice = SettlementService(db=session)
        
        # Call the service method to expand the settlement
        result = await settlement_esrvice.expand_settlement(world_id=world_id)
        
        return result