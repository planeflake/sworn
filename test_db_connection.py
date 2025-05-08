# test_db_connection.py
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.sql import text # Use text for a simple query
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_connection():
    """Tests database connection using async_session_local."""
    print("--- Starting DB Connection Test ---")

    # Ensure project root is findable if needed (usually not for direct imports)
    # But good practice to ensure imports work as expected
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    # Add parent if needed, depending on your structure
    # if PROJECT_ROOT not in sys.path:
    #    sys.path.insert(0, os.path.dirname(PROJECT_ROOT)) # Add 'sworn' dir

    # --- Load Environment Variables ---
    # Crucial for the standalone script
    print("Loading environment variables from .env...")
    loaded = load_dotenv()
    if not loaded:
        print("Warning: .env file not found or empty.")
    # Optional: Print loaded vars to verify
    print(f"DBHOST from env: {os.getenv('DBHOST')}")
    print(f"DBPORT from env: {os.getenv('DBPORT')}")
    print(f"DBNAME from env: {os.getenv('DBNAME')}")
    # Avoid printing password if possible
    # print(f"DBUSER from env: {os.getenv('DBUSER')}")

    try:
        # --- Import the session factory ---
        # Ensure the path is correct relative to PROJECT_ROOT
        print("Importing async_session_local from app.db.async_session...")
        from app.db.async_session import async_session_local
        print("Import successful.")

        # --- Attempt to use the session factory ---
        print("\nAttempting to enter 'async with async_session_local()'...")
        async with async_session_local() as session:
            print(">>> SUCCESSFULLY entered 'async with' block. Session acquired.")
            print(f"Session object: {session}")

            # --- Perform a simple query ---
            print("\nAttempting a simple query: SELECT 1")
            try:
                result = await session.execute(text("SELECT 1"))
                value = result.scalar_one()
                print(f">>> Query successful! Result: {value}")
                print("Database connection appears to be working correctly.")
            except Exception as query_e:
                print(f"!!! ERROR during query execution: {query_e}")
                logging.exception("Query execution failed:") # Log traceback

    except ImportError as e:
        print(f"\n!!! IMPORT ERROR: Could not import async_session_local.")
        print(f"    Error details: {e}")
        print(f"    Check PYTHONPATH or if the file app/db/async_session.py exists.")
    except ValueError as e:
         print(f"\n!!! VALUE ERROR (likely missing env vars): {e}")
    except Exception as e:
        print(f"\n!!! UNEXPECTED ERROR during session acquisition or setup: {e}")
        logging.exception("Test connection failed:") # Log traceback

    print("\n--- DB Connection Test Finished ---")

if __name__ == "__main__":
    asyncio.run(test_connection())