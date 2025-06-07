"""
Global pytest configuration and fixtures
"""
import pytest
import uuid
import asyncio
from decimal import Decimal
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from utils.utils import PurchaseType, TransactionType, TransactionStatus


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_session():
    """Mock async session"""
    session = AsyncMock(spec=AsyncSession)
    session.begin.return_value.__aenter__ = AsyncMock()
    session.begin.return_value.__aexit__ = AsyncMock()
    return session


@pytest.fixture
def mock_user():
    """Mock user with wallet"""
    user = Mock()
    user.id = uuid.uuid4()
    user.wallet = Mock()
    user.wallet.id = uuid.uuid4()
    user.wallet.has_sufficient_balance = AsyncMock(return_value=True)
    user.wallet.deduct_credits = AsyncMock()
    return user


@pytest.fixture
def mock_project():
    """Mock project"""
    project = Mock()
    project.id = uuid.uuid4()
    project.price_per_credit = Decimal('0.10')
    project.has_sufficient_credits = AsyncMock(return_value=True)
    project.reserve_credits = AsyncMock()
    return project


@pytest.fixture
def mock_transaction():
    """Mock transaction"""
    transaction = Mock()
    transaction.id = uuid.uuid4()
    transaction.user_id = uuid.uuid4()
    transaction.project_id = uuid.uuid4()
    transaction.wallet_id = uuid.uuid4()
    transaction.transaction_type = TransactionType.PURCHASE
    transaction.purchase_type = PurchaseType.BY_CREDIT
    transaction.credit_amount = Decimal('100.00')
    transaction.price_paid = Decimal('10.00')
    transaction.price_per_credit = Decimal('0.10')
    transaction.status = TransactionStatus.COMPLETED
    transaction.requested_credits = 30.30
    transaction.requested_budget = 10.0
    transaction.reference = "ABC123"  # or any valid string
    return transaction


@pytest.fixture(autouse=True)
def mock_dependencies():
    """Auto-use fixture to mock common dependencies"""
    with patch('config.jwt_provider.get_current_user') as mock_get_user, \
         patch('config.database.get_db') as mock_get_db:
        
        mock_get_user.return_value = uuid.uuid4()
        mock_get_db.return_value = AsyncMock(spec=AsyncSession)
        
        yield {
            'get_current_user': mock_get_user,
            'get_db': mock_get_db
        }