import uuid
from repository.project_repository import ProjectRepository
from schema.project_schema import *
from schema.response_schema import ResponseModel


class ProjectService:
    def __init__(self, session):
        self.session = session
        self.repository = ProjectRepository(session=session)

    async def create(
            self,
            data: ProjectCreateRequest,
            user_id: uuid.UUID
    ) -> ProjectResponse:
        data_dump = data.model_dump()
        data_dump["created_by"] = user_id
        project = await self.repository.create(obj_data=data_dump)
        return ProjectResponse.model_validate(project)
    