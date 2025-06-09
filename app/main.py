# main.py
import subprocess
import sys
import os
from multiprocessing import Process
import uvicorn
from dotenv import load_dotenv
import signal
import logging

# Configure logging at the application level
def configure_logging():
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear any existing handlers to avoid duplicates
    root_logger.handlers = []
    
    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add the handler to the root logger
    root_logger.addHandler(console_handler)
    
    # Set up app's loggers
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.INFO)
    
    # Set up SQLAlchemy logger explicitly
    sa_logger = logging.getLogger('sqlalchemy.engine')
    sa_logger.setLevel(logging.INFO)
    
    logging.info("Logging configured successfully")

# Configure logging first thing
print("Configuring logging...")
configure_logging()

load_dotenv()  # Load environment variables from .env file

APP_DIR = os.path.dirname(os.path.abspath(__file__)) # Directory containing main.py (e.g., C:\Projects\sworn\app)
PROJECT_ROOT = os.path.dirname(APP_DIR) # The directory containing 'app' (e.g., C:\Projects\sworn)

if PROJECT_ROOT not in sys.path:
   sys.path.insert(0, PROJECT_ROOT)
   logging.info(f"Added '{PROJECT_ROOT}' to sys.path")

# Import fastapi app *after* path adjustments
try:
    from app.api.fastapi import fastapi
except ImportError as e:
    logging.error(f"Error importing FastAPI app (from app.api.fastapi). Ensure PYTHONPATH is correct.")
    logging.error(f"PROJECT_ROOT='{PROJECT_ROOT}', sys.path='{sys.path}'")
    raise e

# Store child processes globally for signal handling
child_processes = []


def start_celery_worker():
    """Starts the Celery worker process."""
    logging.info("Starting Celery worker...")
    celery_app_path = "app.core.celery_app.app"
    cmd = [
        sys.executable, "-m", "celery",
        "-A", celery_app_path,    
        "worker",
        "--loglevel=INFO",
        "-P", "gevent",
        "--concurrency=1"
    ]
    logging.info(f"Celery Worker command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, cwd=PROJECT_ROOT)
    except FileNotFoundError:
        logging.error(f"Error: '{sys.executable} -m celery' command not found. Is Celery installed?")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logging.error(f"Celery worker process failed with exit code {e.returncode}.")
        logging.error("Check if the broker is running and accessible, and if the celery app path is correct.")
        logging.error(f"Attempted Celery app path: {celery_app_path}")
        logging.error(f"Running from directory: {PROJECT_ROOT}")
        sys.exit(e.returncode)
    except Exception as e:
        logging.error(f"An unexpected error occurred starting the Celery worker: {e}")
        sys.exit(1)

def start_uvicorn():
    logging.info("Starting Uvicorn server…")
    uvicorn.run(
        "app.api.fastapi:fastapi",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        log_config=None,     # ← disable Uvicorn’s dictConfig override
        reload=True,
    )

def start_celery_beat():
    """Starts the Celery Beat scheduler process."""
    logging.info("Starting Celery Beat scheduler...")
    # --- IMPORTANT: Adjust the -A argument ---
    celery_app_path = "app.core.celery_app.app" # <--- CHANGE THIS
    cmd = [
        sys.executable, "-m", "celery",
        "-A", celery_app_path,          # <--- Use the correct path
        "beat",
        "--loglevel=INFO"
    ]
    logging.info(f"Celery Beat command: {' '.join(cmd)}")
    try:
        # --- IMPORTANT: Set cwd to the actual project root ---
        subprocess.run(cmd, check=True, cwd=PROJECT_ROOT) # <--- Use correct PROJECT_ROOT
    except FileNotFoundError:
        logging.error(f"Error: '{sys.executable} -m celery' command not found. Is Celery installed?")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logging.error(f"Celery Beat process failed with exit code {e.returncode}.")
        logging.error("Check if the broker is running and accessible, and if the celery app path is correct.")
        logging.error(f"Attempted Celery app path: {celery_app_path}")
        logging.error(f"Running from directory: {PROJECT_ROOT}")
        sys.exit(e.returncode)
    except Exception as e:
        logging.error(f"An unexpected error occurred starting Celery Beat: {e}")
        sys.exit(1)

def signal_handler(signum, frame):
    """Gracefully terminate child processes on SIGINT/SIGTERM."""
    logging.info(f"\nSignal {signal.Signals(signum).name} received, terminating processes...")
    for p in reversed(child_processes): # Terminate in reverse order of start
        if p.is_alive():
            logging.info(f"Terminating process {p.pid} ({p.name})...")
            try:
                p.terminate()
                p.join(timeout=10)
                if p.is_alive():
                    logging.info(f"Process {p.pid} ({p.name}) did not terminate cleanly, killing...")
                    p.kill()
                    p.join(timeout=5)
            except Exception as e:
                logging.error(f"Error terminating process {p.pid} ({p.name}): {e}")
    logging.info("All child processes terminated.")
    sys.exit(0)

def main():
    logging.info(f"Project Root: {PROJECT_ROOT}") # Should now be C:\Projects\sworn
    logging.info(f"App Directory: {APP_DIR}")     # Should now be C:\Projects\sworn\app

    logging.info("\n--- IMPORTANT: Ensure your Celery broker (e.g., Redis) is running! ---\n")

    #signal.signal(signal.SIGINT, signal_handler)
    #signal.signal(signal.SIGTERM, signal_handler)

    logging.info("Initializing processes...")
    process_targets = {
        "Celery_Beat": start_celery_beat,
        "Celery_Worker": start_celery_worker
    }

    global child_processes
    child_processes = []

    #for name, fn in process_targets.items():
    #    p = Process(target=fn, name=name, daemon=False)
    #    p.start()
    #    child_processes.append(p)
    #    logging.info(f"Started process {p.pid} for: {name}")

    try:
        logging.info("\n--- Starting Uvicorn in main process ---")
        start_uvicorn(

            
        )
        logging.info("Uvicorn process finished.")

    except Exception as e:
        logging.error(f"\nUvicorn exited unexpectedly: {e}")

    finally:
        logging.info("\n--- Uvicorn finished or errored, ensuring cleanup ---")
        signal_handler(signal.SIGTERM, None)


if __name__ == "__main__":
    # Ensure app/core/celery_app.py exists and contains the 'app = Celery(...)' instance.
    # Ensure app/core/__init__.py exists (even if empty) to mark 'core' as a package.
    # Ensure app/__init__.py exists (even if empty) to mark 'app' as a package.
    main()