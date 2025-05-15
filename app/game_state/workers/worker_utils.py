# app/game_state/workers/worker_utils.py
import asyncio
import logging
import uuid
from typing import Any, Callable, Dict, TypeVar, Coroutine
from functools import wraps
from redis.exceptions import LockError

from app.core.redis import create_task_lock

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

T = TypeVar('T')

def with_task_lock(
    task_name: str,
    timeout: int = 3600
) -> Callable:
    """
    Decorator that wraps a Celery task with Redis lock handling logic.
    
    Args:
        task_name: Name used for the Redis lock key
        timeout: Lock timeout in seconds (default: 1 hour)
        
    Returns:
        Decorator function
    """
    def decorator(task_func: Callable) -> Callable:
        @wraps(task_func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            # Extract resource_id if provided in kwargs
            resource_id = kwargs.get('world_id')
            
            # Generate a task ID for logging
            task_id = str(uuid.uuid4())
            
            # Get a lock using the helper function
            lock = create_task_lock(
                task_name=task_name,
                resource_id=resource_id,
                timeout=timeout
            )
            
            have_lock = False
            
            try:
                # Try to acquire lock - non-blocking to prevent queue buildup
                have_lock = lock.acquire(blocking=False)
                
                if not have_lock:
                    print(f"Task {task_id}: Lock already held for resource: {resource_id or 'ALL'}, skipping execution")
                    return {
                        "success": False, 
                        "skipped": True, 
                        "reason": f"Another task is already processing this {task_name}"
                    }
                    
                print(f"Task {task_id}: Acquired lock for resource: {resource_id or 'ALL'}, proceeding with execution")
                
                # Get or create an event loop - don't close it after use
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    # No event loop in current thread, create a new one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    print(f"Task {task_id}: Created new event loop")
                
                # Add task_id to kwargs 
                kwargs['task_id'] = task_id
                
                # Run the task function
                return task_func(*args, **kwargs)
                
            except Exception as e:
                logger.exception(f"Task {task_id}: Error in {task_name}: {str(e)}")
                return {"success": False, "error": str(e)}
            finally:
                # Always release the lock if we have it, even if an exception occurred
                if have_lock:
                    try:
                        lock.release()
                        print(f"Task {task_id}: Released lock for resource: {resource_id or 'ALL'}")
                    except LockError:
                        # Lock might have expired
                        logger.warning(f"Task {task_id}: Failed to release lock - it may have expired")
        
        return wrapper
    
    return decorator

def run_async_task(async_func: Callable[..., Coroutine[Any, Any, T]], *args, **kwargs) -> T:
    """
    Run an async function in the current event loop or create a new one if needed.
    
    Args:
        async_func: Async function to run
        *args, **kwargs: Arguments to pass to the async function
        
    Returns:
        Result from the async function
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # No event loop in current thread, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    return loop.run_until_complete(async_func(*args, **kwargs))