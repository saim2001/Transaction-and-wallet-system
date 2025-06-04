import uuid
from fastapi import APIRouter, Depends
from config.jwt_provider import get_current_user
from schema.response_schema import ResponseModel
from schema.wallelt_schema import *
from config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from service.wallet_service import WalletService



router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"]
)

@router.put("/{wallet_id}",status_code=201,response_model=ResponseModel[WalletResponse])
async def sign_in_user(
    data: WalletUpdateRequest,
    wallet_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user),
    ) -> ResponseModel[WalletResponse]:

    try:
        service = WalletService(session=session)
        data = await service.add_balance(wallet_id=wallet_id, data=data)
        return ResponseModel[WalletResponse](msg="Credited Successfully",detail=data)
    except Exception as e:
        raise e
        