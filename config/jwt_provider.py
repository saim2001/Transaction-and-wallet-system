import os
import uuid
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from config.settings import settings
from schema.jwt_schema import TokenData
from config.database import get_db
from utils.utils import get_utc_now
from typing import List, Optional

# Import your User model (adjust path as needed)
from model.user import User  # Adjust import path based on your project structure


ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

security_scheme = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new access token
    
    Takes the input data and creates a new access token with the specified
    expiration time. If expires_delta is not specified, the token will expire
    after ACCESS_TOKEN_EXPIRE_MINUTES minutes.
    
    Args:
        data (dict): The data to encode into the token
        expires_delta (Optional[timedelta]): The time until the token expires
            If not specified, the token will expire after ACCESS_TOKEN_EXPIRE_MINUTES minutes
    
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = get_utc_now() + expires_delta
    else:
        # Default to ACCESS_TOKEN_EXPIRE_MINUTES minutes if expires_delta is not specified
        expire = get_utc_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credential_exception: HTTPException) -> TokenData:
    """
    Verify and decode an access token
    
    If the token is invalid, raise the provided credential_exception.
    If the token is valid, return a TokenData object with the user ID.
    """
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Get the user ID from the payload
        user_id: str = payload.get("id")
        
        # If the user ID is not specified, raise an error
        if user_id is None:
            raise credential_exception
        
        # Validate the UUID format
        try:
            uuid.UUID(user_id)
        except ValueError:
            # If the user ID is not a valid UUID, raise an error
            raise credential_exception
        
        # If the token is valid, return a TokenData object with the user ID
        token_data = TokenData(id=uuid.UUID(user_id))
        
    except JWTError:
        # If the token is invalid (e.g. expired, tampered with), raise an error
        raise credential_exception
    
    except ValueError:
        # If the token is invalid (e.g. malformed), raise an error
        raise credential_exception
    
    # If the token is valid, return the TokenData object
    return token_data

def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> uuid.UUID:
    """
    Get the current user ID from the token
    
    This function takes the token from the Authorization header and verifies it.
    If the token is invalid, it raises an HTTPException with a 401 status code.
    If the token is valid, it returns the user ID.
    """
    token = token.credentials
    
    # Raise an error if the token is invalid
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    
    # Verify the token and get the user ID
    token_verification = verify_access_token(token, credential_exception)
    return token_verification.id




async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    try:
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return None
            
        if not verify_password(password, user.password):
            return None
        
        return user
    except Exception:
        return None

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username, User.is_active == True).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email, User.is_active == True).first()

def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()

def create_reset_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a password reset token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Get reset token expiry from environment or use default (15 minutes)
        reset_minutes = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "15"))
        expire = datetime.now(timezone.utc) + timedelta(minutes=reset_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return email"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")  # Changed from "id" to "email" for clarity
        if email is None:
            return None
        return email
    except JWTError:
        return None

# Dependency to get current user object (not just ID)
async def get_current_user_object(
    db: AsyncSession = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user)
) -> User:
    """Get current user object with full details"""
    result = await db.execute(select(User).filter(User.id == current_user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user