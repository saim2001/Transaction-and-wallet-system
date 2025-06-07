"""
Purchase-specific test fixtures
"""
import pytest
import uuid
from decimal import Decimal
from unittest.mock import Mock


@pytest.fixture
def purchase_request_by_credit(mock_project):
    """Purchase request by credit"""
    return {
        "project_id": str(mock_project.id),
        "amount": 100.0,
        "purchase_type": "BY_CREDIT"
    }


@pytest.fixture
def purchase_request_by_budget(mock_project):
    """Purchase request by budget"""
    return {
        "project_id": str(mock_project.id),
        "amount": 10.0,
        "purchase_type": "BY_BUDGET"
    }


@pytest.fixture
def purchase_request_invalid_amount():
    """Purchase request with invalid amount"""
    return {
        "project_id": str(uuid.uuid4()),
        "amount": 0.0,
        "purchase_type": "BY_CREDIT"
    }


@pytest.fixture
def purchase_request_invalid_type():
    """Purchase request with invalid purchase type"""
    return {
        "project_id": str(uuid.uuid4()),
        "amount": 100.0,
        "purchase_type": "INVALID_TYPE"
    }


@pytest.fixture
def purchase_request_invalid_uuid():
    """Purchase request with invalid UUID"""
    return {
        "project_id": "invalid-uuid",
        "amount": 100.0,
        "purchase_type": "BY_CREDIT"
    }


@pytest.fixture
def mock_project_with_odd_price():
    """Mock project with price that creates remainder"""
    project = Mock()
    project.id = uuid.uuid4()
    project.price_per_credit = Decimal('0.33')
    project.has_sufficient_credits = lambda amount: True
    project.reserve_credits = lambda session, amount, user_id, commit: None
    return project