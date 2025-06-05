from typing import Annotated, Optional
import uuid
from pydantic import BaseModel, confloat
from utils.utils import TransactionType,TransactionStatus,PurchaseType

__all__ = [
    "Transaction",
    "TransactionCreateRequest",
    "TransactionResponse",
    "PurchaseRequest"
]

class Transaction(BaseModel):
    
    user_id: uuid.UUID
    project_id: Optional[uuid.UUID] = None
    wallet_id: uuid.UUID
    transaction_type: TransactionType
    purchase_type: Optional[PurchaseType] = None
    credit_amount: Annotated[float, confloat(gt=0)]
    price_paid: Annotated[float, confloat(gt=0)]
    price_per_credit: Optional[Annotated[float, confloat(gt=0)]] = None
    requested_credits: Optional[Annotated[float, confloat(gt=0)]] = None
    requested_budget: Optional[Annotated[float, confloat(gt=0)]] = None
    reference: Optional[str] = None

class TransactionCreateRequest(Transaction):
    pass

class PurchaseRequest(BaseModel):
    
    project_id: uuid.UUID
    amount: Annotated[float, confloat(gt=0)]
    purchase_type: PurchaseType


class TransactionResponse(Transaction):

    id: uuid.UUID
    status: TransactionStatus

    pass

    class Config:
        from_attributes = True


