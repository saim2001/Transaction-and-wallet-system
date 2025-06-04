from datetime import datetime
from typing import Optional
from sqlalchemy import JSON, UUID, Boolean, Date, DateTime, ForeignKey, Numeric, text,Column, String, Integer, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declared_attr
import uuid
from config.database import Base
from utils.utils import get_utc_now

class BaseModel(Base):
    """
    Abstract base model containing common fields for all models
    
    Fields:
    - id: UUID primary key for better security and scalability
    - created_at: Timestamp when record was created
    - updated_at: Timestamp when record was last modified
    - is_active: Soft delete flag instead of hard deletion
    - created_by: ID of user who created the record (optional)
    - updated_by: ID of user who last updated the record (optional)
    """
    
    __abstract__ = True  # This makes it an abstract base class
    
    # Use UUID for primary key - more secure and scalable
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=text("gen_random_uuid()"),
        index=True,
        doc="Unique identifier for this record"
    )
    
    # Timestamp fields - automatically managed
    created_at = Column(
        DateTime(timezone=True),
        default=get_utc_now,
        nullable=False,
        doc="Timestamp when this record was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now,
        nullable=False,
        doc="Timestamp when this record was last updated"
    )
    
    # Soft delete functionality
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="Whether this record is active (soft delete)"
    )
    
    # Audit trail - who created/updated the record
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey('user.id', ondelete='SET NULL'),
        nullable=True,
        doc="ID of user who created this record"
    )
    
    updated_by = Column(
        UUID(as_uuid=True),
        ForeignKey('user.id', ondelete='SET NULL'),
        nullable=True,
        doc="ID of user who last updated this record"
    )

    @declared_attr
    def __tablename__(cls):
        """
        Auto-generate table name from class name
        Convert CamelCase to snake_case
        """
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
    
    def __repr__(self):
        """
        Default string representation
        Child classes can override this method
        """
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def soft_delete(self, session, deleted_by_id: Optional[uuid.UUID] = None):
        """
        Soft delete the record by setting is_active to False
        """
        self.is_active = False
        self.updated_at = get_utc_now()
        if deleted_by_id:
            self.updated_by = deleted_by_id
        session.commit()
    
    def restore(self, session, restored_by_id: Optional[uuid.UUID] = None):
        """
        Restore a soft-deleted record
        """
        self.is_active = True
        self.updated_at = get_utc_now()
        if restored_by_id:
            self.updated_by = restored_by_id
        session.commit()
    
    def to_dict(self):
        """
        Convert model instance to dictionary
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }