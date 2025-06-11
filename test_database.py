# test_database.py
from database import get_db, engine, Base, SessionLocal
from sqlalchemy.orm import Session
import logging
import sys
from config.settings import sql_alchemy_database_url
from sqlalchemy import inspect

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database_connection(use_session_local=False):
    """
    Test the database connection.

    Args:
        use_session_local (bool): If True, use SessionLocal directly. If False, use get_db generator.

    Returns:
        bool: True if connection is successful, False otherwise.
    """
    logger.info("Testing database connection...")
    logger.info(f"Using connection string: {sql_alchemy_database_url}")

    try:
        if use_session_local:
            # Use SessionLocal directly
            db = SessionLocal()
            connection_source = "SessionLocal"
        else:
            # Use get_db generator
            db = next(get_db())
            connection_source = "get_db generator"

        logger.info(f"Created database session using {connection_source}")

        try:
            # Try to execute a simple query
            result = db.execute("SELECT 1")
            logger.info(f"Database connection successful! Result: {result.fetchone()}")

            # Check database dialect
            dialect = engine.dialect.name
            logger.info(f"Database dialect: {dialect}")

            if dialect == 'mssql':
                logger.info("Successfully connected to SQL Server database.")
            elif dialect == 'sqlite':
                logger.warning("Connected to SQLite database. SQL Server connection might have failed.")
            else:
                logger.info(f"Connected to {dialect} database.")

            # Check database schema
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"Tables in database: {tables}")

            return True
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return False
        finally:
            db.close()
            logger.info("Database session closed.")
    except Exception as e:
        logger.error(f"Error creating database session: {str(e)}")
        return False

def create_tables():
    """Create database tables if they don't exist."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created or already exist.")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        return False

if __name__ == "__main__":
    # Create tables if they don't exist
    if not create_tables():
        logger.error("Failed to create database tables.")
        sys.exit(1)

    # Test the database connection
    success = test_database_connection()
    if not success:
        logger.error("Database connection test failed.")
        sys.exit(1)
    logger.info("Database connection test completed successfully.")
