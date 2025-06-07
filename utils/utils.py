from datetime import datetime
import enum
from fastapi import Depends, HTTPException, Header, Security,status
from fastapi.security import APIKeyHeader
import pytz
from config.settings import settings


API_SECRET_KEY = settings.API_SECRET_KEY
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

UNIQUE_CONSTRAINT_MESSAGES = {
    "user_email_key": "A user with this email already exists.",
    "user_username_key": "This username is already taken.",
    "project_name_key": "A project with this name already exists.",
}
class TransactionType(str,enum.Enum):
    TOPUP = "TOPUP"
    PURCHASE = "PURCHASE"
    REFUND = "REFUND"


class PurchaseType(str,enum.Enum):

    BY_CREDIT = "BY_CREDIT"
    BY_BUDGET = "BY_BUDGET"
    


    
class TransactionStatus(str,enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

def get_utc_now():
    """
    Returns the current UTC time as a timezone-aware datetime object.
    """
    # This function returns the current UTC time
    return datetime.now(pytz.utc)


def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    """
    Verify the API key provided in the X-API-Key header.

    Args:
        api_key (str): The API key from the X-API-Key header

    Returns:
        str: The API key if it is valid

    Raises:
        HTTPException: 403 Forbidden if the API key is invalid
    """
   
    if api_key != API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate API key",
        )
    return api_key
