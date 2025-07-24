# Offer Sync Test Specification

## Test Suite: Offer Sync Functionality

### Test Case 1: Nightly Sync Job Execution
**Objective**: Verify that the nightly sync job correctly inserts/updates offer counts

**Steps**:
1. Set up mock Trackier API responses
2. Trigger sync job manually
3. Verify database state changes
4. Check sync completion event emission

**Expected Results**:
- Sync job completes successfully
- Correct number of offers added/updated
- Sync completion event emitted with accurate counts
- Database contains expected offer data

**Assertions**:
```python
assert sync_result['status'] == 'completed'
assert sync_result['added'] > 0 or sync_result['updated'] > 0
assert sync_result['campaigns_processed'] > 0
```

### Test Case 2: Manual Sync Trigger
**Objective**: Verify manual sync functionality from admin dashboard

**Steps**:
1. Navigate to admin dashboard
2. Click "Sync from Trackier" button
3. Monitor sync progress
4. Verify results display

**Expected Results**:
- Manual sync triggers successfully
- Progress indicators show sync status
- Results displayed with counts
- No errors in console

### Test Case 3: Data Validation
**Objective**: Ensure sync validates and processes data correctly

**Steps**:
1. Provide invalid Trackier API responses
2. Trigger sync with malformed data
3. Verify error handling
4. Check partial failure scenarios

**Expected Results**:
- Invalid data rejected gracefully
- Partial failures logged appropriately
- Valid data processed correctly
- Error messages are descriptive

### Test Case 4: Performance Testing
**Objective**: Verify sync performance under load

**Steps**:
1. Load large dataset (1000+ offers)
2. Measure sync duration
3. Monitor memory usage
4. Check database performance

**Expected Results**:
- Sync completes within acceptable time
- Memory usage remains stable
- Database operations optimized
- No timeouts or crashes

### Test Case 5: Duplicate Handling
**Objective**: Verify duplicate offer detection and handling

**Steps**:
1. Sync same offers multiple times
2. Verify upsert behavior
3. Check data integrity
4. Monitor update vs insert counts

**Expected Results**:
- Duplicates detected correctly
- Existing offers updated, not duplicated
- Data integrity maintained
- Accurate update/insert counts

### Test Case 6: Error Recovery
**Objective**: Test sync recovery from failures

**Steps**:
1. Simulate API failures
2. Trigger sync with retry logic
3. Verify recovery mechanisms
4. Check partial sync completion

**Expected Results**:
- Retry logic works correctly
- Partial failures don't block entire sync
- Recovery mechanisms function
- Error logging is comprehensive

## Test Data Requirements

### Mock Trackier API Responses
```json
{
  "advertisers": [
    {
      "id": "adv_001",
      "name": "Test Brand",
      "category": "E-commerce"
    }
  ],
  "campaigns": [
    {
      "id": "camp_123",
      "advertiser_id": "adv_001",
      "name": "Test Campaign",
      "payout": {"amount": 5.0, "currency": "USD"}
    }
  ]
}
```

### Expected Database State
- Brands table contains synced advertiser data
- Offers table contains synced campaign data
- Proper foreign key relationships maintained
- Audit trail preserved

## Performance Benchmarks

### Acceptable Performance Metrics
- **Sync Duration**: < 5 minutes for 1000 offers
- **Memory Usage**: < 500MB peak
- **Database Operations**: < 1000 queries per sync
- **Error Rate**: < 1% of total operations

### Load Testing Scenarios
- **Small Dataset**: 100 offers, < 30 seconds
- **Medium Dataset**: 1000 offers, < 5 minutes
- **Large Dataset**: 10000 offers, < 30 minutes

## Monitoring and Alerting

### Success Criteria
- Sync job completes without errors
- All expected offers processed
- Database consistency maintained
- Performance metrics within bounds

### Failure Scenarios
- API timeout or connection errors
- Invalid data format received
- Database constraint violations
- Memory exhaustion

### Alerting Rules
- Sync duration exceeds 10 minutes
- Error rate > 5%
- Memory usage > 1GB
- Database connection failures 