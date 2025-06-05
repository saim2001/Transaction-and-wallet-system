from typing import Annotated
import uuid
from pydantic import BaseModel, confloat, constr
__all__ = [
    "ProjectCreateRequest",
    "ProjectResponse",
]

class Project(BaseModel):
    name: Annotated[str, constr(strip_whitespace=True, min_length=3, max_length=50)]
    description: Annotated[str, constr(strip_whitespace=True, min_length=3, max_length=500)]
    total_credits: Annotated[float, confloat(gt=0)]
    available_credits: Annotated[float, confloat(gt=0)]
    price_per_credit: Annotated[float, confloat(gt=0)]

class ProjectCreateRequest(Project):
    pass

class ProjectResponse(Project):
    id: uuid.UUID

    class Config:
        from_attributes = True