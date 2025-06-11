# test_templates.py
from database import SessionLocal
from repositories import template_repository
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_templates():
    """Test template database operations."""
    logger.info("Starting template database operations test...")

    # Create a database session
    db = SessionLocal()
    try:
        # Test creating a template
        test_endpoint_type = "test-endpoint"
        test_name = "Test Template"
        test_body = {"name": "test-template", "description": "A test template"}

        logger.info(f"Creating test template '{test_name}' for '{test_endpoint_type}'...")
        template = template_repository.create_template(db, test_name, test_endpoint_type, test_body)
        logger.info(f"Created template with ID: {template.id}")

        # Test getting a template by name and type
        logger.info(f"Getting template '{test_name}' for '{test_endpoint_type}'...")
        retrieved_template = template_repository.get_template_by_name_and_type(db, test_name, test_endpoint_type)
        if retrieved_template:
            logger.info(f"Retrieved template: {retrieved_template.to_dict()}")
        else:
            logger.error(f"Failed to retrieve template '{test_name}' for '{test_endpoint_type}'")

        # Test getting all templates for an endpoint type
        logger.info(f"Getting all templates for '{test_endpoint_type}'...")
        templates = template_repository.get_templates_by_type(db, test_endpoint_type)
        logger.info(f"Retrieved {len(templates)} templates for '{test_endpoint_type}'")

        # Test updating a template
        updated_body = {"name": "updated-test-template", "description": "An updated test template"}
        logger.info(f"Updating template '{test_name}' for '{test_endpoint_type}'...")
        updated_template = template_repository.update_template(db, test_name, test_endpoint_type, updated_body)
        if updated_template:
            logger.info(f"Updated template: {updated_template.to_dict()}")
        else:
            logger.error(f"Failed to update template '{test_name}' for '{test_endpoint_type}'")

        # Test deleting a template
        logger.info(f"Deleting template '{test_name}' for '{test_endpoint_type}'...")
        deleted = template_repository.delete_template(db, test_name, test_endpoint_type)
        if deleted:
            logger.info(f"Template '{test_name}' for '{test_endpoint_type}' deleted successfully")
        else:
            logger.error(f"Failed to delete template '{test_name}' for '{test_endpoint_type}'")

        logger.info("Template database operations test completed successfully")
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_templates()