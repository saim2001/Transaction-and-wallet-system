from datetime import datetime
import enum
import pytz


class TransactionType(str,enum.Enum):
    TOPUP = "TOPUP"
    PURCHASE = "PURCHASE"
    REFUND = "REFUND"
    
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
