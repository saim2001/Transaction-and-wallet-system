from typing import List, Optional
import uuid
from pydantic import BaseModel, Field
from schema.transaction_schema import TransactionResponse

__all__ = [
    "WalletCreateRequest",
    "WalletResponse",
    "WalletUpdateRequest"
]

class WalletCreateRequest(BaseModel):

    user_id: uuid.UUID
    balance: float

class WalletUpdateRequest(BaseModel):

    balance: float

class WalletResponse(BaseModel):

    id: uuid.UUID
    user_id: uuid.UUID
    balance: float
     # Add computed fields
    credit_balance: Optional[float] = Field(default=None, description="Balance calculated from completed transactions")
    total_invested: Optional[float] = Field(default=None, description="Total USD invested from purchases")
    transactions: List[TransactionResponse]

    class Config:
        from_attributes = True 
    
