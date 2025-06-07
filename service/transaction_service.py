
from decimal import Decimal
from math import floor
import uuid
from fastapi import status
from utils.utils import PurchaseType,TransactionType,TransactionStatus
from fastapi.exceptions import HTTPException
from schema.response_schema import ResponseModel
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
    ) -> ResponseModel[TransactionResponse]:
        """
        Method to purchase credits from a project
        """
        try:
            # Get the user and project
            async with self.session.begin():
                # Get the user
                user = await self.user_repository.get_by_id(
                    obj_id=user_id,
                    relationships=["wallet"]
                )

                if not user:
                    # Raise an error
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

                # Get the project
                project = await self.project_repository.get_by_id(obj_id=data.project_id)

                if not project:
                    # Raise an error
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

                # Initialize variables
                requested_credit = None
                requested_bugdet = None
                purchase_type = None
                data.amount = Decimal(data.amount)
                
                # Handle purchase by credit
                if data.purchase_type.value == PurchaseType.BY_CREDIT.value:
                    # Calculate the number of credits to be purchased
                    credits = data.amount
                    
                    # Calculate the total cost
                    total_cost = credits * project.price_per_credit
                    
                    # Set the purchase type
                    requested_credit = credits
                    purchase_type = PurchaseType.BY_CREDIT
                    
                # Handle purchase by budget
                if data.purchase_type.value == PurchaseType.BY_BUDGET.value:
                    
                    # Calculate credits in all cases
                    credits = data.amount / project.price_per_credit

                    # If not cleanly divisible, floor it to 2 decimal places
                    if data.amount % project.price_per_credit != 0:
                        credits = Decimal(floor(credits * 100) / 100)

                    # Calculate actual cost
                    actual_cost = credits * project.price_per_credit

                    # Calculate refund (optional, if needed)
                    refund = data.amount - actual_cost

                    # Set values
                    total_cost = actual_cost
                    requested_bugdet = total_cost
                    purchase_type = PurchaseType.BY_BUDGET

                
                # Check if the project has enough credits
                sufficient_credits = await project.has_sufficient_credits(
                    amount= Decimal(credits)
                )    
                if sufficient_credits == False:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Insufficient project credits"
                    )
                    
                # Check if the wallet has enough balance
                sufficient_balance = await user.wallet.has_sufficient_balance(
                    amount= Decimal(total_cost)
                )
                if  sufficient_balance == False:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Insufficient wallet funds"
                    )

                # Deduct credits from the wallet
                await user.wallet.deduct_credits(
                    self.session,
                    Decimal(total_cost),
                    user_id,
                    False
                )

                # Reserve credits for the project
                await project.reserve_credits(
                    self.session,
                    Decimal(credits),
                    user_id,
                    False
                )

                # Create the transaction
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
                    status = TransactionStatus.COMPLETED
                )

                transaction = await self.repository.create(
                    obj_data=transaction_data,
                    commit=False
                )

                # Commit the transaction
                await self.session.flush()

                return ResponseModel[TransactionResponse](
                        msg="Purchased Successfully",
                        detail=TransactionResponse.model_validate(transaction)
                    )
        except HTTPException as e :
            # Re-raise HTTP exceptions as-is
            raise e
        except Exception as e:
            # Log the exception if you have logging set up
            # logger.error(f"Unexpected error in purchase: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during purchase"
            )
        

        
