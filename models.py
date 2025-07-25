from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

# Database setup
DATABASE_URL = "sqlite:///./hissaback_demo.db"
engine = create_engine(DATABASE_URL, echo=True)

# Enums
class PayoutStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ConversionStatus(str, Enum):
    TRACKED = "tracked"
    CONFIRMED = "confirmed"
    PAID = "paid"
    REJECTED = "rejected"

class CampaignStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

# Base Models
class Tenant(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: f"tnt_{uuid.uuid4().hex[:8]}", primary_key=True)
    name: str
    email: str
    phone: str
    display_name: str
    theme_color: str = "#667eea"
    subdomain: Optional[str] = None
    featured_categories: str = "[]"  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class Offer(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: f"offer_{uuid.uuid4().hex[:8]}", primary_key=True)
    trackier_campaign_id: str
    advertiser_id: str
    brand: str
    category: str
    title: str
    description: str
    commission_rate: float
    base_share_pct: float = 40.0
    exposed_via_api: bool = True
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Campaign(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: f"camp_{uuid.uuid4().hex[:8]}", primary_key=True)
    tenant_id: str = Field(foreign_key="tenant.id")
    offer_id: str = Field(foreign_key="offer.id")
    name: str
    share_pct: float
    status: CampaignStatus = CampaignStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SmartLink(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: f"lnk_{uuid.uuid4().hex[:8]}", primary_key=True)
    campaign_id: str = Field(foreign_key="campaign.id")
    offer_id: str = Field(foreign_key="offer.id")
    slug: str
    smart_link_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Click(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: f"click_{uuid.uuid4().hex[:8]}", primary_key=True)
    link_id: str = Field(foreign_key="smartlink.id")
    campaign_id: str = Field(foreign_key="campaign.id")
    offer_id: str = Field(foreign_key="offer.id")
    tenant_id: str = Field(foreign_key="tenant.id")
    ip_address: str
    user_agent: str
    referrer: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Conversion(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: f"conv_{uuid.uuid4().hex[:8]}", primary_key=True)
    click_id: str = Field(foreign_key="click.id")
    campaign_id: str = Field(foreign_key="campaign.id")
    offer_id: str = Field(foreign_key="offer.id")
    tenant_id: str = Field(foreign_key="tenant.id")
    order_id: str
    sale_amount: float
    commission_amount: float
    status: ConversionStatus = ConversionStatus.TRACKED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None

class Payout(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: f"payout_{uuid.uuid4().hex[:8]}", primary_key=True)
    tenant_id: str = Field(foreign_key="tenant.id")
    amount: float
    method: str  # "gift_card" or "upi"
    status: PayoutStatus = PayoutStatus.PENDING
    reference_id: Optional[str] = None  # GV code or UPI UTR
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

class LedgerEntry(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: f"ledger_{uuid.uuid4().hex[:8]}", primary_key=True)
    tenant_id: str = Field(foreign_key="tenant.id")
    conversion_id: Optional[str] = Field(foreign_key="conversion.id", default=None)
    payout_id: Optional[str] = Field(foreign_key="payout.id", default=None)
    type: str  # "commission", "payout", "adjustment"
    amount: float
    balance_before: float
    balance_after: float
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Database functions
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# Initialize database
create_db_and_tables() 