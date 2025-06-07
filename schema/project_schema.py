from typing import Annotated
import uuid
from pydantic import BaseModel, Field, StrictFloat, confloat, constr, field_validator
__all__ = [
    "ProjectCreateRequest",
    "ProjectResponse",
]

class Project(BaseModel):
    name: Annotated[str, constr(strip_whitespace=True, min_length=3, max_length=50)]
    description: Annotated[str, constr(strip_whitespace=True, min_length=3, max_length=500)]
    total_credits: Annotated[StrictFloat, Field(gt=0, description="Must be greater than 0")]
    available_credits: Annotated[StrictFloat, Field()]
    price_per_credit: Annotated[StrictFloat, Field(gt=0, description="Must be greater than 0")]
    

    @field_validator('available_credits', mode='after')
    def check_available_not_exceed_total(cls, v, info):
        total = info.data.get('total_credits')
        if total is not None and v > total:
            raise ValueError('available credits must not exceed total credits')
        return v

class ProjectCreateRequest(Project):
    pass

class ProjectResponse(Project):
    id: uuid.UUID

    class Config:
        from_attributes = True