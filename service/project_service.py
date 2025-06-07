import uuid
from repository.project_repository import ProjectRepository
from schema.project_schema import *
from sqlalchemy.exc import IntegrityError
from utils.utils import UNIQUE_CONSTRAINT_MESSAGES
from fastapi import HTTPException, status
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
        
        """
        Create a new project record with the provided data.

        :param data: ProjectCreateRequest object containing project data
        :param user_id: UUID of the user who created the record
        :return: ProjectResponse object with the created project details
        """
        try:
            # Dump the data to a dictionary and add the created_by field
            data_dump = data.model_dump()
            data_dump["created_by"] = user_id
            
            # Create a new project record with the updated data
            project = await self.repository.create(obj_data=data_dump)
            
            # Return the created project details in a ProjectResponse object
            return ProjectResponse.model_validate(project)
        except IntegrityError as e:
            # Rollback the current transaction to prevent partial writes
            await self.session.rollback()
            
            # Check if the error is due to a unique constraint violation
            # and raise an HTTPException with a user-friendly error message
            for key, message in UNIQUE_CONSTRAINT_MESSAGES.items():
                if key in str(e.orig):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=message
                    )
            
            # If the error is not due to a unique constraint violation,
            # raise a generic HTTPException with a vague error message
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Integrity error. Possibly duplicate data."
            )
        except Exception as e:
            raise e
    