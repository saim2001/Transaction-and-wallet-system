import uuid
from pydantic import BaseModel

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
    
