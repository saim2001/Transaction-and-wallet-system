
import uuid
from repository.wallet_repository import WalletRepository
from sqlalchemy.ext.asyncio import AsyncSession
from schema.wallelt_schema import *
class WalletService:
    def __init__(self, session: AsyncSession):
        self.session = session        
        self.repository = WalletRepository(session=session)

    async def add_balance(
            self,
            wallet_id: uuid.UUID,
            data: WalletUpdateRequest
    ) -> WalletResponse:
        try:
            wallet = self.repository.get_by_id(wallet_id=wallet_id)
            wallet.model.add_credits(session=self.session, amount=data.amount,updated_by=data.updated_by)
            return WalletResponse.model_validate(wallet)
        except Exception as e:
            raise e 
    