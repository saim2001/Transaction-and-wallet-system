from sqlalchemy import JSON, UUID, Boolean, Date, DateTime, ForeignKey, Numeric, text,Column, String, Integer, Float, Text
from config.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import uuid
from utils.utils import get_utc_now


class User(Base):

    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=True, default=get_utc_now, onupdate=get_utc_now)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    transactions = relationship("Transaction", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
