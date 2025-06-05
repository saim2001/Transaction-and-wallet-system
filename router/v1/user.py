from fastapi import APIRouter, Depends, Security
from fastapi.security import OAuth2PasswordRequestForm
from utils.utils import get_api_key,api_key_header
from schema.response_schema import ResponseModel
from schema.user_schema import *
from config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from service.user_service import UserService



router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.post("/",status_code=201,dependencies=[Depends(get_api_key)],response_model=ResponseModel[UserResponse])
async def create_user(
    data: UserCreateRequest,
    session: AsyncSession = Depends(get_db),
    ) -> ResponseModel[UserResponse]:

    try:
        service = UserService(session=session)
        data = await service.create(data=data)
        return ResponseModel[UserResponse](msg="User Created Successfully",detail=data)
    except Exception as e:
        raise e
    
@router.post("/sign-in",status_code=201,dependencies=[Depends(get_api_key)],response_model=ResponseModel[dict])
async def sign_in_user(
    data: SignInRequest,
    session: AsyncSession = Depends(get_db),
    ) -> ResponseModel[dict]:

    try:
        service = UserService(session=session)        
        data = await service.sign_in(data=data)
        return ResponseModel[dict](msg="Signed In Successfully",detail=data)
    except Exception as e:
        raise e
        