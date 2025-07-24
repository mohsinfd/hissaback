from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import uuid
import json
import os
import requests
from datetime import datetime, timedelta
import asyncio

# Initialize FastAPI app
app = FastAPI(
    title="Hissaback Platform API",
    description="""
# Hissaback Platform API Documentation

## Overview
Hissaback is an affiliate commission sharing platform that connects creators (publishers) with advertisers (brands) and manages commission sharing with end-users. Give your audience their hissa back.

## API Categories

### 🔐 **Authentication APIs**
APIs for user authentication and OTP verification for creators and end-users.

### 👥 **Creator APIs** 
APIs for creators (publishers) to manage their campaigns, view analytics, and track earnings.

### 🏢 **Admin APIs**
Internal administrative APIs for managing tenants, campaigns, and platform operations.

### 🔗 **Trackier Integration APIs**
APIs for syncing data with Trackier's affiliate network platform.

### 📊 **Analytics & Reporting APIs**
APIs for viewing performance metrics and generating reports.

### 🎯 **End-User APIs**
APIs for end-users to interact with smart links and earn rewards.

### 🔄 **Webhook & Event APIs**
APIs for processing clicks, conversions, and payout events.

## Quick Start
1. **Creators**: Use Creator APIs to manage campaigns and view earnings
2. **Admins**: Use Admin APIs to manage platform operations
3. **End-Users**: Use End-User APIs to interact with smart links
4. **Integrations**: Use Trackier APIs to sync external data

## Authentication
- **Creators**: JWT Bearer token required for creator-specific endpoints
- **Admins**: No authentication required (for demo purposes)
- **End-Users**: OTP-based authentication for reward claiming
""",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User authentication and OTP verification APIs"
        },
        {
            "name": "Creator APIs",
            "description": "APIs for creators to manage campaigns and view earnings"
        },
        {
            "name": "Admin APIs", 
            "description": "Internal administrative APIs for platform management"
        },
        {
            "name": "Trackier Integration",
            "description": "APIs for syncing data with Trackier affiliate network"
        },
        {
            "name": "Analytics",
            "description": "Performance metrics and reporting APIs"
        },
        {
            "name": "End-User APIs",
            "description": "APIs for end-users to interact with smart links"
        },
        {
            "name": "Events & Webhooks",
            "description": "Click tracking, conversion processing, and payout events"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# JWT Dependency for Creator Authentication
async def get_creator_tenant_id(authorization: str = Header(...)) -> str:
    """
    Extract tenant_id from JWT token for creator authentication
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    # For mock implementation, extract tenant_id from token
    # In production, this would decode and verify the JWT
    if token.startswith("mock_jwt_creator_"):
        # Extract tenant_id from the token format: mock_jwt_creator_<tenant_id>
        if "tnt_101" in token:
            return "tnt_101"
        elif "7fac09b7-dc03-47a7-8352-d805863f62d8" in token:
            return "tnt_b373c646"
        else:
            # Try to extract from the token or use a default
            return "tnt_101"  # Default for testing - use the actual tenant ID
    else:
        raise HTTPException(status_code=401, detail="Invalid JWT token")

# Data Models
class CreatorSignupRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    brand_name: Optional[str] = None

class OTPRequest(BaseModel):
    phone: str

class OTPVerifyRequest(BaseModel):
    request_id: str
    code: str

# Creator Dashboard Models
class CreatorLoginRequest(BaseModel):
    phone: str

class CreatorLoginVerifyRequest(BaseModel):
    request_id: str
    code: str

class CreatorStatsResponse(BaseModel):
    clicks_today: int
    conversions_today: int
    pending_payout: float
    period: str

class CreatorCampaignResponse(BaseModel):
    campaign_id: str
    name: str
    status: str
    created_at: str
    share_pct: float
    total_clicks: int
    total_conversions: int

class CreatorPayoutResponse(BaseModel):
    payout_id: str
    date: str
    amount: float
    status: str
    voucher_code: Optional[str] = None

class CreatorProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    theme_hex: Optional[str] = None

class BrandResponse(BaseModel):
    brand_id: str
    trackier_advertiser_id: str
    name: str
    logo_url: Optional[str] = None

class TenantResponse(BaseModel):
    tenant_id: str
    name: str
    trackier_pid: str
    default_share_pct: float
    api_key: str

class OfferResponse(BaseModel):
    offer_id: str
    trackier_campaign_id: str
    advertiser_id: str
    brand: str
    category: str
    base_commission_pct: float
    cool_off_days: int
    status: str
    exposed_via_api: bool = True

class SyncResponse(BaseModel):
    status: str
    offers_processed: int
    added: int
    updated: int
    deactivated: int
    duration_seconds: float

# Block 3: Campaign Builder Models
class CampaignCreateRequest(BaseModel):
    tenant_id: str
    name: str
    offer_id: Optional[str] = None
    share_pct: Optional[float] = None
    flat_reward_amount: Optional[float] = None
    reward_type: str = "PERCENT"  # PERCENT or FLAT

class CampaignResponse(BaseModel):
    campaign_id: str
    tenant_id: str
    name: str
    share_pct: float
    status: str
    created_at: str

class LinkCreateRequest(BaseModel):
    campaign_id: str
    offer_id: str

class LinkResponse(BaseModel):
    link_id: str
    campaign_id: str
    offer_id: str
    slug: str
    smart_link: str

class AnalyticsResponse(BaseModel):
    clicks: int
    conversions: int
    earnings: float
    shared: float
    period: str

# Block 4: End-User Journey Models
class EndUserOTPRequest(BaseModel):
    phone: str
    link_id: str

class EndUserOTPVerifyRequest(BaseModel):
    request_id: str
    code: str
    link_id: str

class ClickTrackingRequest(BaseModel):
    link_id: str
    user_id: Optional[str] = None

class ClickTrackingResponse(BaseModel):
    click_id: str
    link_id: str
    user_id: Optional[str]
    timestamp: str

class ConversionWebhookRequest(BaseModel):
    click_id: str
    offer_id: str
    sale_amount: float
    order_id: str
    status: str  # e.g. "approved", "pending", "rejected"

class LedgerEntry(BaseModel):
    ledger_id: str
    conv_id: str
    click_id: str
    link_id: str
    campaign_id: str
    offer_id: str
    user_id: str
    order_id: str
    sale_amount: float
    base_commission: float
    user_pct: float
    user_amount: float
    creator_amount: float
    status: str  # queued/confirmed/paid
    created_at: str
    cool_off_until: str

class PayoutEntry(BaseModel):
    payout_id: str
    user_id: str
    amount: float
    method: str
    voucher_code: str
    ts_paid: str
    ledger_ids: list

# Mock data storage (replace with real DB)
class MockDatabase:
    def __init__(self):
        self.tenants = []
        self.offers = []
        self.advertisers = []
        self.brands = []  # New brands table
        self.campaigns = []
        self.links = []
        self.clicks = []
        self.ledger = []  # Block 5: ledger support
        self.payouts = []  # Block 6: payout support
        self.otp_requests = {}
        self.load_mock_data()
    
    def load_mock_data(self):
        """Load existing mock data if available"""
        try:
            with open('Data/tenants.mock.json.txt', 'r') as f:
                existing_tenants = json.load(f)
                self.tenants = existing_tenants
        except FileNotFoundError:
            # Add default tenant for testing
            self.tenants = [
                {
                    "tenant_id": "tnt_101",
                    "name": "John's Tech Reviews",
                    "trackier_pid": "pid_123",
                    "default_share_pct": 60.0,
                    "api_key": "api_key_123",
                    "created_at": datetime.utcnow().isoformat(),
                    "featured_categories": [
                        "iPhone Deals", "Laptop Offers", "Audio Gear", "Smart TVs", "Wearables", "Gaming", "Home Appliances"
                    ],
                    "featured_offers": ["camp_1234", "camp_5678", "camp_9012", "camp_3456", "camp_7890", "camp_4321"]
                }
            ]
        
        try:
            with open('Data/offers.mock.json.txt', 'r') as f:
                existing_offers = json.load(f)
                # Convert to our full schema
                self.offers = [
                    {
                        "offer_id": str(offer["offer_id"]),  # Convert to string
                        "trackier_campaign_id": str(offer["offer_id"]),
                        "advertiser_id": f"adv_{offer['offer_id']}",
                        "brand": offer["brand"], 
                        "category": offer.get("category", "Electronics"),
                        "base_commission_pct": offer["commission_pct"],
                        "cool_off_days": 30,
                        "status": "active",
                        "exposed_via_api": True,
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }
                    for offer in existing_offers
                ]
        except FileNotFoundError:
            # Add dummy offers for demo
            self.offers = [
                {
                    "offer_id": "camp_1234",
                    "trackier_campaign_id": "camp_1234",
                    "advertiser_id": "adv_001",
                    "brand": "Flipkart",
                    "category": "iPhone Deals",
                    "base_commission_pct": 6.0,
                    "cool_off_days": 30,
                    "status": "active",
                    "exposed_via_api": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "offer_id": "camp_5678",
                    "trackier_campaign_id": "camp_5678", 
                    "advertiser_id": "adv_002",
                    "brand": "Amazon",
                    "category": "Laptop Offers",
                    "base_commission_pct": 5.0,
                    "cool_off_days": 30,
                    "status": "active",
                    "exposed_via_api": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "offer_id": "camp_9012",
                    "trackier_campaign_id": "camp_9012",
                    "advertiser_id": "adv_003", 
                    "brand": "Myntra",
                    "category": "Audio Gear",
                    "base_commission_pct": 8.0,
                    "cool_off_days": 30,
                    "status": "active",
                    "exposed_via_api": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "offer_id": "camp_3456",
                    "trackier_campaign_id": "camp_3456",
                    "advertiser_id": "adv_004",
                    "brand": "Swiggy",
                    "category": "Smart TVs",
                    "base_commission_pct": 4.0,
                    "cool_off_days": 30,
                    "status": "active",
                    "exposed_via_api": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "offer_id": "camp_7890",
                    "trackier_campaign_id": "camp_7890",
                    "advertiser_id": "adv_005",
                    "brand": "Croma",
                    "category": "Wearables",
                    "base_commission_pct": 7.0,
                    "cool_off_days": 30,
                    "status": "active",
                    "exposed_via_api": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "offer_id": "camp_4321",
                    "trackier_campaign_id": "camp_4321",
                    "advertiser_id": "adv_006",
                    "brand": "Reliance Digital",
                    "category": "Gaming",
                    "base_commission_pct": 6.5,
                    "cool_off_days": 30,
                    "status": "active",
                    "exposed_via_api": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "offer_id": "camp_6543",
                    "trackier_campaign_id": "camp_6543",
                    "advertiser_id": "adv_007",
                    "brand": "Boat",
                    "category": "Home Appliances",
                    "base_commission_pct": 5.5,
                    "cool_off_days": 30,
                    "status": "active",
                    "exposed_via_api": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            ]
        # Add mock brands
        self.brands = [
            {"brand_id": "adv_001", "trackier_advertiser_id": "adv_001", "name": "Flipkart", "logo_url": "https://logo.clearbit.com/flipkart.com"},
            {"brand_id": "adv_002", "trackier_advertiser_id": "adv_002", "name": "Amazon", "logo_url": "https://logo.clearbit.com/amazon.com"},
            {"brand_id": "adv_003", "trackier_advertiser_id": "adv_003", "name": "Myntra", "logo_url": "https://logo.clearbit.com/myntra.com"},
            {"brand_id": "adv_004", "trackier_advertiser_id": "adv_004", "name": "Swiggy", "logo_url": "https://logo.clearbit.com/swiggy.com"},
            {"brand_id": "adv_005", "trackier_advertiser_id": "adv_005", "name": "Croma", "logo_url": "https://logo.clearbit.com/croma.com"},
            {"brand_id": "adv_006", "trackier_advertiser_id": "adv_006", "name": "Reliance Digital", "logo_url": "https://logo.clearbit.com/reliancedigital.in"},
            {"brand_id": "adv_007", "trackier_advertiser_id": "adv_007", "name": "Boat", "logo_url": "https://logo.clearbit.com/boat-lifestyle.com"}
        ]
        # Add mock categories
        self.categories = [
            "iPhone Deals", "Laptop Offers", "Audio Gear", "Smart TVs", "Wearables", "Gaming", "Home Appliances"
        ]
        # Initialize other collections with empty arrays
        self.advertisers = []
        self.campaigns = []
        self.links = []
        self.clicks = []
        self.ledger = []
        self.payouts = []
    
    def save_tenant(self, tenant_data):
        """Save tenant data (mock persistence)"""
        self.tenants.append(tenant_data)
        return tenant_data
    
    def upsert_offer(self, offer_data):
        """Upsert offer data"""
        existing_idx = next(
            (i for i, offer in enumerate(self.offers) if offer["offer_id"] == offer_data["offer_id"]), 
            None
        )
        
        if existing_idx is not None:
            # Update existing
            self.offers[existing_idx].update(offer_data)
            self.offers[existing_idx]["updated_at"] = datetime.utcnow().isoformat()
            return "updated"
        else:
            # Add new
            offer_data["created_at"] = datetime.utcnow().isoformat()
            offer_data["updated_at"] = datetime.utcnow().isoformat()
            self.offers.append(offer_data)
            return "added"
    
    def get_offers(self, tenant_id: Optional[str] = None, category: Optional[str] = None, active_only: bool = True):
        """Get filtered offers"""
        filtered_offers = self.offers
        
        if active_only:
            filtered_offers = [o for o in filtered_offers if o.get("status") == "active"]
        
        if category:
            filtered_offers = [o for o in filtered_offers if o.get("category", "").lower() == category.lower()]
        
        return filtered_offers
    
    # Block 3: Campaign & Link Management
    def create_campaign(self, campaign_data):
        """Create new campaign"""
        campaign_data["created_at"] = datetime.utcnow().isoformat()
        campaign_data["status"] = "active"
        self.campaigns.append(campaign_data)
        return campaign_data
    
    def get_campaign(self, campaign_id: str):
        """Get campaign by ID"""
        return next((c for c in self.campaigns if c["campaign_id"] == campaign_id), None)
    
    def get_tenant_campaigns(self, tenant_id: str):
        """Get all campaigns for a tenant"""
        return [c for c in self.campaigns if c["tenant_id"] == tenant_id]
    
    def create_link(self, link_data):
        """Create new smart link"""
        link_data["created_at"] = datetime.utcnow().isoformat()
        self.links.append(link_data)
        return link_data
    
    def get_tenant_links(self, tenant_id: str):
        """Get all links for a tenant"""
        tenant_campaigns = [c["campaign_id"] for c in self.campaigns if c["tenant_id"] == tenant_id]
        return [l for l in self.links if l["campaign_id"] in tenant_campaigns]
    
    # Block 4: Click Tracking Methods
    def get_link_by_slug(self, slug: str):
        """Get link by slug for smart link resolution"""
        return next((l for l in self.links if l["slug"] == slug), None)
    
    def create_click(self, click_data):
        """Create new click tracking record"""
        click_data["click_id"] = f"click_{len(self.clicks) + 1}"
        click_data["created_at"] = datetime.utcnow().isoformat()
        self.clicks.append(click_data)
        return click_data

    def create_ledger_entry(self, ledger_data):
        ledger_data["ledger_id"] = f"led_{len(self.ledger) + 1}"
        ledger_data["created_at"] = datetime.utcnow().isoformat()
        self.ledger.append(ledger_data)
        return ledger_data

    def create_payout(self, payout_data):
        payout_data["payout_id"] = f"payout_{len(self.payouts) + 1}"
        payout_data["ts_paid"] = datetime.utcnow().isoformat()
        self.payouts.append(payout_data)
        return payout_data
    def get_user_payouts(self, user_id):
        return [p for p in self.payouts if p["user_id"] == user_id]
    
    def upsert_advertiser(self, advertiser_data):
        """Add or update an advertiser (brand)"""
        advertiser_id = advertiser_data["advertiser_id"]
        
        # Check if advertiser already exists
        existing_advertiser = next((a for a in self.advertisers if a["advertiser_id"] == advertiser_id), None)
        
        if existing_advertiser:
            # Update existing advertiser
            existing_advertiser.update(advertiser_data)
            return "updated"
        else:
            # Add new advertiser
            self.advertisers.append(advertiser_data)
            return "added"

    def upsert_brand(self, brand_data):
        """Add or update a brand"""
        brand_id = brand_data["brand_id"]
        
        # Check if brand already exists
        existing_brand = next((b for b in self.brands if b["brand_id"] == brand_id), None)
        
        if existing_brand:
            # Update existing brand
            existing_brand.update(brand_data)
            return "updated"
        else:
            # Add new brand
            self.brands.append(brand_data)
            return "added"

# Global mock database instance
db = MockDatabase()

class TrackierClient:
    """Real Trackier API client with proper endpoints"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.trackier.com/v2"  # Updated to v2
    
    async def get_publishers(self) -> List[Dict[str, Any]]:
        """Get all publishers (creators) from Trackier"""
        # Real Trackier endpoint: GET /v2/publishers
        await asyncio.sleep(0.5)  # Simulate API delay
        
        return [
            {
                "id": "pub_123456",
                "name": "Tech Influencer",
                "email": "tech@example.com",
                "status": "active"
            },
            {
                "id": "pub_789012", 
                "name": "Fashion Blogger",
                "email": "fashion@example.com",
                "status": "active"
            }
        ]
    
    async def get_advertisers(self) -> List[Dict[str, Any]]:
        """Get all advertisers (brands) from Trackier"""
        # Real Trackier endpoint: GET /v2/advertisers
        await asyncio.sleep(0.5)
        
        return [
            {
                "id": "adv_001",
                "name": "Flipkart",
                "category": "E-commerce",
                "status": "active"
            },
            {
                "id": "adv_002",
                "name": "Amazon",
                "category": "E-commerce", 
                "status": "active"
            },
            {
                "id": "adv_003",
                "name": "Myntra",
                "category": "Fashion",
                "status": "active"
            },
            {
                "id": "adv_004",
                "name": "Nykaa",
                "category": "Beauty",
                "status": "active"
            }
        ]
    
    async def get_campaigns(self, advertiser_id: Optional[str] = None, publisher_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get campaigns (offers) from Trackier"""
        # Real Trackier endpoint: GET /v2/campaigns?advertiser_id={id}&publisher_id={id}
        await asyncio.sleep(0.5)
        
        campaigns = [
            {
                "id": "camp_1234",
                "advertiser_id": "adv_001",
                "advertiser_name": "Flipkart",
                "name": "Electronics Sale",
                "category": "E-commerce",
                "payout": {"amount": 6.0, "currency": "USD"},
                "status": "active",
                "preview_url": "https://dl.flipkart.com/dl/electronics"
            },
            {
                "id": "camp_5678",
                "advertiser_id": "adv_002", 
                "advertiser_name": "Amazon",
                "name": "Prime Day Deals",
                "category": "E-commerce",
                "payout": {"amount": 5.0, "currency": "USD"},
                "status": "active",
                "preview_url": "https://amazon.in/prime"
            },
            {
                "id": "camp_9999",
                "advertiser_id": "adv_003",
                "advertiser_name": "Myntra",
                "name": "Fashion Collection",
                "category": "Fashion", 
                "payout": {"amount": 8.0, "currency": "USD"},
                "status": "active",
                "preview_url": "https://myntra.com/collection"
            },
            {
                "id": "camp_7777",
                "advertiser_id": "adv_004",
                "advertiser_name": "Nykaa",
                "name": "Beauty Essentials",
                "category": "Beauty",
                "payout": {"amount": 12.0, "currency": "USD"},
                "status": "active",
                "preview_url": "https://nykaa.com/essentials"
            }
        ]
        
        # Filter by advertiser_id if provided
        if advertiser_id:
            campaigns = [c for c in campaigns if c["advertiser_id"] == advertiser_id]
            
        return campaigns

# Updated Catalogue Service with Trackier terminology
class CatalogueService:
    def __init__(self, db: MockDatabase):
        self.db = db
        self.trackier_client = TrackierClient("mock_api_key")
    
    async def sync_advertisers(self) -> Dict[str, Any]:
        """Sync advertisers (brands) from Trackier"""
        try:
            advertisers = await self.trackier_client.get_advertisers()
            
            # Store advertisers in our database
            for advertiser in advertisers:
                self.db.upsert_advertiser({
                    "advertiser_id": advertiser["id"],
                    "name": advertiser["name"],
                    "category": advertiser["category"],
                    "status": advertiser["status"]
                })
            
            return {
                "status": "success",
                "advertisers_processed": len(advertisers),
                "message": f"Synced {len(advertisers)} advertisers from Trackier"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to sync advertisers: {str(e)}"
            }
    
    async def sync_campaigns(self, advertiser_id: Optional[str] = None) -> Dict[str, Any]:
        """Sync campaigns (offers) from Trackier"""
        try:
            campaigns = await self.trackier_client.get_campaigns(advertiser_id=advertiser_id)
            
            stats = {"added": 0, "updated": 0, "deactivated": 0}
            
            for campaign in campaigns:
                offer_data = {
                    "offer_id": campaign["id"],
                    "advertiser_id": campaign["advertiser_id"],
                    "advertiser_name": campaign["advertiser_name"],
                    "brand": campaign["advertiser_name"],  # Keep for backward compatibility
                    "category": campaign["category"],
                    "base_commission_pct": campaign["payout"]["amount"],
                    "cool_off_days": 30,
                    "status": "active" if campaign["status"] == "active" else "inactive",
                    "preview_url": campaign.get("preview_url", "")
                }
                
                result = self.db.upsert_offer(offer_data)
                stats[result] += 1
            
            return {
                "status": "success",
                "campaigns_processed": len(campaigns),
                "added": stats["added"],
                "updated": stats["updated"],
                "deactivated": stats["deactivated"],
                "message": f"Synced {len(campaigns)} campaigns from Trackier"
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to sync campaigns: {str(e)}"
            }
    
    async def get_available_campaigns(self, publisher_id: str) -> List[Dict[str, Any]]:
        """Get campaigns available for a specific publisher"""
        try:
            campaigns = await self.trackier_client.get_campaigns(publisher_id=publisher_id)
            return campaigns
        except Exception as e:
            return []

# Block 3: Campaign Builder Service
class CampaignBuilderService:
    def __init__(self, db: MockDatabase):
        self.db = db
    
    def create_campaign(self, tenant_id: str, name: str, share_pct: Optional[float] = None) -> CampaignResponse:
        """Create new campaign"""
        # Validate tenant exists
        tenant = next((t for t in self.db.tenants if t["tenant_id"] == tenant_id), None)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Use tenant default share % if not provided
        if share_pct is None:
            share_pct = tenant.get("default_share_pct", 40.0)
        
        # Validate share percentage
        if not (10 <= share_pct <= 90):
            raise HTTPException(status_code=400, detail="Share percentage must be between 10% and 90%")
        
        # Generate campaign
        campaign_id = f"camp_{uuid.uuid4().hex[:8]}"
        
        campaign_data = {
            "campaign_id": campaign_id,
            "tenant_id": tenant_id,
            "name": name,
            "share_pct": share_pct
        }
        
        saved_campaign = self.db.create_campaign(campaign_data)
        
        return CampaignResponse(
            campaign_id=campaign_id,
            tenant_id=tenant_id,
            name=name,
            share_pct=share_pct,
            status="active",
            created_at=saved_campaign["created_at"]
        )
    
    def generate_smart_link(self, campaign_id: str, offer_id: str) -> LinkResponse:
        """Generate smart link for campaign + offer using Trackier format"""
        # Validate campaign exists
        campaign = self.db.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Validate offer exists
        offer = next((o for o in self.db.offers if o["offer_id"] == offer_id), None)
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")
        
        # Generate link
        link_id = f"lnk_{uuid.uuid4().hex[:8]}"
        slug = f"{campaign['name'].lower().replace(' ', '-')}-{offer['brand'].lower()}-{link_id[:6]}"
        
                # Create smart link URL with Trackier macros
        # Format: https://hissaback.app/?publisher_id={publisherId}&campaign_id={campaignId}&trackier_link=1
        smart_link = f"https://hissaback.app/go/{slug}?publisher_id={campaign['tenant_id']}&campaign_id={campaign_id}&trackier_link=1&click_id={{click_id}}"
        
        link_data = {
            "link_id": link_id,
            "campaign_id": campaign_id,
            "offer_id": offer_id,
            "slug": slug,
            "smart_link": smart_link
        }
        
        saved_link = self.db.create_link(link_data)
        
        return LinkResponse(
            link_id=link_id,
            campaign_id=campaign_id,
            offer_id=offer_id,
            slug=slug,
            smart_link=smart_link
        )
    
    def get_tenant_analytics(self, tenant_id: str, period: str = "30d") -> AnalyticsResponse:
        """Get basic analytics for tenant"""
        # Mock analytics data for now
        # In real implementation, would query clicks/conversions tables
        
        tenant_links = self.db.get_tenant_links(tenant_id)
        num_links = len(tenant_links)
        
        # Generate realistic mock data based on number of links
        mock_clicks = num_links * 45  # Average 45 clicks per link
        mock_conversions = int(mock_clicks * 0.12)  # 12% conversion rate
        mock_earnings = mock_conversions * 25.50  # Average ₹25.50 per conversion
        
        # Calculate earnings split
        campaigns = self.db.get_tenant_campaigns(tenant_id)
        avg_share_pct = sum(c["share_pct"] for c in campaigns) / len(campaigns) if campaigns else 40.0
        mock_shared = mock_earnings * (avg_share_pct / 100)
        
        return AnalyticsResponse(
            clicks=mock_clicks,
            conversions=mock_conversions,
            earnings=round(mock_earnings, 2),
            shared=round(mock_shared, 2),
            period=period
        )

# Initialize services
catalogue_service = CatalogueService(db)
campaign_builder = CampaignBuilderService(db)

# Frontend Routes
@app.get("/")
async def serve_frontend():
    """Serve the main landing page - Complete Interface Repository"""
    return FileResponse('static/landing.html')

@app.get("/creator_dashboard.html")
async def serve_creator_dashboard():
    """Serve the creator dashboard frontend"""
    return FileResponse('static/creator_dashboard.html')

@app.get("/creator_login.html")
async def serve_creator_login():
    """Serve the creator login page"""
    return FileResponse('static/creator_login.html')

@app.get("/admin_dashboard.html")
async def serve_admin_dashboard():
    """Serve admin dashboard page"""
    return FileResponse('static/admin_dashboard.html')

@app.get("/api_docs.html")
async def serve_api_docs():
    """Serve comprehensive API documentation page"""
    return FileResponse('static/api_docs.html')

# Endpoints

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/v1/auth/otp/request", tags=["Authentication"])
async def request_otp(request: OTPRequest):
    """
    Step 3 from onboarding.flow.md: Verify Phone
    Call /otp/request; on success, /otp/verify
    """
    # Mock OTP generation (replace with real SMS service)
    request_id = str(uuid.uuid4())
    mock_otp = "123456"  # In production, generate random OTP
    
    # Store OTP request (mock storage)
    db.otp_requests[request_id] = {
        "phone": request.phone,
        "otp": mock_otp,
        "created_at": datetime.utcnow().isoformat(),
        "verified": False
    }
    
    # In production: Send SMS via provider (Twilio, etc.)
    print(f"Mock SMS to {request.phone}: Your OTP is {mock_otp}")
    
    return {"request_id": request_id, "message": "OTP sent successfully"}

@app.post("/v1/auth/otp/verify", tags=["Authentication"])
async def verify_otp(request: OTPVerifyRequest):
    """
    Step 3 continuation: Verify the OTP code
    """
    # Check if request_id exists
    if request.request_id not in db.otp_requests:
        raise HTTPException(status_code=400, detail="Invalid request ID")
    
    otp_data = db.otp_requests[request.request_id]
    
    # Verify OTP code
    if otp_data["otp"] != request.code:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    
    # Mark as verified
    otp_data["verified"] = True
    
    # Generate JWT token (mock implementation)
    jwt_token = f"mock_jwt_{request.request_id}"
    
    return {
        "jwt": jwt_token,
        "phone": otp_data["phone"],
        "message": "OTP verified successfully"
    }

# Creator Authentication Endpoints
@app.post("/v1/auth/creator/login", tags=["Authentication"])
async def creator_login(request: CreatorLoginRequest):
    """
    Creator login: Request OTP for existing creator
    """
    # Check if creator exists
    creator = next(
        (t for t in db.tenants if t.get("phone") == request.phone), 
        None
    )
    if not creator:
        raise HTTPException(
            status_code=404, 
            detail="Creator account not found. Please sign up first."
        )
    
    # Generate OTP request
    request_id = str(uuid.uuid4())
    mock_otp = "123456"  # In production, generate random OTP
    
    # Store OTP request with creator context
    db.otp_requests[request_id] = {
        "phone": request.phone,
        "otp": mock_otp,
        "created_at": datetime.utcnow().isoformat(),
        "verified": False,
        "role": "creator",
        "tenant_id": creator["tenant_id"]
    }
    
    # In production: Send SMS via provider
    print(f"📱 Creator login OTP to {request.phone}: {mock_otp}")
    
    return {"request_id": request_id, "message": "OTP sent successfully"}

@app.post("/v1/auth/creator/verify", tags=["Authentication"])
async def creator_login_verify(request: CreatorLoginVerifyRequest):
    """
    Creator login: Verify OTP and return JWT with creator role
    """
    # Check if request_id exists
    if request.request_id not in db.otp_requests:
        raise HTTPException(status_code=400, detail="Invalid request ID")
    
    otp_data = db.otp_requests[request.request_id]
    
    # Verify OTP code
    if otp_data["otp"] != request.code:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    
    # Mark as verified
    otp_data["verified"] = True
    
    # Generate JWT token with creator role
    jwt_token = f"mock_jwt_creator_{request.request_id}"
    
    # Get creator details
    creator = next(
        (t for t in db.tenants if t.get("phone") == otp_data["phone"]), 
        None
    )
    
    return {
        "jwt": jwt_token,
        "role": "creator",
        "tenant_id": creator["tenant_id"],
        "name": creator["name"],
        "phone": otp_data["phone"],
        "message": "Creator login successful"
    }

@app.post("/v1/creators/signup", response_model=TenantResponse, tags=["Creator APIs"])
async def creator_signup(signup_data: CreatorSignupRequest):
    """
    Steps 4-6 from onboarding.flow.md:
    - Create Tenant → return tenant_id
    - Map Trackier PID → Auto-increment or existing
    - Pick Default Share % → Store on tenant
    """
    
    # Check for duplicate phone (Scenario: Duplicate phone test)
    existing_tenant = next(
        (t for t in db.tenants if t.get("phone") == signup_data.phone), 
        None
    )
    if existing_tenant:
        raise HTTPException(
            status_code=400, 
            detail="Account already exists with this phone number"
        )
    
    # Generate new tenant
    tenant_id = f"tnt_{uuid.uuid4().hex[:8]}"
    trackier_pid = str(len(db.tenants) + 10000)  # Auto-increment from 10000
    api_key = f"pk_live_{uuid.uuid4().hex}"
    
    # Create tenant record
    tenant_data = {
        "tenant_id": tenant_id,
        "name": signup_data.name,
        "email": signup_data.email,
        "phone": signup_data.phone,
        "brand_name": signup_data.brand_name or signup_data.name,
        "trackier_pid": trackier_pid,
        "default_share_pct": 40.0,  # Default from business rules
        "api_key": api_key,
        "created_at": datetime.utcnow().isoformat(),
        "status": "active"
    }
    
    # Save to mock database
    saved_tenant = db.save_tenant(tenant_data)
    
    # Emit event: creator.onboarded (mock Slack webhook)
    print(f"🚀 New Creator Onboarded: {signup_data.name} (tenant_id: {tenant_id})")
    
    # Return success response
    return TenantResponse(
        tenant_id=tenant_id,
        name=signup_data.name,
        trackier_pid=trackier_pid,
        default_share_pct=40.0,
        api_key=api_key
    )

# NEW BLOCK 2 ENDPOINTS

@app.get("/v1/offers", response_model=List[OfferResponse], tags=["Admin APIs"])
async def get_offers(
    tenant_id: Optional[str] = None,
    brand_id: Optional[str] = None,
    category: Optional[str] = None,
    q: Optional[str] = None,
    min_commission: Optional[float] = None,
    limit: int = 50
):
    """
    Get available offers for campaign creation with enhanced filtering for API-only partners
    """
    offers = db.get_offers(tenant_id=tenant_id, category=category, active_only=True)
    
    # Apply additional filters
    if brand_id:
        offers = [o for o in offers if o.get("advertiser_id") == brand_id]
    
    if q:
        offers = [o for o in offers if q.lower() in o.get("brand", "").lower() or q.lower() in o.get("category", "").lower()]
    
    if min_commission:
        offers = [o for o in offers if o.get("base_commission_pct", 0) >= min_commission]
    
    # Filter by API exposure
    offers = [o for o in offers if o.get("exposed_via_api", True)]
    
    # Apply limit
    offers = offers[:limit]
    
    # Convert to response format
    response_offers = [
        OfferResponse(
            offer_id=offer["offer_id"],
            trackier_campaign_id=offer.get("trackier_campaign_id", ""),
            advertiser_id=offer.get("advertiser_id", ""),
            brand=offer["brand"],
            category=offer.get("category", "General"),
            base_commission_pct=offer["base_commission_pct"],
            cool_off_days=offer.get("cool_off_days", 30),
            status=offer.get("status", "active"),
            exposed_via_api=offer.get("exposed_via_api", True)
        )
        for offer in offers
    ]
    
    return response_offers

@app.post("/v1/sync/offers", response_model=SyncResponse, tags=["Trackier Integration"])
async def sync_offers_manual(background_tasks: BackgroundTasks):
    """
    Manual trigger for Trackier catalogue sync
    Based on catalogue-sync.flow.md
    """
    print("🔄 Manual catalogue sync triggered")
    
    # Run sync
    result = await catalogue_service.sync_campaigns()
    
    # Log results
    print(f"📊 Sync Results: {result['added']} added, {result['updated']} updated, {result['deactivated']} deactivated")
    
    return SyncResponse(
        status=result['status'],
        offers_processed=result['campaigns_processed'],
        added=result['added'],
        updated=result['updated'],
        deactivated=result['deactivated'],
        duration_seconds=0
    )

@app.post("/v1/sync/advertisers", tags=["Trackier Integration"])
async def sync_advertisers_manual():
    """Manual sync of advertisers (brands) from Trackier"""
    catalogue_service = CatalogueService(db)
    result = await catalogue_service.sync_advertisers()
    return result

@app.post("/v1/sync/campaigns", tags=["Trackier Integration"])
async def sync_campaigns_manual(advertiser_id: Optional[str] = None):
    """Manual sync of campaigns (offers) from Trackier"""
    catalogue_service = CatalogueService(db)
    result = await catalogue_service.sync_campaigns(advertiser_id=advertiser_id)
    return result

@app.get("/v1/trackier/advertisers", tags=["Trackier Integration"])
async def get_trackier_advertisers():
    """Get advertisers (brands) from Trackier"""
    trackier_client = TrackierClient("mock_api_key")
    advertisers = await trackier_client.get_advertisers()
    return advertisers

@app.get("/v1/trackier/campaigns", tags=["Trackier Integration"])
async def get_trackier_campaigns(advertiser_id: Optional[str] = None, publisher_id: Optional[str] = None):
    """Get campaigns (offers) from Trackier"""
    trackier_client = TrackierClient("mock_api_key")
    campaigns = await trackier_client.get_campaigns(advertiser_id=advertiser_id, publisher_id=publisher_id)
    return campaigns

@app.get("/v1/trackier/publishers", tags=["Trackier Integration"])
async def get_trackier_publishers():
    """Get publishers (creators) from Trackier"""
    trackier_client = TrackierClient("mock_api_key")
    publishers = await trackier_client.get_publishers()
    return publishers

@app.get("/v1/categories", tags=["Admin APIs"])
async def get_categories():
    """Get distinct categories with counts from offers"""
    categories = {}
    
    for offer in db.offers:
        if offer["status"] == "active":
            cat = offer["category"]
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
    
    return [
        {"category": cat, "count": count} 
        for cat, count in categories.items()
    ]

@app.get("/v1/brands", response_model=List[BrandResponse], tags=["Admin APIs"])
async def get_brands():
    """Get all brands/advertisers"""
    return [
        BrandResponse(
            brand_id=brand["brand_id"],
            trackier_advertiser_id=brand["trackier_advertiser_id"],
            name=brand["name"],
            logo_url=brand.get("logo_url")
        )
        for brand in db.advertisers
    ]

@app.get("/v1/offers/stats", tags=["Analytics"])
async def get_offers_stats():
    """Debug endpoint for offer statistics"""
    offers = db.get_offers(active_only=False)
    
    stats = {
        "total_offers": len(offers),
        "active_offers": len([o for o in offers if o.get("status") == "active"]),
        "categories": list(set(o.get("category", "Unknown") for o in offers)),
        "brands": list(set(o.get("brand", "Unknown") for o in offers)),
        "last_sync": "manual_trigger"  # In real app, track last sync time
    }
    
    return stats

# NEW BLOCK 3 ENDPOINTS

@app.post("/v1/campaigns", response_model=CampaignResponse, tags=["Admin APIs"])
async def create_campaign(request: CampaignCreateRequest):
    """
    Create new campaign
    Endpoint #4 from technical specifications
    """
    print(f"🎯 Creating campaign '{request.name}' for tenant {request.tenant_id}")
    
    campaign = campaign_builder.create_campaign(
        tenant_id=request.tenant_id,
        name=request.name,
        share_pct=request.share_pct
    )
    
    print(f"✅ Campaign created: {campaign.campaign_id}")
    return campaign

@app.post("/v1/links", response_model=LinkResponse, tags=["Admin APIs"])
async def create_smart_link(request: LinkCreateRequest):
    """
    Generate smart link for campaign + offer
    Endpoint #5 from technical specifications
    """
    print(f"🔗 Generating smart link for campaign {request.campaign_id} + offer {request.offer_id}")
    
    link = campaign_builder.generate_smart_link(
        campaign_id=request.campaign_id,
        offer_id=request.offer_id
    )
    
    print(f"✅ Smart link generated: {link.smart_link}")
    return link

@app.get("/v1/analytics/creator", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_creator_analytics(
    tenant_id: str,
    period: str = "30d"
):
    """
    Get creator analytics dashboard
    Endpoint #6 from technical specifications
    """
    print(f"📊 Fetching analytics for tenant {tenant_id} (period: {period})")
    
    analytics = campaign_builder.get_tenant_analytics(tenant_id, period)
    
    return analytics

# Creator Dashboard API Endpoints
@app.get("/v1/creator/stats", response_model=CreatorStatsResponse, tags=["Creator APIs"])
async def get_creator_stats(tenant_id: str = Depends(get_creator_tenant_id), range: str = "today"):
    """
    Get creator quick stats for Overview tab
    """
    # Mock stats data
    today = datetime.utcnow().date()
    
    # Calculate today's clicks
    today_clicks = len([
        c for c in db.clicks 
        if datetime.fromisoformat(c["timestamp"]).date() == today
        and any(l["campaign_id"] in [camp["campaign_id"] for camp in db.campaigns if camp["tenant_id"] == tenant_id] 
                for l in db.links if l["link_id"] == c["link_id"])
    ])
    
    # Calculate today's conversions
    today_conversions = len([
        l for l in db.ledger 
        if datetime.fromisoformat(l["created_at"]).date() == today
        and any(camp["tenant_id"] == tenant_id 
                for camp in db.campaigns if camp["campaign_id"] == l["campaign_id"])
    ])
    
    # Calculate pending payout
    pending_payout = sum([
        l["user_amount"] for l in db.ledger 
        if l["status"] in ["queued", "confirmed"]
        and any(camp["tenant_id"] == tenant_id 
                for camp in db.campaigns if camp["campaign_id"] == l["campaign_id"])
    ])
    
    return CreatorStatsResponse(
        clicks_today=today_clicks,
        conversions_today=today_conversions,
        pending_payout=pending_payout,
        period=range
    )

@app.get("/v1/creator/campaigns", response_model=List[CreatorCampaignResponse], tags=["Creator APIs"])
async def get_creator_campaigns(tenant_id: str = Depends(get_creator_tenant_id)):
    """
    Get creator campaigns for Campaigns tab
    """
    creator_campaigns = []
    
    for campaign in db.campaigns:
        if campaign["tenant_id"] == tenant_id:
            # Calculate campaign stats
            campaign_links = [l for l in db.links if l["campaign_id"] == campaign["campaign_id"]]
            total_clicks = len([c for c in db.clicks if c["link_id"] in [l["link_id"] for l in campaign_links]])
            total_conversions = len([l for l in db.ledger if l["campaign_id"] == campaign["campaign_id"]])
            
            creator_campaigns.append(CreatorCampaignResponse(
                campaign_id=campaign["campaign_id"],
                name=campaign["name"],
                status=campaign["status"],
                created_at=campaign["created_at"],
                share_pct=campaign["share_pct"],
                total_clicks=total_clicks,
                total_conversions=total_conversions
            ))
    
    return creator_campaigns

@app.get("/v1/creator/payouts", response_model=List[CreatorPayoutResponse], tags=["Creator APIs"])
async def get_creator_payouts(tenant_id: str = Depends(get_creator_tenant_id), status: Optional[str] = None):
    """
    Get creator payouts for Payouts tab
    """
    # Get all ledger entries for this creator
    creator_ledger = [
        l for l in db.ledger 
        if any(camp["tenant_id"] == tenant_id 
               for camp in db.campaigns if camp["campaign_id"] == l["campaign_id"])
    ]
    
    # Get payouts for these ledger entries
    creator_payouts = []
    for payout in db.payouts:
        # Check if this payout is for the creator's ledger entries
        if any(lid in [l["ledger_id"] for l in creator_ledger] for lid in payout["ledger_ids"]):
            if status is None or payout["status"] == status:
                creator_payouts.append(CreatorPayoutResponse(
                    payout_id=payout["payout_id"],
                    date=payout["ts_paid"],
                    amount=payout["amount"],
                    status=payout["status"],
                    voucher_code=payout.get("voucher_code")
                ))
    
    return creator_payouts

@app.get("/v1/creator/profile", tags=["Creator APIs"])
async def get_creator_profile(tenant_id: str = Depends(get_creator_tenant_id)):
    """
    Get creator profile information
    """
    # Find creator
    creator = next((t for t in db.tenants if t["tenant_id"] == tenant_id), None)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    
    return {
        "tenant_id": creator["tenant_id"],
        "name": creator["name"],
        "phone": creator.get("phone", ""),
        "email": creator.get("email", ""),
        "theme_hex": creator.get("theme_hex", "#3B82F6")
    }

@app.put("/v1/creator/profile", tags=["Creator APIs"])
async def update_creator_profile(request: CreatorProfileUpdateRequest, tenant_id: str = Depends(get_creator_tenant_id)):
    """
    Update creator profile settings
    """
    # Find creator
    creator = next((t for t in db.tenants if t["tenant_id"] == tenant_id), None)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    
    # Update fields
    if request.display_name:
        creator["name"] = request.display_name
    if request.phone:
        creator["phone"] = request.phone
    if request.email:
        creator["email"] = request.email
    if request.theme_hex:
        creator["theme_hex"] = request.theme_hex
    
    return {"message": "Profile updated successfully", "creator": creator}

@app.get("/v1/campaigns", tags=["Admin APIs"])
async def list_campaigns(tenant_id: Optional[str] = None):
    """Debug endpoint to list campaigns"""
    if tenant_id:
        campaigns = db.get_tenant_campaigns(tenant_id)
    else:
        campaigns = db.campaigns
    
    return {"campaigns": campaigns, "count": len(campaigns)}

@app.get("/v1/links", tags=["Admin APIs"])
async def list_links(tenant_id: Optional[str] = None):
    """Debug endpoint to list smart links"""
    if tenant_id:
        links = db.get_tenant_links(tenant_id)
    else:
        links = db.links
    
    return {"links": links, "count": len(links)}

# Existing debug endpoints
@app.get("/v1/tenants", tags=["Admin APIs"])
async def list_tenants():
    """Debug endpoint to view all tenants"""
    return {"tenants": db.tenants, "count": len(db.tenants)}

@app.get("/v1/tenants/{tenant_id}", tags=["Admin APIs"])
async def get_tenant(tenant_id: str):
    """Get specific tenant details"""
    tenant = next((t for t in db.tenants if t["tenant_id"] == tenant_id), None)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

# BLOCK 4: END-USER JOURNEY ENDPOINTS

@app.get("/go/{slug}", tags=["End-User APIs"])
async def handle_smart_link(slug: str):
    """
    Handle smart link clicks - serves end-user landing page
    This is the entry point for users clicking creator's shared links
    """
    print(f"🔗 Smart link accessed: {slug}")
    
    # Find the link by slug
    link = db.get_link_by_slug(slug)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Get campaign and offer details for display
    campaign = db.get_campaign(link["campaign_id"])
    offer = next((o for o in db.offers if o["offer_id"] == link["offer_id"]), None)
    
    if not campaign or not offer:
        raise HTTPException(status_code=404, detail="Campaign or offer not found")
    
    # Calculate potential cashback
    potential_cashback = offer["base_commission_pct"] * (campaign["share_pct"] / 100)
    
    print(f"📄 Serving landing page for {offer['brand']} (potential cashback: {potential_cashback}%)")
    
    # Serve the end-user landing page HTML
    return FileResponse('static/landing.html')

@app.post("/v1/events/click", response_model=ClickTrackingResponse, tags=["Events & Webhooks"])
async def track_click(request: ClickTrackingRequest):
    """
    Track user clicks for analytics
    Endpoint #7 from technical specifications
    """
    print(f"📊 Tracking click for link {request.link_id}")
    
    # Verify link exists
    link = next((l for l in db.links if l["link_id"] == request.link_id), None)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Create click record
    click_data = {
        "link_id": request.link_id,
        "user_id": request.user_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    click = db.create_click(click_data)
    
    print(f"✅ Click tracked: {click['click_id']}")
    
    return ClickTrackingResponse(
        click_id=click["click_id"],
        link_id=click["link_id"],
        user_id=click.get("user_id"),
        timestamp=click["timestamp"]
    )

@app.post("/v1/auth/enduser/otp/request", tags=["End-User APIs"])
async def request_enduser_otp(request: EndUserOTPRequest):
    """
    Request OTP for end-user verification (specific to a link)
    """
    print(f"📱 End-user OTP requested for {request.phone} (link: {request.link_id})")
    
    # Verify link exists
    link = next((l for l in db.links if l["link_id"] == request.link_id), None)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Generate request ID
    request_id = f"req_{uuid.uuid4().hex[:8]}"
    
    # Store OTP request (in real app, would send SMS)
    db.otp_requests[request_id] = {
        "phone": request.phone,
        "link_id": request.link_id,
        "code": "123456",  # Mock OTP
        "expires_at": datetime.utcnow() + timedelta(minutes=5),
        "verified": False
    }
    
    print(f"📨 Mock OTP sent: 123456 (request_id: {request_id})")
    
    return {"request_id": request_id, "message": "OTP sent successfully"}

@app.post("/v1/auth/enduser/otp/verify", tags=["End-User APIs"])
async def verify_enduser_otp(request: EndUserOTPVerifyRequest):
    """
    Verify OTP for end-user and return redirect info
    """
    print(f"🔐 Verifying end-user OTP for request {request.request_id}")
    
    # Check OTP request exists
    otp_data = db.otp_requests.get(request.request_id)
    if not otp_data:
        raise HTTPException(status_code=400, detail="Invalid request ID")
    
    # Check expiry
    if datetime.utcnow() > otp_data["expires_at"]:
        raise HTTPException(status_code=400, detail="OTP expired")
    
    # Verify code
    if otp_data["code"] != request.code:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Mark as verified
    otp_data["verified"] = True
    
    # Get link and offer details for redirect
    link = next((l for l in db.links if l["link_id"] == request.link_id), None)
    offer = next((o for o in db.offers if o["offer_id"] == link["offer_id"]), None)
    
    # Mock merchant redirect URL (in real app, would be trackable URL)
    merchant_url = f"https://dl.flipkart.com/dl/home-decor?utm_source=hissaback&click_id={uuid.uuid4().hex[:8]}"
    
    print(f"✅ OTP verified! Redirecting to: {merchant_url}")
    
    return {
        "verified": True,
        "merchant_url": merchant_url,
        "message": "Verification successful! Redirecting to merchant..."
    }

@app.post("/v1/events/conversion", tags=["Events & Webhooks"])
async def process_conversion(request: ConversionWebhookRequest):
    """
    Trackier webhook: process conversion, calculate split, create ledger entry
    """
    print(f"🎯 Processing conversion for click {request.click_id}, order {request.order_id}")
    # Find click
    click = next((c for c in db.clicks if c["click_id"] == request.click_id), None)
    if not click:
        raise HTTPException(status_code=404, detail="Click not found")
    # Find link
    link = next((l for l in db.links if l["link_id"] == click["link_id"]), None)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    # Find campaign
    campaign = db.get_campaign(link["campaign_id"])
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    # Find offer
    offer = next((o for o in db.offers if o["offer_id"] == request.offer_id), None)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    # Calculate commission split
    base_commission = offer["base_commission_pct"] * request.sale_amount / 100.0
    user_pct = 100.0 - campaign["share_pct"]
    user_amount = base_commission * (user_pct / 100.0)
    creator_amount = base_commission - user_amount
    # Cool-off period
    cool_off_days = offer.get("cool_off_days", 30)
    cool_off_until = (datetime.utcnow() + timedelta(days=cool_off_days)).isoformat()
    # Create ledger entry
    ledger_data = {
        "conv_id": f"conv_{uuid.uuid4().hex[:8]}",
        "click_id": click["click_id"],
        "link_id": link["link_id"],
        "campaign_id": campaign["campaign_id"],
        "offer_id": offer["offer_id"],
        "user_id": click.get("user_id", "anonymous"),
        "order_id": request.order_id,
        "sale_amount": request.sale_amount,
        "base_commission": base_commission,
        "user_pct": user_pct,
        "user_amount": user_amount,
        "creator_amount": creator_amount,
        "status": "queued" if request.status == "approved" else request.status,
        "cool_off_until": cool_off_until
    }
    ledger_entry = db.create_ledger_entry(ledger_data)
    print(f"✅ Ledger entry created: {ledger_entry['ledger_id']} (user: {ledger_entry['user_amount']}, creator: {ledger_entry['creator_amount']})")
    return {"status": "ok", "ledger_id": ledger_entry["ledger_id"]}

@app.get("/v1/ledger", tags=["Admin APIs"])
async def list_ledger():
    """Debug endpoint to list ledger entries"""
    return {"ledger": db.ledger, "count": len(db.ledger)}

@app.post("/v1/rewards/payout/run", tags=["Events & Webhooks"])
async def run_payouts():
    """
    Process eligible ledger entries and create payouts (simulate AGCOD)
    """
    print("💸 Running payout job...")
    # Find eligible ledger entries: status='queued', cool_off expired, user_amount >= 10
    now = datetime.utcnow()
    eligible = [
        l for l in db.ledger
        if l["status"] == "queued"
        and l["user_amount"] >= 10
        and datetime.fromisoformat(l["cool_off_until"]) <= now
    ]
    # Group by user_id
    user_groups = {}
    for l in eligible:
        user_id = l["user_id"]
        if user_id not in user_groups:
            user_groups[user_id] = []
        user_groups[user_id].append(l)
    payout_count = 0
    for user_id, entries in user_groups.items():
        total = sum(l["user_amount"] for l in entries)
        ledger_ids = [l["ledger_id"] for l in entries]
        # Simulate AGCOD voucher code
        voucher_code = f"AGC-{uuid.uuid4().hex[:8].upper()}"
        payout_data = {
            "user_id": user_id,
            "amount": total,
            "method": "amazon_gv",
            "voucher_code": voucher_code,
            "ledger_ids": ledger_ids
        }
        payout = db.create_payout(payout_data)
        # Mark ledger entries as paid
        for l in entries:
            l["status"] = "paid"
        payout_count += 1
        print(f"✅ Payout {payout['payout_id']} for user {user_id}: ₹{total} (voucher: {voucher_code})")
        # Simulate notification
        print(f"📲 SMS to {user_id}: Your Amazon voucher {voucher_code} for ₹{total} is ready!")
    return {"paid_count": payout_count, "users_paid": list(user_groups.keys())}

@app.get("/v1/rewards/user", tags=["End-User APIs"])
async def get_user_payouts(user_id: str):
    """List payouts for a user"""
    payouts = db.get_user_payouts(user_id)
    return {"payouts": payouts, "count": len(payouts)}

# Development server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 