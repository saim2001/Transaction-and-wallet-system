from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, HTTPException
from schema.response_schema import ResponseModel
from schema.user_schema import *
from config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from service.transaction_service import TransactionService
from config.jwt_provider import get_current_user
from schema.transaction_schema import *



router = APIRouter(
    prefix="/transaction",
    tags=["Transaction"]
)

@router.post("/purchase/",status_code=201, description="""
    Perform a credit or budget-based purchase on a specific project.

    - `purchase_type` must be either `"BY_CREDIT"` or `"BY_BUDGET"`.
    - `amount` must be greater than zero.
    - `project_id` should be a valid UUID of the target project.

    This endpoint will return a transaction record after a successful purchase.
    """,response_model=ResponseModel[TransactionResponse])
async def purchase(
    data: PurchaseRequest,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db),
    ) -> ResponseModel[TransactionResponse]:

    try:
        service = TransactionService(session=session)
        return await service.purchase(data=data,user_id=user_id)
  
    except Exception as e:
        raise e