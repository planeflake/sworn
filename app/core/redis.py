"""
Centralized Redis client module.
Provides a shared Redis client instance for the application.
"""
import os
import redis
import logging


# Get Redis configuration from environment variables with fallbacks
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', '0')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# Create and export the Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=int(REDIS_PORT),
    db=int(REDIS_DB),
    password=REDIS_PASSWORD,
    decode_responses=True
)

# Add useful helper functions for common Redis operations

def get_lock(name, timeout=60, sleep=0.1, blocking=False):
    """
    Get a Redis lock with the given name and timeout.
    
    Args:
        name (str): The name of the lock
        timeout (int): The lock timeout in seconds
        sleep (float): The sleep time between blocking retries
        blocking (bool): Whether to block until the lock is acquired
        
    Returns:
        redis.Lock: A Redis lock object
    """
    return redis_client.lock(
        name=name,
        timeout=timeout, 
        sleep=sleep,
        blocking=blocking
    )

def create_task_lock(task_name, resource_id=None, timeout=60):
    """
    Create a lock specifically for Celery tasks.
    
    Args:
        task_name (str): The name of the task
        resource_id (str, optional): The ID of the resource being processed
        timeout (int): The lock timeout in seconds
        
    Returns:
        redis.Lock: A Redis lock object
    """
    lock_name = f"task_lock:{task_name}:{resource_id or 'all'}"
    return get_lock(lock_name, timeout=timeout)

def health_check():
    """
    Check that Redis is working correctly.
    
    Returns:
        bool: True if Redis is working, False otherwise
    """
    try:
        return redis_client.ping()
    except Exception as e:
        logging.error(f"Redis health check failed: {str(e)}")
        return False