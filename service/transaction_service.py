
from decimal import Decimal
from math import floor
import uuid
from fastapi import status
from utils.utils import PurchaseType,TransactionType,TransactionStatus
from fastapi.exceptions import HTTPException
from repository.transaction_repository import TransactionRepository
from repository.project_repository import ProjectRepository
from repository.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from schema.transaction_schema import *
class TransactionService:
    def __init__(self, session: AsyncSession):
        self.session = session        
        self.repository = TransactionRepository(session=session)
        self.project_repository = ProjectRepository(session=session)
        self.user_repository = UserRepository(session=session)

    async def purchase(
            self,
            user_id: uuid.UUID,
            data: PurchaseRequest
    ) -> TransactionResponse:
        try:
            requested_credit = None
            requested_bugdet = None
            purchase_type = None
            data.amount = Decimal(data.amount)
            
            
            async with self.session.begin():

                user = await self.user_repository.get_by_id(
                obj_id=user_id,
                relationships=["wallet"]
                )
                project = await self.project_repository.get_by_id(obj_id=data.project_id)

                if data.purchase_type.value == PurchaseType.BY_CREDIT.value:
                        
                        credits = data.amount
                        total_cost = credits * project.price_per_credit
                        requested_credit = credits
                        purchase_type = PurchaseType.BY_CREDIT

                if data.purchase_type.value == PurchaseType.BY_BUDGET.value:

                    if data.amount % project.price_per_credit != 0:
                        credits = Decimal(floor(data.amount / project.price_per_credit * 100) / 100)
                        actual_cost = credits * project.price_per_credit
                        refund = data.amount - actual_cost
                        total_cost = actual_cost
                        requested_bugdet = total_cost
                        purchase_type = PurchaseType.BY_BUDGET

                sufficient_credits = await project.has_sufficient_credits(
                    amount= Decimal(credits)
                )    
                if sufficient_credits == False:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Insufficient project credits"
                    )
                    
                sufficient_balance = await user.wallet.has_sufficient_balance(
                    amount= Decimal(total_cost)
                )
                if  sufficient_balance == False:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Insufficient wallet funds"
                    )

                await user.wallet.deduct_credits(
                    self.session,
                    Decimal(total_cost),
                    user_id,
                    False
                )

                await project.reserve_credits(
                    self.session,
                    Decimal(credits),
                    user_id,
                    False
                )

                transaction_data = TransactionCreateRequest(
                    user_id = user_id,
                    project_id=project.id,
                    wallet_id=user.wallet.id,
                    transaction_type = TransactionType.PURCHASE,
                    purchase_type= purchase_type,
                    credit_amount = credits,
                    price_paid = total_cost,
                    requested_credits=requested_credit,
                    requested_budget=requested_bugdet,
                    price_per_credit = project.price_per_credit,
                )

                transaction = await self.repository.create(
                    obj_data=transaction_data,
                    commit=False
                )
            

            return TransactionResponse.model_validate(transaction)

            
        except Exception as e:
            raise e 