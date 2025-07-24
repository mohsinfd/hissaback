import pytest
import json
from fastapi.testclient import TestClient
from app import app

# Test client
client = TestClient(app)

class TestCreatorOnboarding:
    """
    Test scenarios from tests/onboarding.test.md
    """
    
    def test_successful_signup_flow(self):
        """
        Scenario: Successful sign‑up
        Given valid details & OTP
        When user completes onboarding.flow
        Then JSON store `tenants` contains exactly one new object
        And event `creator.onboarded` is emitted
        """
        
        # Step 1: Request OTP
        otp_request = {
            "phone": "+919876543210"
        }
        otp_response = client.post("/v1/auth/otp/request", json=otp_request)
        assert otp_response.status_code == 200
        
        otp_data = otp_response.json()
        assert "request_id" in otp_data
        request_id = otp_data["request_id"]
        
        # Step 2: Verify OTP
        verify_request = {
            "request_id": request_id,
            "code": "123456"  # Mock OTP code
        }
        verify_response = client.post("/v1/auth/otp/verify", json=verify_request)
        assert verify_response.status_code == 200
        
        verify_data = verify_response.json()
        assert "jwt" in verify_data
        assert verify_data["phone"] == "+919876543210"
        
        # Step 3: Complete Creator Signup
        signup_request = {
            "name": "Test Creator",
            "email": "test@example.com",
            "phone": "+919876543210",
            "brand_name": "Test Brand"
        }
        
        signup_response = client.post("/v1/creators/signup", json=signup_request)
        assert signup_response.status_code == 200
        
        # Validate response structure
        signup_data = signup_response.json()
        assert "tenant_id" in signup_data
        assert "trackier_pid" in signup_data
        assert signup_data["name"] == "Test Creator"
        assert signup_data["default_share_pct"] == 40.0
        assert "api_key" in signup_data
        
        # Verify tenant was created in database
        tenant_id = signup_data["tenant_id"]
        tenant_response = client.get(f"/v1/tenants/{tenant_id}")
        assert tenant_response.status_code == 200
        
        tenant_data = tenant_response.json()
        assert tenant_data["tenant_id"] == tenant_id
        assert tenant_data["name"] == "Test Creator"
        assert tenant_data["phone"] == "+919876543210"
        assert tenant_data["status"] == "active"
    
    def test_duplicate_phone_rejection(self):
        """
        Scenario: Duplicate phone
        Given phone already exists
        When OTP verified
        Then flow aborts with message "Account already exists"
        """
        
        # First signup (should succeed)
        signup_request_1 = {
            "name": "First Creator",
            "email": "first@example.com", 
            "phone": "+919999999999",
            "brand_name": "First Brand"
        }
        
        first_response = client.post("/v1/creators/signup", json=signup_request_1)
        assert first_response.status_code == 200
        
        # Second signup with same phone (should fail)
        signup_request_2 = {
            "name": "Second Creator",
            "email": "second@example.com",
            "phone": "+919999999999",  # Same phone number
            "brand_name": "Second Brand"
        }
        
        second_response = client.post("/v1/creators/signup", json=signup_request_2)
        assert second_response.status_code == 400
        
        error_data = second_response.json()
        assert "Account already exists" in error_data["detail"]
    
    def test_invalid_otp_rejection(self):
        """
        Test OTP verification with wrong code
        """
        
        # Request OTP
        otp_request = {"phone": "+918888888888"}
        otp_response = client.post("/v1/auth/otp/request", json=otp_request)
        assert otp_response.status_code == 200
        
        request_id = otp_response.json()["request_id"]
        
        # Try with wrong OTP
        verify_request = {
            "request_id": request_id,
            "code": "999999"  # Wrong code
        }
        
        verify_response = client.post("/v1/auth/otp/verify", json=verify_request)
        assert verify_response.status_code == 400
        
        error_data = verify_response.json()
        assert "Invalid OTP code" in error_data["detail"]
    
    def test_api_health_endpoints(self):
        """
        Test basic API health and connectivity
        """
        
        # Test root endpoint
        root_response = client.get("/")
        assert root_response.status_code == 200
        assert "Hissaback Platform API" in root_response.json()["message"]
        
        # Test health check
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"
    
    def test_tenants_listing(self):
        """
        Test tenants listing endpoint
        """
        
        tenants_response = client.get("/v1/tenants")
        assert tenants_response.status_code == 200
        
        tenants_data = tenants_response.json()
        assert "tenants" in tenants_data
        assert "count" in tenants_data
        assert isinstance(tenants_data["tenants"], list)

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 