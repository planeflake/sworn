# app/game_state/workers/world_worker.py
import logging
from typing import Optional, List, Dict, Any, Tuple
import asyncio
import uuid
from redis.exceptions import LockError
import time
import math

from celery import group
from app.core.celery_app import app
from app.core.redis import create_task_lock
from app.db.async_session import get_session
from app.game_state.services.world_service import WorldService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration for distributed processing
BATCH_SIZE = 20  # Maximum number of worlds to process in a single task
MIN_WORLDS_FOR_DISTRIBUTION = 5  # Minimum number of worlds needed before distributing tasks
MAX_CONCURRENT_TASKS = 5  # Maximum number of tasks to launch in parallel
LOCK_TIMEOUT = 60  # Lock timeout in seconds


@app.task
def advance_game_day(world_id=None):
    """
    Main task entry point for advancing game day.
    
    This function serves as a dispatcher. It has two modes of operation:
    
    1. Single World Mode (world_id is provided):
       - Processes just that one specific world
       
    2. Distribution Mode (world_id is None):
       - Fetches all world IDs
       - Distributes them across multiple worker tasks
       - Launches those tasks in parallel
    
    Args:
        world_id (str, optional): Specific world ID to process. If None, distributes processing.
    """
    print(f"TASK: advance_game_day - STARTED with world_id={world_id}")
    
    # Generate a task ID for logging
    task_id = str(uuid.uuid4())
    
    if world_id is not None:
        # Single world mode - process just this one world
        return _process_single_world(world_id, task_id)
    else:
        # Distribution mode - fetch all worlds and distribute them
        return _distribute_world_processing(task_id)


def _distribute_world_processing(task_id: str) -> Dict[str, Any]:
    """
    Distributes world processing across multiple tasks.
    
    This function:
    1. Fetches all world IDs
    2. Creates batches of worlds
    3. Launches separate tasks for each batch
    4. Returns the task IDs for monitoring
    
    Args:
        task_id (str): Task identifier for logging
        
    Returns:
        Dict: Results including task IDs of the launched subtasks
    """
    print(f"Task {task_id}: Distribution mode - fetching all world IDs")
    
    # Get or create an event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print(f"Task {task_id}: Created new event loop for distribution")
    
    # Get all world IDs
    world_ids = loop.run_until_complete(_get_all_world_ids())
    
    if not world_ids:
        print(f"Task {task_id}: No worlds found to advance")
        return {"success": False, "error": "No worlds found to advance"}
    
    print(f"Task {task_id}: Found {len(world_ids)} worlds to process")
    
    # If we only have a few worlds, process them directly
    if len(world_ids) < MIN_WORLDS_FOR_DISTRIBUTION:
        print(f"Task {task_id}: Only {len(world_ids)} worlds - processing directly without distribution")
        results = loop.run_until_complete(_process_worlds_directly(world_ids, task_id))
        return {"success": True, "distribution": False, "results": results}
    
    # Create batches of worlds
    batches = _create_world_batches(world_ids, BATCH_SIZE)
    print(f"Task {task_id}: Created {len(batches)} batches of worlds")
    
    # Limit concurrent tasks to MAX_CONCURRENT_TASKS
    batches_to_process = min(len(batches), MAX_CONCURRENT_TASKS)
    print(f"Task {task_id}: Launching {batches_to_process} concurrent processing tasks")
    
    # Launch a separate task for each batch
    subtasks = []
    for i in range(batches_to_process):
        batch = batches[i]
        # Create a new task for this batch
        subtask = process_world_batch.delay(batch, f"{task_id}-batch-{i}")
        subtasks.append(subtask.id)
    
    return {
        "success": True,
        "distribution": True,
        "total_worlds": len(world_ids),
        "batches_created": len(batches),
        "batches_launched": batches_to_process,
        "subtask_ids": subtasks
    }


@app.task
def process_world_batch(world_ids: List[str], batch_id: str) -> Dict[str, Any]:
    """
    Process a batch of worlds in a separate task.
    
    This function takes a list of world IDs and processes them one by one,
    using individual locks for each world to prevent conflicts.
    
    Args:
        world_ids (List[str]): List of world IDs to process
        batch_id (str): Batch identifier for logging
        
    Returns:
        Dict: Results of processing each world
    """
    print(f"BATCH {batch_id}: Starting processing of {len(world_ids)} worlds")
    
    # Get or create an event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print(f"BATCH {batch_id}: Created new event loop")
    
    # Process each world in the batch, returning combined results
    results = loop.run_until_complete(_process_batch_async(world_ids, batch_id))
    
    print(f"BATCH {batch_id}: Completed processing {len(world_ids)} worlds")
    return {
        "success": True,
        "batch_id": batch_id,
        "worlds_processed": len(results),
        "results": results
    }


def _process_single_world(world_id: str, task_id: str) -> Dict[str, Any]:
    """
    Process a single world with proper locking.
    
    This function obtains a lock specific to the world,
    processes it, and then releases the lock.
    
    Args:
        world_id (str): The ID of the world to process
        task_id (str): Task identifier for logging
        
    Returns:
        Dict: Results of processing the world
    """
    print(f"Task {task_id}: Single world mode - processing world {world_id}")
    
    # Get a lock specific to this world
    lock = create_task_lock(
        task_name="advance_game_day",
        resource_id=world_id,
        timeout=LOCK_TIMEOUT
    )
    
    have_lock = False
    
    try:
        # Try to acquire lock - non-blocking to prevent queue buildup
        have_lock = lock.acquire(blocking=False)
        
        if not have_lock:
            print(f"Task {task_id}: Lock already held for world: {world_id}, skipping execution")
            return {
                "success": False, 
                "skipped": True, 
                "reason": f"Another task is already processing world {world_id}"
            }
            
        print(f"Task {task_id}: Acquired lock for world: {world_id}, proceeding with execution")
        
        # Get or create an event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            print(f"Task {task_id}: Created new event loop")
        
        # Process the world
        result = loop.run_until_complete(_advance_single_world_async(world_id, task_id))
        return result
        
    except Exception as e:
        logger.exception(f"Task {task_id}: Error processing world {world_id}: {str(e)}")
        return {"success": False, "error": str(e), "world_id": world_id}
    finally:
        # Always release the lock if we have it
        if have_lock:
            try:
                lock.release()
                print(f"Task {task_id}: Released lock for world: {world_id}")
            except LockError:
                logger.warning(f"Task {task_id}: Failed to release lock for world {world_id}")


async def _get_all_world_ids() -> List[str]:
    """
    Fetch all world IDs from the database.
    
    Returns:
        List[str]: List of world IDs
    """
    # Create a fresh session
    session = await get_session()
    
    try:
        # Create a WorldService and fetch all world IDs
        world_service = WorldService(session)
        return await world_service.get_all_world_ids(session)
    finally:
        # Ensure the session is closed
        await session.close()


def _create_world_batches(world_ids: List[str], batch_size: int) -> List[List[str]]:
    """
    Create batches of world IDs for distributed processing.
    
    Args:
        world_ids (List[str]): List of all world IDs
        batch_size (int): Maximum size of each batch
        
    Returns:
        List[List[str]]: List of world ID batches
    """
    return [world_ids[i:i + batch_size] for i in range(0, len(world_ids), batch_size)]


async def _process_batch_async(world_ids: List[str], batch_id: str) -> List[Dict[str, Any]]:
    """
    Process multiple worlds asynchronously with individual locking.
    
    Args:
        world_ids (List[str]): List of world IDs to process
        batch_id (str): Batch identifier for logging
        
    Returns:
        List[Dict]: Results for each world
    """
    results = []
    
    # Process each world in sequence, with individual locks
    for world_id in world_ids:
        # Create a unique ID for this world processing attempt
        process_id = f"{batch_id}-{world_id[:8]}"
        
        # Get a lock specific to this world
        lock = create_task_lock(
            task_name="advance_game_day",
            resource_id=world_id,
            timeout=LOCK_TIMEOUT
        )
        
        have_lock = False
        
        try:
            # Try to acquire lock - non-blocking
            have_lock = lock.acquire(blocking=False)
            
            if not have_lock:
                print(f"BATCH {batch_id}: Lock already held for world {world_id}, skipping")
                results.append({
                    "world_id": world_id,
                    "success": False,
                    "skipped": True,
                    "reason": "Another task is already processing this world"
                })
                continue
            
            print(f"BATCH {batch_id}: Acquired lock for world {world_id}, processing")
            
            # Process the world
            result = await _advance_single_world_async(world_id, process_id)
            results.append(result)
            
        except Exception as e:
            logger.exception(f"BATCH {batch_id}: Error processing world {world_id}: {str(e)}")
            results.append({
                "world_id": world_id,
                "success": False,
                "error": str(e)
            })
        finally:
            # Always release the lock if we have it
            if have_lock:
                try:
                    lock.release()
                    print(f"BATCH {batch_id}: Released lock for world {world_id}")
                except LockError:
                    logger.warning(f"BATCH {batch_id}: Failed to release lock for world {world_id}")
    
    return results


async def _process_worlds_directly(world_ids: List[str], task_id: str) -> List[Dict[str, Any]]:
    """
    Process a small number of worlds directly without distribution.
    
    Args:
        world_ids (List[str]): List of world IDs to process
        task_id (str): Task identifier for logging
        
    Returns:
        List[Dict]: Results for each world
    """
    print(f"Task {task_id}: Processing {len(world_ids)} worlds directly")
    return await _process_batch_async(world_ids, task_id)


async def _advance_single_world_async(world_id: str, task_id: str) -> Dict[str, Any]:
    """
    Advance a single world's game day.
    
    Args:
        world_id (str): ID of the world to advance
        task_id (str): Task identifier for logging
        
    Returns:
        Dict: Results of the operation
    """
    print(f"Task {task_id}: Advancing world {world_id}")
    
    # Get a fresh session for this operation
    session = await get_session()
    
    try:
        # Create a WorldService instance with the session
        world_service = WorldService(session)
        
        # Advance the world's game day
        updated_world = await world_service.advance_game_day(world_id)
        
        if updated_world:
            print(f"Task {task_id}: Successfully advanced world {world_id} to day {updated_world.day}")
            return {
                "world_id": updated_world.id,
                "day": updated_world.day,
                "success": True
            }
        else:
            print(f"Task {task_id}: Failed to advance world {world_id} - not found or error")
            return {
                "world_id": world_id,
                "success": False,
                "error": "World not found or could not be advanced"
            }
    finally:
        # Ensure the session is properly closed
        await session.close()
        print(f"Task {task_id}: Closed DB session for world {world_id}")