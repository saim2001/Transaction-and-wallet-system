from typing import Annotated
import uuid
from fastapi import APIRouter, Depends
from config.jwt_provider import get_current_user
from schema.response_schema import ResponseModel
from schema.wallelt_schema import *
from config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from service.wallet_service import WalletService
from schema.pagination_schema import PaginatedRequest,PaginatedResponse



router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"]
)

@router.put("/topup/{wallet_id}/",status_code=201,response_model=ResponseModel[WalletResponse])
async def sign_in_user(
    data: WalletUpdateRequest,
    wallet_id: uuid.UUID,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db),
    
    ) -> ResponseModel[WalletResponse]:

    try:
        service = WalletService(session=session)
        wallet_data = await service.add_balance(wallet_id=wallet_id, data=data,user_id=user_id)
        print(wallet_data)
        return ResponseModel[WalletResponse](msg="Credited Successfully",detail=wallet_data)
    except Exception as e:
        raise e
    
@router.get("/",status_code=200,response_model=WalletResponse)
async def get_wallet(
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db),
    
    ) -> WalletResponse:

    try:
        service = WalletService(session=session)
        wallet_data = await service.get_by_user(user_id = user_id)
        return wallet_data
    except Exception as e:
        raise e
    
    

    
        