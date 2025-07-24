import pytest
import uuid
from fastapi.testclient import TestClient
from app import app

# Test client
client = TestClient(app)

class TestCampaignBuilder:
    """
    Test scenarios for Block 3: Campaign Builder
    """
    
    def setup_method(self):
        """Setup test data before each test"""
        # Create unique phone number for each test
        unique_suffix = str(uuid.uuid4().hex[:6])
        
        # Create a test tenant first
        self.test_signup = {
            "name": "Test Creator",
            "email": f"test{unique_suffix}@example.com",
            "phone": f"+9199{unique_suffix[:8]}",
            "brand_name": "Test Brand"
        }
        
        signup_response = client.post("/v1/creators/signup", json=self.test_signup)
        assert signup_response.status_code == 200
        
        self.tenant_data = signup_response.json()
        self.tenant_id = self.tenant_data["tenant_id"]
        
        # Sync offers to have available offers
        sync_response = client.post("/v1/sync/offers")
        assert sync_response.status_code == 200
    
    def test_create_campaign_success(self):
        """
        Test successful campaign creation
        """
        campaign_request = {
            "tenant_id": self.tenant_id,
            "name": "Summer Sale Campaign",
            "share_pct": 35.0
        }
        
        response = client.post("/v1/campaigns", json=campaign_request)
        assert response.status_code == 200
        
        campaign = response.json()
        
        # Validate campaign structure
        required_fields = ["campaign_id", "tenant_id", "name", "share_pct", "status", "created_at"]
        for field in required_fields:
            assert field in campaign
        
        assert campaign["tenant_id"] == self.tenant_id
        assert campaign["name"] == "Summer Sale Campaign"
        assert campaign["share_pct"] == 35.0
        assert campaign["status"] == "active"
        assert campaign["campaign_id"].startswith("camp_")
    
    def test_create_campaign_with_default_share_pct(self):
        """
        Test campaign creation uses tenant default share % when not specified
        """
        campaign_request = {
            "tenant_id": self.tenant_id,
            "name": "Default Share Campaign"
            # No share_pct specified
        }
        
        response = client.post("/v1/campaigns", json=campaign_request)
        assert response.status_code == 200
        
        campaign = response.json()
        assert campaign["share_pct"] == 40.0  # Tenant default
    
    def test_generate_smart_link_success(self):
        """
        Test successful smart link generation
        """
        # First create a campaign
        campaign_request = {
            "tenant_id": self.tenant_id,
            "name": "Link Test Campaign",
            "share_pct": 40.0
        }
        
        campaign_response = client.post("/v1/campaigns", json=campaign_request)
        campaign_id = campaign_response.json()["campaign_id"]
        
        # Get an available offer
        offers_response = client.get("/v1/offers?limit=1")
        offers = offers_response.json()
        assert len(offers) > 0
        offer_id = offers[0]["offer_id"]
        
        # Generate smart link
        link_request = {
            "campaign_id": campaign_id,
            "offer_id": offer_id
        }
        
        response = client.post("/v1/links", json=link_request)
        assert response.status_code == 200
        
        link = response.json()
        
        # Validate link structure
        required_fields = ["link_id", "campaign_id", "offer_id", "slug", "smart_link"]
        for field in required_fields:
            assert field in link
        
        assert link["campaign_id"] == campaign_id
        assert link["offer_id"] == offer_id
        assert link["link_id"].startswith("lnk_")
        assert "hissaback.app/go/" in link["smart_link"]
        assert link["slug"] in link["smart_link"]
    
    def test_creator_analytics_endpoint(self):
        """
        Test creator analytics endpoint
        """
        # Create some campaigns and links first
        campaign_request = {
            "tenant_id": self.tenant_id,
            "name": "Analytics Test Campaign",
            "share_pct": 45.0
        }
        
        campaign_response = client.post("/v1/campaigns", json=campaign_request)
        campaign_id = campaign_response.json()["campaign_id"]
        
        # Generate a link
        offers_response = client.get("/v1/offers?limit=1")
        offer_id = offers_response.json()[0]["offer_id"]
        
        link_request = {
            "campaign_id": campaign_id,
            "offer_id": offer_id
        }
        
        client.post("/v1/links", json=link_request)
        
        # Get analytics
        response = client.get(f"/v1/analytics/creator?tenant_id={self.tenant_id}&period=30d")
        assert response.status_code == 200
        
        analytics = response.json()
        
        # Validate analytics structure
        required_fields = ["clicks", "conversions", "earnings", "shared", "period"]
        for field in required_fields:
            assert field in analytics
        
        assert isinstance(analytics["clicks"], int)
        assert isinstance(analytics["conversions"], int)
        assert isinstance(analytics["earnings"], (int, float))
        assert isinstance(analytics["shared"], (int, float))
        assert analytics["period"] == "30d"
        
        # Basic validation: clicks >= conversions
        assert analytics["clicks"] >= analytics["conversions"]
        # Shared should be less than total earnings
        assert analytics["shared"] <= analytics["earnings"]
    
    def test_complete_campaign_builder_workflow(self):
        """
        Test complete workflow: Create campaign → Generate link → View analytics
        """
        # Step 1: Create campaign
        campaign_request = {
            "tenant_id": self.tenant_id,
            "name": "E-commerce Campaign",
            "share_pct": 50.0
        }
        
        campaign_response = client.post("/v1/campaigns", json=campaign_request)
        assert campaign_response.status_code == 200
        campaign = campaign_response.json()
        
        # Step 2: Get E-commerce offers
        offers_response = client.get("/v1/offers?category=E-commerce&limit=2")
        assert offers_response.status_code == 200
        offers = offers_response.json()
        assert len(offers) >= 1
        
        # Step 3: Generate links for offers
        generated_links = []
        for offer in offers[:2]:  # Generate max 2 links
            link_request = {
                "campaign_id": campaign["campaign_id"],
                "offer_id": offer["offer_id"]
            }
            
            link_response = client.post("/v1/links", json=link_request)
            assert link_response.status_code == 200
            generated_links.append(link_response.json())
        
        # Step 4: Verify links were created
        assert len(generated_links) >= 1
        for link in generated_links:
            assert link["campaign_id"] == campaign["campaign_id"]
            assert "hissaback.app/go/" in link["smart_link"]
        
        # Step 5: Check analytics reflect the activity
        analytics_response = client.get(f"/v1/analytics/creator?tenant_id={self.tenant_id}")
        assert analytics_response.status_code == 200
        
        analytics = analytics_response.json()
        
        # Should have some mock analytics data based on number of links
        assert analytics["clicks"] > 0
        assert analytics["conversions"] >= 0
        assert analytics["shared"] > 0  # Since share_pct is 50%

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 