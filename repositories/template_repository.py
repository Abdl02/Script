# template_repository.py
from sqlalchemy.orm import Session
from models import Template
import json
from typing import Dict, Any, List, Optional

def create_template(db: Session, name: str, endpoint_type: str, body: Dict[str, Any]) -> Template:
    """Create a new template in the database."""
    db_template = Template(name=name, endpoint_type=endpoint_type, body=body)
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def get_template_by_name_and_type(db: Session, name: str, endpoint_type: str) -> Optional[Template]:
    """Get a template by name and endpoint type."""
    return db.query(Template).filter(
        Template.name == name,
        Template.endpoint_type == endpoint_type.lower()
    ).first()

def get_templates_by_type(db: Session, endpoint_type: str) -> List[Template]:
    """Get all templates for a specific endpoint type."""
    return db.query(Template).filter(
        Template.endpoint_type == endpoint_type.lower()
    ).all()

def update_template(db: Session, name: str, endpoint_type: str, body: Dict[str, Any]) -> Optional[Template]:
    """Update an existing template."""
    db_template = get_template_by_name_and_type(db, name, endpoint_type)
    if db_template:
        # The Template model's __init__ method already converts the body to a JSON string,
        # but we're updating an existing instance, so we need to do it manually here.
        # Check if the body is already a JSON string to avoid double-encoding
        if isinstance(body, dict):
            db_template.body = json.dumps(body)
        else:
            db_template.body = body
        db.commit()
        db.refresh(db_template)
    return db_template

def delete_template(db: Session, name: str, endpoint_type: str) -> bool:
    """Delete a template by name and endpoint type."""
    db_template = get_template_by_name_and_type(db, name, endpoint_type)
    if db_template:
        db.delete(db_template)
        db.commit()
        return True
    return False

def get_all_templates(db: Session) -> List[Template]:
    """Get all templates."""
    return db.query(Template).all()
