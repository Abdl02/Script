# models.py
from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.sql import func
from database import Base
import json

class Template(Base):
    """Database model for body templates."""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    endpoint_type = Column(String(100), nullable=False)
    body = Column(Text, nullable=False)  # JSON stored as text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __init__(self, name, endpoint_type, body):
        self.name = name
        self.endpoint_type = endpoint_type.lower()  # Normalize endpoint type
        self.body = json.dumps(body)  # Convert dict to JSON string

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "endpoint_type": self.endpoint_type,
            "body": json.loads(self.body),  # Convert JSON string back to dict
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
