import pytest
from fastapi.testclient import TestClient
from app import app

# Test client
client = TestClient(app)

class TestCatalogueSync:
    """
    Test scenarios for Block 2: Catalogue Sync
    """
    
    def test_get_offers_endpoint(self):
        """
        Test offers endpoint returns valid data structure
        """
        response = client.get("/v1/offers")
        assert response.status_code == 200
        
        offers = response.json()
        assert isinstance(offers, list)
        
        # Validate offer structure if offers exist
        if offers:
            offer = offers[0]
            required_fields = ["offer_id", "brand", "category", "base_commission_pct", "cool_off_days", "status"]
            for field in required_fields:
                assert field in offer
                
            assert isinstance(offer["offer_id"], str)
            assert isinstance(offer["base_commission_pct"], (int, float))
            assert offer["status"] in ["active", "inactive"]
    
    def test_offers_filtering_by_category(self):
        """
        Test category filtering works correctly
        """
        # First, trigger a sync to populate offers
        sync_response = client.post("/v1/sync/offers")
        assert sync_response.status_code == 200
        
        # Test category filtering
        response = client.get("/v1/offers?category=E-commerce")
        assert response.status_code == 200
        
        offers = response.json()
        if offers:
            # All returned offers should be E-commerce category
            for offer in offers:
                assert offer["category"] == "E-commerce"
    
    def test_offers_limit_parameter(self):
        """
        Test limit parameter works correctly
        """
        # Trigger sync first
        sync_response = client.post("/v1/sync/offers")
        assert sync_response.status_code == 200
        
        # Test with limit
        response = client.get("/v1/offers?limit=2")
        assert response.status_code == 200
        
        offers = response.json()
        assert len(offers) <= 2
    
    def test_manual_sync_offers(self):
        """
        Test manual catalogue sync functionality
        """
        response = client.post("/v1/sync/offers")
        assert response.status_code == 200
        
        sync_result = response.json()
        
        # Validate sync response structure
        required_fields = ["status", "offers_processed", "added", "updated", "deactivated", "duration_seconds"]
        for field in required_fields:
            assert field in sync_result
        
        assert sync_result["status"] == "success"
        assert isinstance(sync_result["offers_processed"], int)
        assert isinstance(sync_result["duration_seconds"], (int, float))
        assert sync_result["offers_processed"] > 0  # Should have processed some offers
    
    def test_offers_stats_endpoint(self):
        """
        Test offers statistics endpoint
        """
        # First sync to populate data
        client.post("/v1/sync/offers")
        
        response = client.get("/v1/offers/stats")
        assert response.status_code == 200
        
        stats = response.json()
        required_fields = ["total_offers", "active_offers", "categories", "brands", "last_sync"]
        for field in required_fields:
            assert field in stats
        
        assert isinstance(stats["total_offers"], int)
        assert isinstance(stats["active_offers"], int)
        assert isinstance(stats["categories"], list)
        assert isinstance(stats["brands"], list)
        assert stats["active_offers"] <= stats["total_offers"]
    
    def test_sync_then_retrieve_workflow(self):
        """
        Test complete workflow: sync offers then retrieve them
        """
        # Step 1: Sync offers
        sync_response = client.post("/v1/sync/offers")
        assert sync_response.status_code == 200
        
        sync_data = sync_response.json()
        offers_processed = sync_data["offers_processed"]
        
        # Step 2: Retrieve offers
        offers_response = client.get("/v1/offers")
        assert offers_response.status_code == 200
        
        offers = offers_response.json()
        
        # Should have some offers after sync
        assert len(offers) > 0
        assert len(offers) <= offers_processed  # Some might be inactive
        
        # Step 3: Verify offer data quality
        for offer in offers:
            assert offer["offer_id"] > 0
            assert len(offer["brand"]) > 0
            assert offer["base_commission_pct"] > 0
            assert offer["cool_off_days"] > 0
    
    def test_category_diversity_after_sync(self):
        """
        Test that sync brings in offers from multiple categories
        """
        # Trigger sync
        client.post("/v1/sync/offers")
        
        # Get stats
        stats_response = client.get("/v1/offers/stats")
        stats = stats_response.json()
        
        # Should have multiple categories
        assert len(stats["categories"]) >= 2
        assert len(stats["brands"]) >= 2
        
        # Common categories should be present
        categories = [cat.lower() for cat in stats["categories"]]
        assert any("commerce" in cat or "fashion" in cat or "beauty" in cat for cat in categories)
    
    def test_offers_api_performance(self):
        """
        Test that offers API responds quickly (mock performance test)
        """
        import time
        
        # Sync first
        client.post("/v1/sync/offers")
        
        # Time the offers endpoint
        start_time = time.time()
        response = client.get("/v1/offers")
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Should respond in reasonable time (< 1 second for mock)
        response_time = end_time - start_time
        assert response_time < 1.0
    
    def test_integration_with_existing_offers(self):
        """
        Test that sync integrates with existing mock offers data
        """
        # Get initial offers count (from mock files)
        initial_response = client.get("/v1/offers")
        initial_count = len(initial_response.json())
        
        # Trigger sync (should add more offers)
        sync_response = client.post("/v1/sync/offers")
        sync_data = sync_response.json()
        
        # Get final offers count
        final_response = client.get("/v1/offers")
        final_count = len(final_response.json())
        
        # Should have added new offers or updated existing ones
        assert sync_data["offers_processed"] > 0
        assert final_count >= initial_count  # At least same number, possibly more

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 