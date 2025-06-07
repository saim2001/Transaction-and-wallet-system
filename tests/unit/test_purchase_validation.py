"""
Unit tests for purchase endpoint validation
"""
import pytest
import uuid
from tests.fixtures.purchase_fixtures import *
from main import app
from config.jwt_provider import get_current_user
from config.database import get_db


class TestPurchaseValidation:
    """Test class for purchase endpoint validation"""

    @pytest.mark.asyncio
    async def test_purchase_invalid_amount(self, client, purchase_request_invalid_amount,mock_session, 
        mock_user):
        """Test purchase with invalid amount (zero or negative)"""


        app.dependency_overrides[get_current_user] = lambda: mock_user.id
        app.dependency_overrides[get_db] = lambda: mock_session
        
        response = client.post(
            "/api/v1/transaction/purchase/",
            json=purchase_request_invalid_amount,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should return validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_purchase_negative_amount(self, client):
        """Test purchase with negative amount"""
        
        purchase_request = {
            "project_id": str(uuid.uuid4()),
            "amount": -10.0,
            "purchase_type": "BY_CREDIT"
        }
        
        response = client.post(
            "/api/v1/transaction/purchase/",
            json=purchase_request,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should return validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_purchase_invalid_purchase_type(self, client, purchase_request_invalid_type):
        """Test purchase with invalid purchase type"""
        
        response = client.post(
            "/api/v1/transaction/purchase/",
            json=purchase_request_invalid_type,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should return validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_purchase_invalid_project_id(self, client, purchase_request_invalid_uuid):
        """Test purchase with invalid project ID format"""
        
       
        response = client.post(
            "/api/v1/transaction/purchase/",
            json=purchase_request_invalid_uuid,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should return validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_purchase_missing_fields(self, client):
        """Test purchase with missing required fields"""
        
        incomplete_request = {
            "amount": 100.0
            # Missing project_id and purchase_type
        }
        
        response = client.post(
            "/api/v1/transaction/purchase/",
            json=incomplete_request,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should return validation error
        assert response.status_code == 422