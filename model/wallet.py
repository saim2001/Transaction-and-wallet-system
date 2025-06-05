from decimal import Decimal
from sqlalchemy import DECIMAL, UUID, Column, ForeignKey, Index
from .base_model import BaseModel
from sqlalchemy.orm import relationship
from utils.utils import get_utc_now

class Wallet(BaseModel):
    """
    User's credit wallet
    Inherits: id, created_at, updated_at, is_active, created_by_id, updated_by_id
    """
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True,
        doc="User who owns this wallet"
    )
    
    balance = Column(
        DECIMAL(precision=15, scale=2),
        default=Decimal('0.00'),
        nullable=False,
        index=True,
        doc="Current credit balance"
    )
    
    # Relationships
    transactions = relationship("Transaction", back_populates="wallet")
    user = relationship("User", foreign_keys=[user_id],back_populates="wallet")
    created_by_user = relationship("User", foreign_keys="[Wallet.created_by]", back_populates="wallet_created")
    updated_by_user = relationship("User", foreign_keys="[Wallet.updated_by]", back_populates="wallet_updated")
    
    # Indexes
    __table_args__ = (
        Index('idx_wallet_user_active', 'user_id', 'is_active'),
        Index('idx_wallet_balance', 'balance'),
    )
    
    def __repr__(self):
        return f"<Wallet(id={self.id}, user_id={self.user_id}, balance={self.balance})>"
    
    async def add_credits(self, session, amount: Decimal,updated_by: UUID, commit: bool = True):
        """
        Add credits to wallet (atomic operation)
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        self.balance += amount
        self.updated_at = get_utc_now()
        self.updated_by = updated_by
        if commit == True:
            await session.commit()
    
    async def deduct_credits(self, session, amount: Decimal, updated_by: UUID,commit: bool = True):
        """
        Deduct credits from wallet (atomic operation)
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if self.balance < amount:
            raise ValueError(f"Insufficient balance. Available: {self.balance}, Requested: {amount}")
        
        self.balance -= amount
        self.updated_at = get_utc_now()
        self.updated_by = updated_by
        if commit == True:
            await session.commit()
    
    async def has_sufficient_balance(self, amount: Decimal) -> bool:
        """
        Check if wallet has sufficient balance
        """
        return self.balance >= amount

    async def credit_balance(self):
        """Calculate balance from transactions"""
        return sum(t.credit_amount for t in self.transactions if t.status == 'COMPLETED')
    
   
    async def total_invested(self):
        """Calculate total USD invested"""
        return sum(t.price_paid for t in self.transactions 
                  if t.transaction_type == 'PURCHASE' and t.status == 'COMPLETED')