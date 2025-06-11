# database.py
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import sql_alchemy_database_url, sqlite_database_url  # Import from settings.py

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create a Base class for declarative class definitions (SQLAlchemy models)
# This needs to be defined before importing models to avoid circular imports
Base = declarative_base()

# Try to create the SQLAlchemy engine with SQL Server
try:
    logger.info("Attempting to connect to SQL Server...")
    engine = create_engine(
        sql_alchemy_database_url,
        pool_pre_ping=True,  # Check connection before using from pool
        pool_recycle=3600,   # Recycle connections after 1 hour
        pool_size=5,         # Maximum number of connections to keep in pool
        max_overflow=10      # Maximum number of connections to create beyond pool_size
    )

    # Test the connection
    with engine.connect() as connection:
        connection.execute("SELECT 1")
    logger.info("Successfully connected to SQL Server")

except Exception as e:
    logger.error(f"Error connecting to SQL Server: {str(e)}")
    logger.warning("Falling back to SQLite database")

    # Fallback to SQLite if SQL Server connection fails
    engine = create_engine(
        sqlite_database_url,
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )

# Create a SessionLocal class, which will be used to create database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a DB session in FastAPI path operations
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
