# app/db/async_session.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import asyncio
import os
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager

load_dotenv()  # Load environment variables from .env file

logger = logging.getLogger(__name__)

# --- Database Connection Details ---
DBNAME = os.getenv("DBNAME")
DBHOST = os.getenv("DBHOST")
DBPORT = os.getenv("DBPORT")
DBUSER = os.getenv("DBUSER")
DBPASSWORD = os.getenv("DBPASSWORD")

# Basic validation (optional but recommended)
if not all([DBNAME, DBHOST, DBPORT, DBUSER, DBPASSWORD]):
    raise ValueError("One or more database environment variables are not set.")

DATABASE_URL = f"postgresql+asyncpg://{DBUSER}:{DBPASSWORD}@{DBHOST}:{DBPORT}/{DBNAME}"

# --- Engine creation function to ensure proper event loop binding ---
def get_engine():
    """
    Creates an async engine bound to the current event loop.
    This ensures connections are properly managed within the context
    of the current event loop.
    """
    try:
        # Get current event loop or create one
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # No event loop in current thread, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        logger.info("Created new event loop for database engine")
    
    # Create engine with explicit loop binding
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        future=True,
        pool_size=5,          # Smaller pool to reduce connection issues
        max_overflow=10,      # Reduced overflow
        pool_timeout=30,      # Connection acquisition timeout
        pool_pre_ping=True,   # Checks connection validity before use
        pool_use_lifo=True,   # Prefer recently used connections
        pool_recycle=1800,    # Recycle connections after 30 minutes
    )
    
    return engine

# Create a default engine
async_engine = get_engine()

# --- Create the Session Factory ---
async_session_maker = async_sessionmaker(
    expire_on_commit=False,
    class_=AsyncSession,
)

# --- Session creation function ---
async def get_session():
    """
    Creates a new session bound to an engine that's connected to the current event loop.
    This should be used in contexts where you want to ensure proper event loop binding.
    """
    engine = get_engine()
    session = async_session_maker(bind=engine)
    return session

# Backward compatibility for existing code
async_session_local = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Context manager for safely using a session
@asynccontextmanager
async def get_db_session():
    """
    A context manager that provides a database session and handles cleanup properly.
    Usage:
        async with get_db_session() as session:
            # use session here
    """
    session = await get_session()
    try:
        yield session
    finally:
        await session.close()