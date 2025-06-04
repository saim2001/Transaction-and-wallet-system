from sqlalchemy.ext.asyncio import AsyncSession
from model.user import User
from .base_repository import BaseORM



class UserRepository(BaseORM):
    def __init__(self, session: AsyncSession):        
        super().__init__(session, User)