
from typing import Generic, TypeVar
from pydantic import BaseModel

__all__ = [
    "ResponseModel"    
]

T = TypeVar('T')


class ResponseModel(BaseModel,Generic[T]):
    msg: str
    detail: T