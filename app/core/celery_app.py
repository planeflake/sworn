# celery_app.py
from celery import Celery
import os
# from celery.schedules import crontab # Use simple floats for seconds interval

# Get Redis configuration from environment variables with fallbacks
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', '0')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# Construct Redis URLs for Broker and Backend
# Ensure your Redis server is running!
REDIS_URL = f"redis://{f':{REDIS_PASSWORD}@' if REDIS_PASSWORD else ''}{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)

# Create a new Celery instance
# The first argument is the name of the current module, used for naming tasks automatically
# The 'main' name here corresponds to the typical Celery convention, but you could use 'sworn'
# Make sure the task name in beat_schedule matches the final auto-generated name
# or explicitly name your tasks with @app.task(name='my.explicit.task.name')
app = Celery('sworn_tasks')

# Configure Celery
app.conf.update(
    broker_url=CELERY_BROKER_URL,
    result_backend=CELERY_RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # --- Asyncio Configuration ---
    # Use 'prefork' (default) or 'gevent'/'eventlet' if needed.
    # 'solo' is okay for simple testing but has limitations.
    # 'prefork' is generally recommended for I/O-bound async tasks as it provides
    # multiple event loops (one per worker process).
    worker_pool='gevent', # Changed from 'solo' - usually better for async I/O
    # Let Celery manage the asyncio event loop within the worker process
    # No specific 'event_loop' setting needed in recent Celery versions when using async def tasks.
    # --- Other Settings ---
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_prefetch_multiplier=1, # Good for long-running tasks
    worker_max_tasks_per_child=1000, # Restart worker process after 1000 tasks
    # Define includes for task auto-discovery
    # Point this to the modules where your @app.task definitions live
    imports=('app.game_state.workers.world_worker',) # Updated path
)

# Define the beat schedule (periodic tasks)
app.conf.beat_schedule = {
    'advance-game-day-every-10-seconds': {
        # The task name string: 'module_path.function_name'
        # This path MUST be importable by the Celery worker and beat.
        'task': 'app.game_state.workers.world_worker.advance_game_day',
        'schedule': 3660.0,  # Run every 10 seconds
        'args': (None,),  # Arguments to pass to the task (advance all worlds)
        # Optionally add options like: 'options': {'queue': 'periodic'}
    },
    # Add other periodic tasks here if needed
}

# Optional: Set default queue, routing, etc.
# app.conf.task_default_queue = 'default'
# app.conf.task_routes = {'app.game_state.workers.world_worker.*': {'queue': 'world'}}

# Auto-discover tasks from the locations specified in app.conf.imports
# You don't strictly need autodiscover_tasks() if you list modules in 'imports'
# app.autodiscover_tasks(['app.game_state.workers']) # Keep only if needed and imports isn't enough

if __name__ == '__main__':
    # This allows running the worker directly using: python celery_app.py worker -l info
    # However, the recommended way is using the `celery` command-line tool.
    app.worker_main()