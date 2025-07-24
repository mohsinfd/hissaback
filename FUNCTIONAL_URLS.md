# 🚀 Hissaback Platform - Complete Functional URLs Repository

## 📍 **Main Landing Page**
- **URL**: `http://localhost:8001/`
- **Description**: Complete interface repository - serves as the main entry point for all platform interfaces
- **Features**: Organized by user type, direct links to all interfaces, API documentation, and quick access

---

## 🏢 **Admin Interfaces**

### **Admin Dashboard**
- **URL**: `http://localhost:8001/admin_dashboard.html`
- **Description**: Complete platform management interface
- **Features**: 
  - Campaign creation and management
  - Smart link generation
  - Tenant management
  - Trackier data synchronization
  - Platform analytics

### **API Documentation (Swagger)**
- **URL**: `http://localhost:8001/docs`
- **Description**: Interactive API documentation with categorized endpoints
- **Features**:
  - Organized by API categories (Authentication, Creator APIs, Admin APIs, etc.)
  - Interactive testing interface
  - Request/response examples
  - Authentication requirements

### **Custom API Documentation**
- **URL**: `http://localhost:8001/api_docs.html`
- **Description**: User-friendly API documentation
- **Features**:
  - Business-focused descriptions
  - Organized by user type
  - Easier navigation for non-technical users

---

## 👥 **Creator Interfaces**

### **Creator Dashboard**
- **URL**: `http://localhost:8001/creator_dashboard.html`
- **Description**: Main dashboard for creators (publishers)
- **Features**:
  - Campaign management
  - Earnings tracking
  - Performance analytics
  - Smart link generation
  - Payout history

### **Creator Login**
- **URL**: `http://localhost:8001/creator_login.html`
- **Description**: Authentication interface for creators
- **Features**:
  - Phone number login
  - OTP verification
  - Account creation

---

## 🎯 **End-User Interfaces**

### **Smart Link Handler**
- **URL**: `http://localhost:8001/go/{slug}`
- **Example**: `http://localhost:8001/go/sample-offer`
- **Description**: Smart link interface for end-users
- **Features**:
  - OTP verification
  - Reward claiming
  - Purchase tracking
  - Cashback processing

---

## 🔗 **API Endpoints**

### **Authentication APIs**
- `POST /v1/auth/otp/request` - Request OTP
- `POST /v1/auth/otp/verify` - Verify OTP
- `POST /v1/auth/creator/login` - Creator login
- `POST /v1/auth/creator/verify` - Creator verification

### **Creator APIs**
- `GET /v1/creator/stats` - Creator statistics
- `GET /v1/creator/campaigns` - Creator campaigns
- `GET /v1/creator/payouts` - Creator payouts
- `POST /v1/creators/signup` - Creator registration

### **Admin APIs**
- `GET /v1/offers` - List offers
- `GET /v1/campaigns` - List campaigns
- `GET /v1/tenants` - List tenants
- `GET /v1/categories` - Get categories
- `GET /v1/brands` - Get brands
- `POST /v1/campaigns` - Create campaign
- `POST /v1/links` - Generate smart link

### **Trackier Integration**
- `GET /v1/trackier/advertisers` - Get advertisers
- `GET /v1/trackier/campaigns` - Get campaigns
- `GET /v1/trackier/publishers` - Get publishers
- `POST /v1/sync/advertisers` - Sync advertisers
- `POST /v1/sync/campaigns` - Sync campaigns

### **Analytics & Events**
- `GET /v1/analytics/creator` - Creator analytics
- `GET /v1/offers/stats` - Offer statistics
- `POST /v1/events/click` - Track click
- `POST /v1/events/conversion` - Process conversion

### **End-User APIs**
- `GET /go/{slug}` - Smart link handler
- `GET /v1/rewards/user` - User rewards
- `POST /v1/auth/enduser/otp/request` - End-user OTP request
- `POST /v1/auth/enduser/otp/verify` - End-user OTP verify

---

## ⚡ **Quick Access Links**

### **System Health**
- **URL**: `http://localhost:8001/health`
- **Description**: System health status and uptime monitoring

### **OpenAPI Schema**
- **URL**: `http://localhost:8001/openapi.json`
- **Description**: Raw OpenAPI 3.1 specification for API integration

### **Widget Script**
- **URL**: `http://localhost:8001/static/widget.js`
- **Description**: JavaScript widget for embedding offer grids

---

## 🎯 **User Journey Examples**

### **Admin User Journey**
1. **Start**: `http://localhost:8001/` (Landing page)
2. **Access**: `http://localhost:8001/admin_dashboard.html` (Admin dashboard)
3. **API Docs**: `http://localhost:8001/docs` (Swagger documentation)
4. **Custom Docs**: `http://localhost:8001/api_docs.html` (User-friendly docs)

### **Creator User Journey**
1. **Start**: `http://localhost:8001/` (Landing page)
2. **Login**: `http://localhost:8001/creator_login.html` (Authentication)
3. **Dashboard**: `http://localhost:8001/creator_dashboard.html` (Main interface)

### **End-User Journey**
1. **Smart Link**: `http://localhost:8001/go/sample-offer` (Creator-generated link)
2. **Verification**: OTP verification through the interface
3. **Rewards**: Automatic reward processing

---

## 🔧 **Development & Testing**

### **API Testing**
- **Swagger UI**: `http://localhost:8001/docs`
- **Health Check**: `http://localhost:8001/health`
- **OpenAPI Schema**: `http://localhost:8001/openapi.json`

### **Frontend Testing**
- **All Interfaces**: Accessible through the main landing page
- **Direct Access**: Each interface has its own direct URL
- **Mobile Responsive**: All interfaces work on mobile devices

---

## 📱 **Mobile Access**

All interfaces are mobile-responsive and can be accessed from:
- **Desktop**: `http://localhost:8001/`
- **Mobile**: `http://localhost:8001/` (same URL, responsive design)
- **Tablet**: `http://localhost:8001/` (adaptive layout)

---

## 🚀 **Quick Start Guide**

1. **Start Server**: `python -m uvicorn app:app --host 0.0.0.0 --port 8001`
2. **Open Landing**: `http://localhost:8001/`
3. **Choose Interface**: Click on any interface card to access it
4. **Test APIs**: Use `/docs` for interactive API testing
5. **Explore Features**: Navigate through different user interfaces

---

## ✅ **Status Indicators**

- **🟢 LIVE**: Fully functional interfaces
- **🟡 DEV**: Development/testing interfaces
- **🔵 API**: Backend API endpoints
- **🟣 DOCS**: Documentation interfaces

---

*Last Updated: Hissaback Platform v1.0.0*
*All URLs are relative to `http://localhost:8001/` when running locally* 