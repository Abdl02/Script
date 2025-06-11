# init_db.py
from database import engine, Base
from models import Template  # Import all models
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database by creating all tables."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")

        # Verify tables were created by checking if they exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Tables in database: {tables}")

        # Check for required tables
        required_tables = ["templates"]
        missing_tables = [table for table in required_tables if table not in tables]

        if missing_tables:
            logger.warning(f"The following tables were not created: {', '.join(missing_tables)}")
            logger.warning("There might be an issue with the database connection or schema definition.")

            # Try to diagnose the issue
            if engine.dialect.name == 'sqlite':
                logger.info("Using SQLite database. Make sure the database file is accessible and not corrupted.")
            elif engine.dialect.name == 'mssql':
                logger.info("Using SQL Server database. Make sure the connection parameters are correct and the server is running.")


            # Return False to indicate failure, but don't raise an exception
            return False
        else:
            logger.info("All required tables exist. Database initialization successful.")

        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        # Log more detailed error information based on the exception type
        if "permission" in str(e).lower():
            logger.error("This might be a permission issue. Make sure the user has the necessary permissions to create tables.")
        elif "timeout" in str(e).lower():
            logger.error("Database connection timed out. Make sure the database server is running and accessible.")
        elif "already exists" in str(e).lower():
            logger.warning("Some tables already exist. This might not be an error if you're re-initializing the database.")
            return True

        return False

if __name__ == "__main__":
    success = init_db()
    if not success:
        logger.error("Database initialization failed.")
        sys.exit(1)
    logger.info("Database initialization completed.")
