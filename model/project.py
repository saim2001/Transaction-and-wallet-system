from decimal import Decimal
from sqlalchemy import DECIMAL, Column, Index, String, Text
from .base_model import BaseModel
from sqlalchemy.orm import relationship
from utils.utils import get_utc_now

class Project(BaseModel):
    """
    Environmental project that offers carbon offset credits
    Inherits: id, created_at, updated_at, is_active, created_by_id, updated_by_id
    """
    
    name = Column(
        String(255),
        nullable=False,
        doc="Project name"
    )
    
    description = Column(
        Text,
        doc="Detailed project description"
    )
    
    total_credits = Column(
        DECIMAL(precision=15, scale=2),
        default=Decimal('0.00'),
        nullable=False,
        doc="Total credits this project can offer"
    )
    
    available_credits = Column(
        DECIMAL(precision=15, scale=2),
        default=Decimal('0.00'),
        nullable=False,
        index=True,
        doc="Credits still available for purchase"
    )
    
    price_per_credit = Column(
        DECIMAL(precision=10, scale=2),
        default=Decimal('0.00'),
        nullable=False,
        doc="Price per credit in USD"
    )
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[BaseModel.created_by])
    updated_by_user = relationship("User", foreign_keys=[BaseModel.updated_by])
    transactions = relationship("Transaction", back_populates="project")
    
    # Indexes
    __table_args__ = (
        Index('idx_project_active_credits', 'is_active', 'available_credits'),
        Index('idx_project_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, available_credits={self.available_credits})>"
    
    def has_sufficient_credits(self, amount: Decimal) -> bool:
        """
        Check if project has enough credits for purchase
        """
        return self.available_credits >= amount
    
    def reserve_credits(self, session, amount: Decimal):
        """
        Reserve credits for purchase (atomic operation)
        """
        if not self.has_sufficient_credits(amount):
            raise ValueError(f"Insufficient credits. Available: {self.available_credits}, Requested: {amount}")
        
        self.available_credits -= amount
        self.updated_at = get_utc_now()
        session.commit()