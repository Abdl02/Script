import logging
import sys
from test_database import test_database_connection, create_tables

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection():
    """
    Test connection to the database using SessionLocal directly.
    This is a wrapper around test_database_connection with use_session_local=True.
    """
    logger.info("Testing direct database connection using SessionLocal...")
    return test_database_connection(use_session_local=True)

if __name__ == "__main__":
    # Create tables if they don't exist
    if not create_tables():
        logger.error("Failed to create database tables.")
        sys.exit(1)

    # Test the database connection
    success = test_connection()
    if not success:
        logger.error("Database connection test failed.")
        sys.exit(1)
    logger.info("Database connection test completed successfully.")
