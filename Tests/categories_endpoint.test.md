# Categories Endpoint Test Specification

## Test Suite: Categories API Endpoint

### Test Case 1: Basic Categories Retrieval
**Objective**: Verify that `/v1/categories` returns distinct categories with counts

**Steps**:
1. Call `/v1/categories` endpoint
2. Verify response format
3. Check category counts
4. Validate data accuracy

**Expected Results**:
- Categories returned successfully
- Each category has accurate count
- Response format matches specification
- Only active offers counted

**Assertions**:
```python
assert response.status_code == 200
assert len(response.json()) > 0
assert all('category' in item for item in response.json())
assert all('count' in item for item in response.json())
assert all(item['count'] > 0 for item in response.json())
```

### Test Case 2: Categories After Sync
**Objective**: Verify categories endpoint returns correct counts after offer sync

**Steps**:
1. Perform offer sync from Trackier
2. Call categories endpoint
3. Verify counts match synced data
4. Check for new categories

**Expected Results**:
- Categories reflect synced offers
- Counts accurate after sync
- New categories appear correctly
- No duplicate categories

**Test Data**:
```json
{
  "categories": [
    {"category": "E-commerce", "count": 15},
    {"category": "Fashion", "count": 8},
    {"category": "Beauty", "count": 12},
    {"category": "Electronics", "count": 6}
  ]
}
```

### Test Case 3: Empty Categories Handling
**Objective**: Verify behavior when no offers exist

**Steps**:
1. Clear all offers from database
2. Call categories endpoint
3. Verify empty response
4. Restore test data

**Expected Results**:
- Empty array returned
- No errors thrown
- Response format maintained
- System handles empty state gracefully

### Test Case 4: Category Count Accuracy
**Objective**: Verify category counts match actual offer data

**Steps**:
1. Count offers by category manually
2. Call categories endpoint
3. Compare manual counts with API
4. Verify accuracy

**Expected Results**:
- API counts match manual counts
- Only active offers included
- No discrepancies found
- Counts are real-time accurate

### Test Case 5: Performance Testing
**Objective**: Verify categories endpoint performance

**Steps**:
1. Load large dataset (1000+ offers)
2. Measure response time
3. Test concurrent requests
4. Monitor resource usage

**Expected Results**:
- Response time < 100ms
- Handles concurrent requests
- Memory usage stable
- No performance degradation

### Test Case 6: Category Filtering
**Objective**: Verify categories respect offer filtering

**Steps**:
1. Filter offers by various criteria
2. Call categories endpoint
3. Verify counts reflect filters
4. Test different filter combinations

**Expected Results**:
- Categories respect offer filters
- Counts accurate for filtered data
- Filter combinations work correctly
- No data leakage

## Integration Tests

### Test Case 7: Categories with Offer Creation
**Objective**: Verify categories update when offers are created

**Steps**:
1. Record initial category counts
2. Create new offer with existing category
3. Create new offer with new category
4. Verify category counts updated

**Expected Results**:
- Existing category count increased
- New category appears in list
- Counts updated immediately
- Data consistency maintained

### Test Case 8: Categories with Offer Deactivation
**Objective**: Verify categories update when offers are deactivated

**Steps**:
1. Record initial category counts
2. Deactivate offers in specific category
3. Verify category count decreased
4. Check category removal if count reaches zero

**Expected Results**:
- Category count decreased correctly
- Category removed if count reaches zero
- Only active offers counted
- Data integrity maintained

## Edge Cases

### Test Case 9: Special Characters in Categories
**Objective**: Verify handling of special characters in category names

**Steps**:
1. Create offers with special characters in categories
2. Call categories endpoint
3. Verify special characters handled correctly
4. Check JSON encoding

**Test Categories**:
- "E-commerce & Retail"
- "Fashion & Beauty"
- "Tech & Electronics"
- "Food & Beverage"

**Expected Results**:
- Special characters preserved
- JSON encoding correct
- No parsing errors
- Display handled properly

### Test Case 10: Very Long Category Names
**Objective**: Verify handling of very long category names

**Steps**:
1. Create offers with very long category names
2. Call categories endpoint
3. Verify long names handled correctly
4. Check response size limits

**Expected Results**:
- Long names handled gracefully
- No truncation issues
- Response size reasonable
- Performance not impacted

## Performance Benchmarks

### Response Time Requirements
- **Small Dataset** (< 100 offers): < 50ms
- **Medium Dataset** (100-1000 offers): < 100ms
- **Large Dataset** (> 1000 offers): < 200ms

### Memory Usage Limits
- **Peak Memory**: < 10MB
- **Memory Leaks**: None detected
- **Garbage Collection**: Proper cleanup

### Concurrent Request Handling
- **10 Concurrent Requests**: All successful
- **100 Concurrent Requests**: All successful
- **1000 Concurrent Requests**: 95% success rate

## Error Handling

### Test Case 11: Database Connection Errors
**Objective**: Verify graceful handling of database errors

**Steps**:
1. Simulate database connection failure
2. Call categories endpoint
3. Verify error response
4. Check error logging

**Expected Results**:
- Appropriate error response
- Error logged correctly
- No system crash
- Graceful degradation

### Test Case 12: Invalid Request Handling
**Objective**: Verify handling of invalid requests

**Steps**:
1. Send malformed requests
2. Test invalid HTTP methods
3. Verify error responses
4. Check security headers

**Expected Results**:
- Proper error responses
- Security headers present
- No information leakage
- Request validation working

## Monitoring and Validation

### Key Metrics to Monitor
- Response time percentiles
- Error rates
- Category count accuracy
- Cache hit rates (if implemented)

### Validation Rules
- Category counts must be positive integers
- No duplicate categories in response
- All categories must have associated offers
- Response format must be consistent

### Alerting Criteria
- Response time > 500ms
- Error rate > 1%
- Category count discrepancies detected
- Database connection failures

## Test Data Setup

### Sample Offer Data
```json
[
  {
    "offer_id": 1,
    "category": "E-commerce",
    "status": "active"
  },
  {
    "offer_id": 2,
    "category": "Fashion",
    "status": "active"
  },
  {
    "offer_id": 3,
    "category": "E-commerce",
    "status": "active"
  },
  {
    "offer_id": 4,
    "category": "Beauty",
    "status": "inactive"
  }
]
```

### Expected Categories Response
```json
[
  {
    "category": "E-commerce",
    "count": 2
  },
  {
    "category": "Fashion",
    "count": 1
  }
]
```

## Automation Requirements

### Test Environment Setup
- Clean database state before each test
- Consistent test data loading
- Mock external dependencies
- Isolated test execution

### Continuous Integration
- Tests run on every code change
- Performance regression detection
- Automated reporting
- Failure notification 