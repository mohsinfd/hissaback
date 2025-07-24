import pytest
import uuid
from fastapi.testclient import TestClient
from app import app

# Test client
client = TestClient(app)

class TestUserJourney:
    """
    Test scenarios for Block 4: End-User Journey
    Complete user flow from smart link click to merchant redirect
    """

    def setup_method(self):
        """Setup test data before each test"""
        # Create unique identifiers for each test
        unique_suffix = str(uuid.uuid4().hex[:6])

        # Create a test tenant first
        self.test_signup = {
            "name": "Test Creator Journey",
            "email": f"journey{unique_suffix}@example.com",
            "phone": f"+9177{unique_suffix[:8]}",
            "brand_name": "Journey Test Brand"
        }

        signup_response = client.post("/v1/creators/signup", json=self.test_signup)
        assert signup_response.status_code == 200
        self.tenant_id = signup_response.json()["tenant_id"]

        # Create a test campaign
        campaign_data = {
            "tenant_id": self.tenant_id,
            "name": "User Journey Test Campaign",
            "share_pct": 50.0
        }

        campaign_response = client.post("/v1/campaigns", json=campaign_data)
        assert campaign_response.status_code == 200
        self.campaign_id = campaign_response.json()["campaign_id"]

        # Generate a smart link
        link_data = {
            "campaign_id": self.campaign_id,
            "offer_id": 1234
        }

        link_response = client.post("/v1/links", json=link_data)
        assert link_response.status_code == 200
        link_details = link_response.json()
        self.link_id = link_details["link_id"]
        self.slug = link_details["slug"]

    def test_smart_link_access_success(self):
        """Test that smart links serve the landing page correctly"""
        response = client.get(f"/go/{self.slug}")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        # In real test, would check HTML content contains expected elements

    def test_smart_link_not_found(self):
        """Test handling of invalid smart links"""
        response = client.get("/go/invalid-slug-that-does-not-exist")
        
        assert response.status_code == 404
        assert "Link not found" in response.json()["detail"]

    def test_enduser_otp_request_success(self):
        """Test successful OTP request for end users"""
        otp_request = {
            "phone": "+919876543210",
            "link_id": self.link_id
        }

        response = client.post("/v1/auth/enduser/otp/request", json=otp_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert data["message"] == "OTP sent successfully"
        
        # Store request_id for subsequent tests
        self.request_id = data["request_id"]

    def test_enduser_otp_request_invalid_link(self):
        """Test OTP request with invalid link_id"""
        otp_request = {
            "phone": "+919876543210",
            "link_id": "invalid_link_id"
        }

        response = client.post("/v1/auth/enduser/otp/request", json=otp_request)
        
        assert response.status_code == 404
        assert "Link not found" in response.json()["detail"]

    def test_enduser_otp_verify_success(self):
        """Test successful OTP verification"""
        # First request OTP
        otp_request = {
            "phone": "+919876543210",
            "link_id": self.link_id
        }
        
        otp_response = client.post("/v1/auth/enduser/otp/request", json=otp_request)
        assert otp_response.status_code == 200
        request_id = otp_response.json()["request_id"]

        # Then verify with correct OTP (mock OTP is always "123456")
        verify_request = {
            "request_id": request_id,
            "code": "123456",
            "link_id": self.link_id
        }

        response = client.post("/v1/auth/enduser/otp/verify", json=verify_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] == True
        assert "merchant_url" in data
        assert "Verification successful" in data["message"]
        assert "utm_source=hissaback" in data["merchant_url"]

    def test_enduser_otp_verify_wrong_code(self):
        """Test OTP verification with wrong code"""
        # First request OTP
        otp_request = {
            "phone": "+919876543210",
            "link_id": self.link_id
        }
        
        otp_response = client.post("/v1/auth/enduser/otp/request", json=otp_request)
        request_id = otp_response.json()["request_id"]

        # Try to verify with wrong OTP
        verify_request = {
            "request_id": request_id,
            "code": "999999",
            "link_id": self.link_id
        }

        response = client.post("/v1/auth/enduser/otp/verify", json=verify_request)
        
        assert response.status_code == 400
        assert "Invalid OTP" in response.json()["detail"]

    def test_enduser_otp_verify_invalid_request_id(self):
        """Test OTP verification with invalid request_id"""
        verify_request = {
            "request_id": "invalid_request_id",
            "code": "123456",
            "link_id": self.link_id
        }

        response = client.post("/v1/auth/enduser/otp/verify", json=verify_request)
        
        assert response.status_code == 400
        assert "Invalid request ID" in response.json()["detail"]

    def test_click_tracking_success(self):
        """Test successful click tracking"""
        click_request = {
            "link_id": self.link_id,
            "user_id": "user_123"
        }

        response = client.post("/v1/events/click", json=click_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "click_id" in data
        assert data["link_id"] == self.link_id
        assert data["user_id"] == "user_123"
        assert "timestamp" in data

    def test_click_tracking_without_user_id(self):
        """Test click tracking without user_id (anonymous)"""
        click_request = {
            "link_id": self.link_id
        }

        response = client.post("/v1/events/click", json=click_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "click_id" in data
        assert data["link_id"] == self.link_id
        assert data["user_id"] is None

    def test_click_tracking_invalid_link(self):
        """Test click tracking with invalid link_id"""
        click_request = {
            "link_id": "invalid_link_id"
        }

        response = client.post("/v1/events/click", json=click_request)
        
        assert response.status_code == 404
        assert "Link not found" in response.json()["detail"]

    def test_complete_user_journey_workflow(self):
        """Test the complete end-to-end user journey"""
        # 1. Access smart link (would serve landing page)
        link_response = client.get(f"/go/{self.slug}")
        assert link_response.status_code == 200

        # 2. Request OTP
        otp_request = {
            "phone": "+919876543210",
            "link_id": self.link_id
        }
        otp_response = client.post("/v1/auth/enduser/otp/request", json=otp_request)
        assert otp_response.status_code == 200
        request_id = otp_response.json()["request_id"]

        # 3. Verify OTP (successful verification)
        verify_request = {
            "request_id": request_id,
            "code": "123456",
            "link_id": self.link_id
        }
        verify_response = client.post("/v1/auth/enduser/otp/verify", json=verify_request)
        assert verify_response.status_code == 200
        merchant_url = verify_response.json()["merchant_url"]

        # 4. Track click (would happen via JavaScript)
        click_request = {
            "link_id": self.link_id,
            "user_id": "verified_user_123"
        }
        click_response = client.post("/v1/events/click", json=click_request)
        assert click_response.status_code == 200

        # Verify the flow created proper tracking data
        click_data = click_response.json()
        assert click_data["link_id"] == self.link_id
        assert "click_id" in click_data

        print(f"✅ Complete user journey test passed!")
        print(f"   Smart Link: /go/{self.slug}")
        print(f"   Merchant URL: {merchant_url}")
        print(f"   Click ID: {click_data['click_id']}")

    def test_user_journey_performance_metrics(self):
        """Test various performance and analytics scenarios"""
        test_phone = "+919876543210"
        
        # Simulate multiple users clicking the same link
        user_ids = ["user_001", "user_002", "user_003"]
        click_ids = []
        
        for user_id in user_ids:
            # Each user goes through OTP flow
            otp_request = {
                "phone": f"{test_phone[:-1]}{user_id[-1]}",  # Slightly different phones
                "link_id": self.link_id
            }
            otp_response = client.post("/v1/auth/enduser/otp/request", json=otp_request)
            assert otp_response.status_code == 200
            
            # Verify OTP
            verify_request = {
                "request_id": otp_response.json()["request_id"],
                "code": "123456",
                "link_id": self.link_id
            }
            verify_response = client.post("/v1/auth/enduser/otp/verify", json=verify_request)
            assert verify_response.status_code == 200
            
            # Track click
            click_request = {"link_id": self.link_id, "user_id": user_id}
            click_response = client.post("/v1/events/click", json=click_request)
            assert click_response.status_code == 200
            click_ids.append(click_response.json()["click_id"])
        
        # Verify we have multiple unique click IDs
        assert len(set(click_ids)) == 3
        
        print(f"✅ Performance test: {len(click_ids)} users successfully tracked")


if __name__ == "__main__":
    # Run individual tests for debugging
    test_instance = TestUserJourney()
    test_instance.setup_method()
    
    print("🧪 Running Block 4: User Journey Tests")
    
    try:
        test_instance.test_smart_link_access_success()
        print("✅ Smart link access test passed")
        
        test_instance.test_enduser_otp_request_success()
        print("✅ End-user OTP request test passed")
        
        test_instance.test_enduser_otp_verify_success()
        print("✅ End-user OTP verification test passed")
        
        test_instance.test_click_tracking_success()
        print("✅ Click tracking test passed")
        
        test_instance.test_complete_user_journey_workflow()
        print("✅ Complete user journey test passed")
        
        print("🎉 All Block 4 tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise 