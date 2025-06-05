
from decimal import Decimal
import uuid
from fastapi.exceptions import HTTPException
from fastapi import status
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

                wallet_data = {
                    'id': wallet.id,
                    'user_id': wallet.user_id,
                    'balance': wallet.balance,
                    'created_at': wallet.created_at,
                    'updated_at': wallet.updated_at,
                    'is_active': wallet.is_active
                }
                
            return WalletResponse.model_validate(wallet_data)
        except Exception as e:
            raise e

    async def get_by_user(
    self,
    user_id: uuid.UUID  # Optional: for additional security to ensure user owns the wallet
    ) -> WalletResponse:
    
        try:
            # Build filters - include user_id for security if provided
            filters = []
            filters.append(self.repository.model.user_id == user_id)
            
            # Get the wallet record with transactions
            query = select(self.repository.model).filter(*filters).options(
                selectinload(self.repository.model.transactions)
            )
            
            result = await self.repository.db.execute(query)
            wallet = result.unique().scalars().first()
            
            if not wallet:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
            
            # Convert to response object with computed values
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
            
            return WalletResponse(**response_data)

        except Exception as e:
            raise e
            
            
