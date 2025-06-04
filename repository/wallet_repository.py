from sqlalchemy.ext.asyncio import AsyncSession
from model.wallet import Wallet
from .base_repository import BaseORM





class WalletRepository(BaseORM):
    def __init__(self, session: AsyncSession):        
        super().__init__(session, Wallet)