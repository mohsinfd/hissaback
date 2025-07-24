# API-Only Partner Test Specification

## Test Suite: API-Only Partner Integration

### Test Case 1: API Key Authentication
**Objective**: Verify API key generation and authentication for partners

**Steps**:
1. Generate API key for partner
2. Test API key authentication
3. Verify rate limiting
4. Check permission scoping

**Expected Results**:
- API key generated successfully
- Authentication works correctly
- Rate limits enforced
- Proper permission scoping

**Assertions**:
```python
assert api_key_response['status'] == 'success'
assert api_key_response['key'] is not None
assert rate_limit_headers['X-RateLimit-Limit'] == '300'
```

### Test Case 2: Offer Discovery
**Objective**: Verify partner can discover available offers

**Steps**:
1. Partner calls `/v1/offers` with API key
2. Test various filter parameters
3. Verify response format
4. Check caching behavior

**Expected Results**:
- Offers returned successfully
- Filters work correctly
- Response format matches specification
- Caching functions properly

**Test Parameters**:
- `brand_id`: Filter by specific brand
- `category`: Filter by category
- `q`: Search query
- `min_commission`: Minimum commission filter
- `limit`: Result limit

### Test Case 3: Campaign Creation
**Objective**: Verify partner can create campaigns with offer selection

**Steps**:
1. Partner selects offer from catalogue
2. Create campaign with share percentage
3. Verify campaign creation
4. Check campaign data persistence

**Expected Results**:
- Campaign created successfully
- Offer association maintained
- Share percentage stored correctly
- Campaign ID returned

**Test Scenarios**:
- Percentage-based reward split
- Flat amount reward split
- Invalid offer selection
- Duplicate campaign creation

### Test Case 4: Smart Link Generation
**Objective**: Verify smart link generation for campaigns

**Steps**:
1. Create campaign with offer
2. Generate smart link
3. Verify link format
4. Test link functionality

**Expected Results**:
- Smart link generated successfully
- Link contains proper parameters
- Link redirects correctly
- Tracking parameters embedded

**Link Format Validation**:
```
https://hissaback.app/go/{slug}?publisher_id={publisherId}&campaign_id={campaignId}&trackier_link=1&click_id={{click_id}}
```

### Test Case 5: Conversion Processing
**Objective**: Verify conversion tracking and reward distribution

**Steps**:
1. Simulate click on smart link
2. Process conversion webhook
3. Verify ledger entry creation
4. Check reward distribution

**Expected Results**:
- Click tracked successfully
- Conversion processed correctly
- Ledger entry created
- Rewards distributed according to split

### Test Case 6: Payout Status Tracking
**Objective**: Verify partner can track payout status

**Steps**:
1. Partner queries payout status
2. Verify payout data
3. Test different payout states
4. Check payout history

**Expected Results**:
- Payout status returned correctly
- Historical data available
- Status updates accurate
- Data properly scoped to partner

### Test Case 7: Webhook Integration
**Objective**: Verify webhook delivery for reward events

**Steps**:
1. Partner subscribes to webhooks
2. Trigger reward events
3. Verify webhook delivery
4. Test webhook retry logic

**Expected Results**:
- Webhooks delivered successfully
- Event data accurate
- Retry logic functions
- Delivery confirmations received

## Integration Test Scenarios

### Scenario 1: Complete Partner Flow
**Objective**: Test end-to-end partner integration

**Steps**:
1. Partner generates API key
2. Discovers available offers
3. Creates campaign with offer
4. Generates smart link
5. Tracks conversions and payouts
6. Receives webhook notifications

**Expected Results**:
- Complete flow works seamlessly
- All API calls successful
- Data consistency maintained
- Performance acceptable

### Scenario 2: Multiple Partners
**Objective**: Test system with multiple API-only partners

**Steps**:
1. Create multiple partner accounts
2. Generate unique API keys
3. Test concurrent operations
4. Verify data isolation

**Expected Results**:
- Partners isolated correctly
- No data leakage between partners
- System handles concurrent load
- Performance remains stable

### Scenario 3: Error Handling
**Objective**: Test error scenarios and recovery

**Steps**:
1. Test invalid API keys
2. Test rate limit exceeded
3. Test invalid request data
4. Test system failures

**Expected Results**:
- Appropriate error responses
- Rate limiting enforced
- Data validation working
- Graceful error handling

## Performance Testing

### Load Testing Scenarios
- **Concurrent Partners**: 100 partners making requests
- **High Volume**: 1000+ API calls per minute
- **Large Datasets**: 10000+ offers in catalogue
- **Webhook Volume**: 100+ webhooks per minute

### Performance Benchmarks
- **API Response Time**: < 200ms average
- **Throughput**: 1000+ requests per minute
- **Error Rate**: < 1%
- **Availability**: 99.9% uptime

## Security Testing

### Authentication Tests
- Invalid API key rejection
- Expired key handling
- Key rotation testing
- Permission escalation prevention

### Data Security Tests
- Partner data isolation
- Sensitive data protection
- Audit trail verification
- Access control validation

## Monitoring and Alerting

### Key Metrics to Monitor
- API response times
- Error rates by endpoint
- Rate limit violations
- Partner usage patterns
- Webhook delivery success

### Alerting Rules
- API response time > 500ms
- Error rate > 5%
- Rate limit violations > 100/hour
- Webhook delivery failure > 10%
- System availability < 99%

## Test Data Requirements

### Partner Test Data
```json
{
  "partner_id": "partner_001",
  "api_key": "test_api_key_123",
  "allowed_brands": ["brand_001", "brand_002"],
  "rate_limit": 300,
  "permissions": ["read_offers", "create_campaigns", "generate_links"]
}
```

### Offer Test Data
```json
{
  "offer_id": 1234,
  "brand": "Test Brand",
  "category": "E-commerce",
  "base_commission_pct": 5.0,
  "exposed_via_api": true
}
```

### Campaign Test Data
```json
{
  "campaign_id": "camp_123",
  "offer_id": 1234,
  "share_pct": 50.0,
  "reward_type": "PERCENT",
  "tenant_id": "partner_001"
}
``` 