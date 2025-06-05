from sqlalchemy.ext.asyncio import AsyncSession
from model.project import Project
from .base_repository import BaseORM



class ProjectRepository(BaseORM):
    def __init__(self, session: AsyncSession):        
        super().__init__(session, Project)