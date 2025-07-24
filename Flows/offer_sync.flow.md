# Offer Sync Flow Specification

## Overview
Automated synchronization of offers and brands from Trackier to Hissaback platform.

## Flow Steps

### 1. Fetch Brands from Trackier
- **Endpoint**: `GET /v2/advertisers` (Trackier API)
- **Headers**: `X-API-Key: {trackier_api_key}`
- **Action**: Upsert into `brands` table
- **Fields**: `brand_id`, `trackier_advertiser_id`, `name`, `logo_url`
- **Audit**: Store raw JSON payload in S3

### 2. Fetch Offers for Each Brand
- **Endpoint**: `GET /v2/campaigns?advertiser_id={brandId}` (Trackier API)
- **Headers**: `X-API-Key: {trackier_api_key}`
- **Action**: Upsert into `offers` table
- **Fields**: `offer_id`, `trackier_campaign_id`, `advertiser_id`, `category`, `base_commission_pct`
- **Audit**: Store raw JSON payload in S3
- **Optimization**: Use checksum to skip unchanged rows

### 3. Fetch Publishers (Optional - Admin View Only)
- **Endpoint**: `GET /v2/publishers` (Trackier API)
- **Headers**: `X-API-Key: {trackier_api_key}`
- **Action**: Update `tenants.trackier_pid` mapping
- **Audit**: Store raw JSON payload in S3

### 4. Sync Completion
- **Event**: Emit `sync.offers.completed` event
- **Payload**: Counts (inserted/updated/deactivated)
- **Metrics**: Duration, success/failure status

## Error Handling
- **Retry Logic**: 3 attempts with exponential backoff
- **Partial Failures**: Continue with other brands/offers
- **Alerting**: Notify on sync failures
- **Logging**: Detailed logs for debugging

## Scheduling
- **Nightly Job**: Run at 2 AM UTC
- **Manual Trigger**: Admin dashboard re-sync button
- **Monitoring**: Track sync duration and success rates

## Data Validation
- **Required Fields**: Ensure all mandatory fields are present
- **Data Types**: Validate field types match expected schema
- **Business Rules**: Check commission percentages are reasonable
- **Duplicate Detection**: Handle duplicate offers gracefully

## Performance Considerations
- **Batch Processing**: Process offers in batches of 100
- **Parallel Processing**: Fetch offers for multiple brands concurrently
- **Database Optimization**: Use bulk upsert operations
- **Memory Management**: Stream large responses to avoid memory issues 