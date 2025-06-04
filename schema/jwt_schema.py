
from typing import Optional
import uuid
from pydantic import BaseModel


__all__ = [
    "TokenData"    
]

class TokenData(BaseModel):
    id: Optional[uuid.UUID] = None