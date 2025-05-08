# send_task.py
import sys
import os
import asyncio
from dotenv import load_dotenv

# Ensure project root is in path to find app modules
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Load environment variables here too, as celery_app needs them
load_dotenv()

# Import the specific task function AFTER ensuring path and env vars are set
try:
    # Assuming celery_app is now loading .env, we just need the task ref
    from app.game_state.workers.world_worker import advance_game_day
except ImportError as e:
    print(f"Error importing task. Ensure celery_app loads env vars and paths are correct.")
    print(e)
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during import: {e}")
    sys.exit(1)


async def main():
    print("\nSending advance_game_day task (world_id=None)...")
    # Use .delay() for simple calls
    # The arguments passed here match the task signature (excluding 'self')
    result_async = advance_game_day.delay(world_id=None)
    print(f"Advance_game_day task sent, task ID: {result_async.id}")

    print("\nWaiting a bit for worker to process...")
    await asyncio.sleep(15) # Wait 15 seconds

    # Optionally try to get the result (will fail if EncodeError happened)
    try:
        print(f"\nAttempting to get result for task {result_async.id}...")
        result = result_async.get(timeout=10)
        print(f"Result received: {result}")
        print(f"Task state: {result_async.state}")
    except Exception as e:
        print(f"Failed to get result: {e}")
        # Check state if result retrieval failed
        try:
             print(f"Current task state: {result_async.state}")
             # If state is FAILURE, backend might have traceback info
             # print(f"Traceback: {result_async.traceback}") # Might be large
        except Exception as state_e:
             print(f"Could not retrieve task state: {state_e}")


if __name__ == "__main__":
    print("--- Starting Task Sender ---")
    # Ensure Redis is running before sending
    # You might add a Redis ping here if needed
    asyncio.run(main())
    print("--- Task Sender Finished ---")