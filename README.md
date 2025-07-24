# 🚀 Hissaback Platform

A comprehensive affiliate commission sharing platform with three main interfaces for testing and managing the complete user journey.

## 📋 Overview

Hissaback is a platform that enables creators to share affiliate links and earn commissions while providing end-users with cashback rewards. Give your audience their hissa back. The platform consists of:

1. **Admin Dashboard** - Platform management and testing
2. **Creator Dashboard** - Creator campaign management
3. **End-User Interface** - User journey from link click to purchase

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin Panel   │    │ Creator Panel   │    │  End-User Flow  │
│                 │    │                 │    │                 │
│ • Manage Users  │    │ • View Stats    │    │ • Click Link    │
│ • Sync Offers   │    │ • Create Camps  │    │ • Verify Phone  │
│ • Test APIs     │    │ • Track Earnings│    │ • Get Cashback  │
│ • Monitor Flow  │    │ • Manage Profile│    │ • Shop & Earn   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   FastAPI Backend│
                    │                 │
                    │ • Authentication│
                    │ • Campaign Mgmt │
                    │ • Click Tracking│
                    │ • Payout System │
                    └─────────────────┘
```

## 🚀 Quick Start

### 1. Start the Server

```bash
# Navigate to project directory
cd "Cursor - 23 - Profitshare 2.0"

# Start the FastAPI server
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### 2. Access the Interfaces

Once the server is running, open your browser and navigate to:

- **Admin Dashboard**: http://localhost:8000/admin_dashboard.html
- **Creator Dashboard**: http://localhost:8000/creator_dashboard.html
- **Creator Login**: http://localhost:8000/creator_login.html
- **API Documentation**: http://localhost:8000/docs

## 🎯 Interface Guide

### 1. Admin Dashboard (`/admin_dashboard.html`)

**Purpose**: Complete platform management and testing interface

**Features**:
- 📊 **Overview**: Platform statistics and quick actions
- 👥 **Creator Management**: Create and manage creators
- 🎯 **Campaign Builder**: Create campaigns and generate smart links
- 🛍️ **Offer Catalogue**: Sync and manage offers from Trackier
- 📈 **Analytics**: View creator performance data
- 🧪 **Testing Flows**: Test all APIs and user journeys

**Quick Actions**:
- Create test creators and campaigns
- Sync offers from external APIs
- Test complete user journeys
- Monitor platform health

### 2. Creator Dashboard (`/creator_dashboard.html`)

**Purpose**: Creator-focused interface for managing campaigns and tracking earnings

**Features**:
- 📊 **Overview**: Performance stats and quick actions
- 🎯 **Campaigns**: View and manage campaigns
- 💰 **Payouts**: Track earnings and payout history
- ⚙️ **Settings**: Update profile and preferences
- 🧪 **Testing**: Test creator-specific APIs

**Authentication**:
- Phone number: `+919820692913`
- OTP code: `123456` (for testing)

### 3. End-User Interface (`/landing.html`)

**Purpose**: Complete user journey from link click to purchase

**Flow**:
1. **Phone Verification**: User enters phone and verifies OTP
2. **Cashback Details**: Shows benefits and confirms eligibility
3. **Redirect to Store**: Automatic redirect to merchant site

**Testing Features**:
- Auto-fill for quick testing
- Debug tools to view API responses
- Click tracking and conversion testing

## 🔧 API Testing

### Creator Authentication Flow

```bash
# 1. Create a creator
curl -X POST "http://localhost:8000/v1/creators/signup" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Creator", "email": "test@example.com", "phone": "+919820692913"}'

# 2. Login (request OTP)
curl -X POST "http://localhost:8000/v1/auth/creator/login" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919820692913"}'

# 3. Verify OTP
curl -X POST "http://localhost:8000/v1/auth/creator/verify" \
  -H "Content-Type: application/json" \
  -d '{"request_id": "mock_request", "code": "123456"}'

# 4. Access creator APIs (use JWT from step 3)
curl -X GET "http://localhost:8000/v1/creator/stats" \
  -H "Authorization: Bearer mock_jwt_creator_xxx"
```

### End-User Flow

```bash
# 1. Request OTP for end-user
curl -X POST "http://localhost:8000/v1/auth/enduser/otp/request" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919820692913", "link_id": "lnk_test123"}'

# 2. Verify OTP
curl -X POST "http://localhost:8000/v1/auth/enduser/otp/verify" \
  -H "Content-Type: application/json" \
  -d '{"request_id": "mock_request", "code": "123456", "link_id": "lnk_test123"}'

# 3. Track click
curl -X POST "http://localhost:8000/v1/events/click" \
  -H "Content-Type: application/json" \
  -d '{"link_id": "lnk_test123", "user_id": "user_test123"}'

# 4. Process conversion
curl -X POST "http://localhost:8000/v1/events/conversion" \
  -H "Content-Type: application/json" \
  -d '{"click_id": "click_test123", "offer_id": 1234, "sale_amount": 1500.00, "order_id": "order_123", "status": "approved"}'
```

## 🎮 Testing Scenarios

### Complete User Journey Test

1. **Admin Dashboard**: Create a test creator and campaign
2. **Creator Dashboard**: Login and view the created campaign
3. **Generate Smart Link**: Create a smart link for the campaign
4. **End-User Flow**: Click the smart link and complete the verification
5. **Track Conversion**: Simulate a purchase conversion

### Quick Test Commands

```bash
# Test server health
curl http://localhost:8000/health

# View all tenants (creators)
curl http://localhost:8000/v1/tenants

# View all campaigns
curl http://localhost:8000/v1/campaigns

# View all offers
curl http://localhost:8000/v1/offers

# Sync offers from Trackier
curl -X POST http://localhost:8000/v1/sync/offers
```

## 📱 Mobile Responsiveness

All interfaces are designed to be mobile-first and responsive:
- Admin Dashboard: Optimized for desktop with mobile support
- Creator Dashboard: Mobile-first design for creators on-the-go
- End-User Interface: Optimized for mobile users clicking links

## 🔐 Security Features

- JWT-based authentication for creators
- OTP verification for both creators and end-users
- Role-based access control
- Secure API endpoints with proper validation

## 🚀 Deployment

The platform is ready for deployment with:
- FastAPI backend with automatic API documentation
- Static file serving for frontend interfaces
- CORS configuration for cross-origin requests
- Mock data for testing (replace with real database in production)

## 📊 Monitoring

- Real-time API response logging
- Click tracking and conversion monitoring
- Creator performance analytics
- Platform health monitoring

## 🎯 Next Steps

1. **Database Integration**: Replace mock data with real database
2. **SMS Integration**: Integrate real SMS service for OTP
3. **Payment Gateway**: Add real payment processing
4. **Analytics Dashboard**: Enhanced reporting and insights
5. **Mobile Apps**: Native mobile applications

---

**Happy Testing! 🎉**

Use the admin dashboard to explore all features and test the complete user journey from creator signup to end-user conversion. 