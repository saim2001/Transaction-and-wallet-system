from typing import List, TypeVar, Generic
from pydantic import BaseModel,UUID4,Field
from pydantic.generics import GenericModel
from typing import Optional

__all__ = [
    "PaginatedResponse",
    "PaginatedRequest"    
]

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    page: int
    page_size: int
    total_count: int
    total_pages: int
    data: List[T]

    class Config:
        from_attributes = True


class PaginatedRequest(BaseModel):
    """
    A Pydantic model for paginated requests with optional filters.
    """
    skip: int = Field(0, ge=0, description="Number of records to skip (offset)")
    limit: int = Field(10, le=15000, description="Number of records to return (max 100)")
    filter: Optional[str] = Field(None, description="Primary filter to apply to the results")
    filter_2: Optional[str] = Field(None, description="Secondary filter to apply to the results")    
    ifilter: Optional[int] = None    

    class Config:
        from_attributes = False  # ORM mode is typically for response models, not input models
    


# T = TypeVar("T", bound=BaseModel)

# class ResponseModel(GenericModel, Generic[T]):
#     data: T
#     message: str = "Success"
    
