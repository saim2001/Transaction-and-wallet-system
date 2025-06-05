from typing import Annotated
import uuid
from fastapi import APIRouter, Depends
from schema.response_schema import ResponseModel
from schema.user_schema import *
from config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from service.project_service import ProjectService
from config.jwt_provider import get_current_user
from schema.project_schema import *



router = APIRouter(
    prefix="/project",
    tags=["Project"]
)

@router.post("/",status_code=201,response_model=ResponseModel[ProjectResponse])
async def create_project(
    data: ProjectCreateRequest,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db),
    ) -> ResponseModel[ProjectResponse]:

    try:
        service = ProjectService(session=session)
        data = await service.create(data=data,user_id=user_id)
        return ResponseModel[ProjectResponse](msg="Project Created Successfully",detail=data)
    except Exception as e:
        raise e