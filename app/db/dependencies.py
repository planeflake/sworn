# Inside app/db/dependencies.py
import logging
from app.db.async_session import async_session_local # Use your factory
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency using explicit commit/rollback for debugging."""
    logging.info(">>> [Dependency] Creating session...")
    session: AsyncSession = async_session_local()
    session_closed = False
    try:
        # Begin isn't strictly necessary with autocommit=False (default)
        # but can make transaction boundaries explicit if needed.
        # await session.begin() # Optional explicit begin
        logging.info(f">>> [Dependency] Session {id(session)} created.")
        yield session
        # --- Explicit Commit ---
        logging.info(f">>> [Dependency] Yield completed for session {id(session)}. Attempting explicit commit...")
        await session.commit()
        logging.info(f">>> [Dependency] Explicit commit successful for session {id(session)}.")
    except Exception as e:
        logging.error(f">>> [Dependency] Exception escaped yield for session {id(session)}: {e}", exc_info=True)
        logging.info(f">>> [Dependency] Attempting explicit rollback for session {id(session)}...")
        await session.rollback()
        logging.info(f">>> [Dependency] Explicit rollback successful for session {id(session)}.")
        raise # Re-raise exception for FastAPI
    finally:
        if not session_closed and session.is_active: # Check if active before closing
             logging.info(f">>> [Dependency] Closing session {id(session)}...")
             await session.close()
             session_closed = True
             logging.info(f">>> [Dependency] Session {id(session)} closed.")
        else:
             logging.info(f">>> [Dependency] Session {id(session)} already closed or inactive in finally block.")