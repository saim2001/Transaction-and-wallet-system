from sqlalchemy import JSON, UUID, Boolean, Date, DateTime, ForeignKey, Numeric, text,Column, String, Integer, Float, Text
from config.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import uuid
from utils.utils import get_utc_now


class User(Base):

    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    username = Column(String(255), nullable=False,unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=True, default=get_utc_now, onupdate=get_utc_now)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    wallet = relationship("Wallet", foreign_keys="[Wallet.user_id]", back_populates="user", uselist=False)
    transactions = relationship("Transaction",foreign_keys="[Transaction.user_id]", back_populates="user")
    wallet_created = relationship("Wallet", foreign_keys="[Wallet.created_by]", back_populates="created_by_user", uselist=False)
    transactions_created = relationship("Transaction",foreign_keys="[Transaction.created_by]", back_populates="created_by_user")
    wallet_updated = relationship("Wallet", foreign_keys="[Wallet.updated_by]", back_populates="updated_by_user", uselist=False)
    transactions_updated = relationship("Transaction",foreign_keys="[Transaction.updated_by]", back_populates="updated_by_user")
    projects_created = relationship("Project", foreign_keys="[Project.created_by]", back_populates="created_by_user")
    projects_updated = relationship("Project", foreign_keys="[Project.updated_by]", back_populates="updated_by_user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
