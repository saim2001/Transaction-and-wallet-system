
from pydantic import BaseModel




class TokenData(BaseModel):
    id: Optional[uuid.UUID] = None