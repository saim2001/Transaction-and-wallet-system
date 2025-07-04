from sqlalchemy import DECIMAL, UUID, Column, Enum, ForeignKey, Index, String
from .base_model import BaseModel
from sqlalchemy.orm import relationship
from utils.utils import get_utc_now,TransactionStatus,TransactionType,PurchaseType



class Transaction(BaseModel):
    """
    Transaction history for all credit movements
    Inherits: id, created_at, updated_at, is_active, created_by_id, updated_by_id
    """
    
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        doc="User involved in the transaction"
    )
    
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey('project.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        doc="Project involved in the transaction (nullable for topups)"
    )

    wallet_id = Column(
        UUID(as_uuid=True),
        ForeignKey('wallet.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        doc="Wallet involved in the transaction"
    )
    
    transaction_type = Column(
        Enum(TransactionType, name="transaction_type_enum"),
        nullable=False,
        index=True,
        doc="Type of transaction (TOPUP, PURCHASE, REFUND)"
    )

    purchase_type = Column(
                            Enum(
                                'BY_CREDIT', 
                                'BY_BUDGET',
                                native_enum=True,
                                name="purchase_type_enum"
                            ),
                            nullable=True
                        )

    credit_amount = Column(
        DECIMAL(precision=15, scale=2),
        nullable=False,
        doc="Amount of credits involved"
    )
    requested_credits = Column(
        DECIMAL(precision=15, scale=2),
        nullable=True,
    )
    requested_budget = Column(
        DECIMAL(precision=15, scale=2),
        nullable=True,
    )
    
    
    price_paid = Column(
        DECIMAL(precision=10, scale=2),
        nullable=True,
        doc="Price paid for the transaction (in USD)"
    )

    price_per_credit = Column(
        DECIMAL(precision=10, scale=2),
        nullable=True,
        doc="Price paid for the transaction (in USD)"
    )
    
    status = Column(
        Enum(TransactionStatus, name="transaction_status_enum"),
        default=TransactionStatus.PENDING,
        nullable=False,
        index=True,
        doc="Transaction status"
    )
    
    reference = Column(
        String(100),
        nullable=True,
        doc="External reference or note"
    )
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id],back_populates="transactions")
    project = relationship("Project", back_populates="transactions")
    wallet = relationship("Wallet", back_populates="transactions")
    created_by_user = relationship("User", foreign_keys="[Transaction.created_by]", back_populates="transactions_created")
    updated_by_user = relationship("User", foreign_keys="[Transaction.updated_by]", back_populates="transactions_updated")

    # Indexes
    __table_args__ = (
        Index('idx_transaction_user_type', 'user_id', 'transaction_type'),
        Index('idx_transaction_status_created', 'status', 'created_at'),
        Index('idx_transaction_project', 'project_id'),
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, type={self.transaction_type}, amount={self.credit_amount}, status={self.status})>"
    
    async def mark_completed(self, session, commit: bool = True):
        """
        Mark transaction as completed
        """
        self.status = TransactionStatus.COMPLETED
        self.updated_at = get_utc_now()
        
        if commit:
            await session.commit()
    
    async def mark_failed(self, session, commit: bool = True):
        """
        Mark transaction as failed
        """
        self.status = TransactionStatus.FAILED
        self.updated_at = get_utc_now()
        
        if commit:
            await session.commit()