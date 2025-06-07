"""
Unit tests for purchase endpoint edge cases
"""
import pytest
import uuid
from decimal import Decimal
from main import app
from config.jwt_provider import get_current_user
from config.database import get_db
from unittest.mock import AsyncMock, Mock, patch
from service.transaction_service import TransactionService


class TestPurchaseEdgeCases:
    """Test class for purchase endpoint edge cases"""

    @pytest.mark.asyncio
    async def test_purchase_by_budget_with_remainder(
        self,
        client, 
        mock_session, 
        mock_user, 
        mock_transaction,
        mock_dependencies
    ):
        """Test purchase by budget that doesn't divide evenly"""
        
        # Patch dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user.id
        app.dependency_overrides[get_db] = lambda: mock_session

        mock_project = Mock()
        mock_project.id = uuid.uuid4()
        mock_project.price_per_credit = Decimal('0.33')
        mock_project.has_sufficient_credits = AsyncMock(return_value=True)
        mock_project.reserve_credits = AsyncMock()

        purchase_request = {
            "project_id": str(mock_project.id),
            "amount": 10.0,
            "purchase_type": "BY_BUDGET"
        }

        # Patch dependencies used inside the service
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

            response = client.post(
                "/api/v1/transaction/purchase/",
                json=purchase_request,
                headers={"Authorization": "Bearer test_token"}
            )

            print(response.json())

            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_purchase_with_very_small_amount(
        self, 
        client, 
        mock_session, 
        mock_user, 
        mock_project, 
        mock_transaction
    ):
        """Test purchase with very small decimal amount"""
        
        purchase_request = {
            "project_id": str(mock_project.id),
            "amount": 0.01,  # Very small amount
            "purchase_type": "BY_CREDIT"
        }
        
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
                json=purchase_request,
                headers={"Authorization": "Bearer test_token"}
            )
            
            # Assertions
            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_purchase_with_large_amount(
        self, 
        client, 
        mock_session, 
        mock_user, 
        mock_project, 
        mock_transaction
    ):
        """Test purchase with very large amount"""
        
        purchase_request = {
            "project_id": str(mock_project.id),
            "amount": 999999.99,  # Very large amount
            "purchase_type": "BY_CREDIT"
        }
        
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
                json=purchase_request,
                headers={"Authorization": "Bearer test_token"}
            )
            
            # Assertions
            assert response.status_code == 201