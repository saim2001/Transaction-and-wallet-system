from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from  repository.user_repository import UserRepository 
from repository.wallet_repository import WalletRepository
from sqlalchemy.ext.asyncio import AsyncSession
from config.jwt_provider import hash_password,verify_password,create_access_token
from schema.user_schema import *
from schema.wallelt_schema import WalletCreateRequest
from utils.utils import UNIQUE_CONSTRAINT_MESSAGES

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session=session)
        self.wallet_repository = WalletRepository(session=session)

    async def create(
            self,
            data: UserCreateRequest
    ) -> UserResponse:
        """
        Create a new user record.
        
        :param data: UserCreateRequest object containing user data.
        :return: UserResponse object with the created user details.
        """
        try:
            # Hash the user's password before saving to the database
            data.password = hash_password(data.password)
            async with self.session.begin():
                # Create a new user record in the database
                user = await self.repository.create(obj_data=data,commit=False)
                await self.session.flush()
                wallet = WalletCreateRequest(user_id=user.id,balance=0.0)
                await self.wallet_repository.create(obj_data=wallet.model_dump(),commit=False)
            return UserResponse.model_validate(user)
        except IntegrityError as e:
            await self.session.rollback()
            for key, message in UNIQUE_CONSTRAINT_MESSAGES.items():
                if key in str(e.orig):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=message
                    )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Integrity error. Possibly duplicate data."
            )
        except Exception as e:
            await self.session.rollback()
            # Reraise any exceptions encountered during the process
            raise e
    
    async def sign_in(
            self,
            data: SignInRequest
    ) -> str:
        try:
            user = await self.repository.get_by_filter(
                filters=[
                    self.repository.model.email == data.email,
                    self.repository.model.is_active == True
                ]
            )
            
            if ((not user) or 
                (not verify_password(data.password, user.password))):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Incorrect email or passsword"
                )
            
            access_token = create_access_token(
                                data={"id": str(user.id)}
                            )
            
            return {"access_token": access_token, "token_type": "bearer"}
        except Exception as e:
            raise e

    
