"""
Unit tests for purchase endpoint
"""
import pytest
from main import app
from config.jwt_provider import get_current_user
from config.database import get_db
import uuid
from unittest.mock import AsyncMock, patch
from service.transaction_service import TransactionService
from tests.fixtures.purchase_fixtures import *


class TestPurchaseEndpoint:
    """Test class for purchase endpoint"""

    @pytest.mark.asyncio
    async def test_purchase_by_credit_success(
        self, 
        client, 
        mock_session, 
        mock_user, 
        mock_project, 
        mock_transaction,
        purchase_request_by_credit
    ):
        """Test successful purchase by credit"""

        # Patch dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user.id
        app.dependency_overrides[get_db] = lambda: mock_session
        
        with patch('config.jwt_provider.get_current_user', return_value=mock_user), \
                patch('config.database.get_db', return_value=mock_session), \
                patch('service.transaction_service.UserRepository') as MockUserRepo, \
                patch('service.transaction_service.ProjectRepository') as MockProjectRepo, \
                patch('service.transaction_service.TransactionRepository') as MockTransactionRepo:

            # Create the service manually and inject mocks
            service = TransactionService(session=mock_session)
            service.user_repository = MockUserRepo.return_value
            service.project_repository = MockProjectRepo.return_value
            service.repository = MockTransactionRepo.return_value

            # Set return values on the repo methods
            service.user_repository.get_by_id = AsyncMock(return_value=mock_user)
            service.project_repository.get_by_id = AsyncMock(return_value=mock_project)
            service.repository.create = AsyncMock(return_value=mock_transaction)
            
            # Make request
            response = client.post(
                "/api/v1/transaction/purchase/",
                json=purchase_request_by_credit,
                headers={"Authorization": "Bearer test_token"}
            )
            
            # Assertions
            assert response.status_code == 201
            response_data = response.json()
            assert response_data["msg"] == "Purchased Successfully"
            assert "detail" in response_data

    @pytest.mark.asyncio
    async def test_purchase_by_budget_success(
        self, 
        client, 
        mock_session, 
        mock_user, 
        mock_project, 
        mock_transaction,
        purchase_request_by_budget
    ):
        """Test successful purchase by budget"""
        
        # Patch dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user.id
        app.dependency_overrides[get_db] = lambda: mock_session
        
        with patch('config.jwt_provider.get_current_user', return_value=mock_user), \
                patch('config.database.get_db', return_value=mock_session), \
                patch('service.transaction_service.UserRepository') as MockUserRepo, \
                patch('service.transaction_service.ProjectRepository') as MockProjectRepo, \
                patch('service.transaction_service.TransactionRepository') as MockTransactionRepo:

            # Create the service manually and inject mocks
            service = TransactionService(session=mock_session)
            service.user_repository = MockUserRepo.return_value
            service.project_repository = MockProjectRepo.return_value
            service.repository = MockTransactionRepo.return_value

            # Set return values on the repo methods
            service.user_repository.get_by_id = AsyncMock(return_value=mock_user)
            service.project_repository.get_by_id = AsyncMock(return_value=mock_project)
            service.repository.create = AsyncMock(return_value=mock_transaction)
            
            # Make request
            response = client.post(
                "/api/v1/transaction/purchase/",
                json=purchase_request_by_budget,
                headers={"Authorization": "Bearer test_token"}
            )
            
            # Assertions
            assert response.status_code == 201
            response_data = response.json()
            assert response_data["msg"] == "Purchased Successfully"