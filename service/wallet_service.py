
from decimal import Decimal
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from schema.pagination_schema import PaginatedRequest,PaginatedResponse
from utils.utils import TransactionType
from repository.wallet_repository import WalletRepository
from repository.transaction_repository import TransactionRepository
from schema.transaction_schema import TransactionCreateRequest
from sqlalchemy.ext.asyncio import AsyncSession
from schema.wallelt_schema import *
class WalletService:
    def __init__(self, session: AsyncSession):
        self.session = session        
        self.repository = WalletRepository(session=session)
        self.transaction_repository = TransactionRepository(session=session)

    async def add_balance(
            self,
            wallet_id: uuid.UUID,
            user_id: uuid.UUID,
            data: WalletUpdateRequest
    ) -> WalletResponse:
        try:
            async with self.session.begin():
                wallet = await self.repository.get_by_id(obj_id=wallet_id)
                await wallet.add_credits(session=self.session, amount=Decimal(data.balance),updated_by=user_id,commit=False)
                transaction_data = TransactionCreateRequest(
                    user_id = user_id,
                    wallet_id=wallet.id,
                    transaction_type = TransactionType.TOPUP,
                    credit_amount = 0,
                    price_paid = data.balance,
                )

                await self.transaction_repository.create(
                    obj_data=transaction_data,
                    commit=False
                )
                
            return WalletResponse.model_validate(wallet)
        except Exception as e:
            raise e

    async def get_all(
            self,
            user_id: uuid.UUID,
            pagination: PaginatedRequest
    ) -> PaginatedResponse[WalletResponse]:
         
        try:
            
                # Get wallets without using response_model in repository
            filters = [self.repository.model.user_id == user_id]
            
            # Get raw records first
            query = select(self.repository.model).filter(*filters).options(
                selectinload(self.repository.model.transactions)
            )
            
            count_query = select(func.count(self.repository.model.id)).filter(*filters)
            count_result = await self.repository.db.execute(count_query)
            total_count = count_result.scalar()
            
            data_query = await self.repository.db.execute(
                query.offset(pagination.skip).limit(pagination.limit)
            )
            wallets = data_query.unique().scalars().all()
            
            # Convert to response objects with computed values
            wallet_responses = []
            for wallet in wallets:
                response_data = {
                    'id': wallet.id,
                    'user_id': wallet.user_id,
                    'balance': wallet.balance,
                    'created_at': wallet.created_at,
                    'updated_at': wallet.updated_at,
                    'is_active': wallet.is_active,
                    'credit_balance': await wallet.credit_balance(),
                    'total_invested': await wallet.total_invested(),
                    "transactions": wallet.transactions
                }
                wallet_responses.append(WalletResponse(**response_data))
            
            total_pages = (total_count + pagination.limit - 1) // pagination.limit
            
            return PaginatedResponse[WalletResponse](
                page=(pagination.skip // pagination.limit) + 1,
                page_size=pagination.limit,
                total_count=total_count,
                total_pages=total_pages,
                data=wallet_responses,
            )

        except Exception as e:
            raise e
            
            
            
