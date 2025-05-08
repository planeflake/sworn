from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DBNAME = os.environ["DBNAME"]
DBHOST = os.environ["DBHOST"]
DBPORT = os.environ["DBPORT"]
DBUSER = os.environ["DBUSER"]   
DBPASSWORD = os.environ["DBPASSWORD"]

# Create the async engine
sync_engine = create_engine(
    f"postgresql+asyncpg://{DBUSER}:{DBPASSWORD}@{DBHOST}:{DBPORT}/{DBNAME}",
    echo=True,
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)