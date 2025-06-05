from sqlalchemy.ext.asyncio import AsyncSession
from model.transaction import Transaction
from .base_repository import BaseORM



class TransactionRepository(BaseORM):
    def __init__(self, session: AsyncSession):        
        super().__init__(session, Transaction)