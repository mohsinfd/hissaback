# API-Only Partner Flow Specification

## Overview
Flow for partners who want to integrate Hissaback's offer catalogue and reward system via API only, without using our UI.

## Partner Onboarding

### 1. API Key Generation
- **Method**: Partner generates API key in our console or via admin
- **Scope**: Define allowed brands/offers for the partner
- **Rate Limits**: 300 req/min; burst 1,000
- **Permissions**: Read offers, create campaigns, generate links

### 2. Partner Discovery
- **Endpoint**: `GET /v1/offers`
- **Filters**: `brand_id`, `category`, `q`, `min_commission`
- **Response**: Enriched offer list with brand name, base commission, default share%
- **Caching**: 5-minute TTL for public API keys

## Campaign Creation Flow

### 1. Offer Discovery
- Partner calls `/v1/offers` to discover catalogue
- Filtered by their allowed brands/offers
- Review offer details, commission rates, categories

### 2. Campaign Creation
- **Endpoint**: `POST /v1/campaigns`
- **Body**: `{ offer_id, share_pct | flat_reward, tenant_id }`
- **Logic**: We persist split logic; Trackier doesn't know about it
- **Response**: Campaign details with campaign_id

### 3. Smart Link Generation
- **Endpoint**: `POST /v1/links`
- **Body**: `{ campaign_id }`
- **Response**: Smart link with embedded pid & offer_id
- **Alternative**: Raw Trackier link + our redirect param macro

## Conversion & Reward Flow

### 1. Conversion Processing
- Conversions & postbacks hit our system
- We split commission based on campaign settings
- Create ledger entries for tracking
- Process payouts to end users

### 2. Payout Status
- **Endpoint**: `GET /v1/rewards/user` (already exists)
- Partners can query payout statuses
- Track reward distribution and payment status

### 3. Optional Webhooks
- Partner subscribes to webhooks:
  - `reward.paid`: When reward is successfully paid
  - `reward.queued`: When reward is queued for payment
- Real-time notifications for reward events

## Integration Examples

### Headless Integration
- Partner uses only our APIs
- No UI components required
- Full control over user experience
- Custom branding and flow

### Widget Integration
- Use our widget kit (JS/NPM)
- Components: `widgets/offer-grid.js`, `widgets/deal-card.js`
- Props: `tenant_id`, `category`, `limit`, `theme_hex`
- Embedded in partner's existing site

### White-label Site
- Use our white-label site template
- Customizable branding and navigation
- Hosted on our infrastructure
- Partner's domain/subdomain

## Security & Access Control

### API Key Management
- Secure key generation and storage
- Key rotation capabilities
- Usage monitoring and analytics
- Revocation for security incidents

### Rate Limiting
- **Standard**: 300 requests per minute
- **Burst**: 1,000 requests allowed
- **Headers**: Rate limit info in response headers
- **Throttling**: Graceful degradation under load

### Data Isolation
- RLS (Row Level Security) for tenant scoping
- Partner can only access their authorized offers
- Audit logging for all API access
- Data privacy compliance

## Monitoring & Analytics

### Partner Dashboard
- API usage statistics
- Campaign performance metrics
- Revenue and payout tracking
- Error rate monitoring

### System Monitoring
- API response times
- Error rates and types
- Rate limit violations
- Sync job status and performance

## Error Handling

### API Errors
- Standard HTTP status codes
- Detailed error messages
- Error codes for programmatic handling
- Retry recommendations

### Business Logic Errors
- Invalid offer selection
- Insufficient permissions
- Rate limit exceeded
- Campaign creation failures

## Testing & Validation

### Integration Testing
- API endpoint validation
- Authentication and authorization
- Rate limiting behavior
- Error handling scenarios

### Load Testing
- High-volume offer requests
- Concurrent campaign creation
- Webhook delivery reliability
- Database performance under load 