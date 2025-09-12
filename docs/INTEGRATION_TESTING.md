# Integration Testing Guide

## Test Categories

### 1. API Endpoint Tests
```python
# Test valid URLs
test_scrape_valid_ikea_url()
test_scrape_valid_target_url()
test_scrape_valid_west_elm_url()

# Test invalid URLs
test_scrape_invalid_url()
test_scrape_unsupported_domain()
test_scrape_malformed_url()

# Test edge cases
test_scrape_url_with_special_characters()
test_scrape_very_long_url()
test_scrape_url_with_redirects()
```

### 2. Data Validation Tests
```python
# Test missing images
test_scrape_product_with_no_images()
test_scrape_product_with_invalid_images()

# Test malformed data
test_scrape_product_with_missing_fields()
test_scrape_product_with_invalid_dimensions()

# Test batch processing
test_batch_process_with_mixed_results()
test_batch_process_with_all_failures()
test_batch_process_with_large_dataset()
```

### 3. WebSocket Tests
```python
# Test real-time updates
test_websocket_connection()
test_websocket_progress_updates()
test_websocket_error_handling()

# Test concurrent connections
test_multiple_websocket_connections()
test_websocket_connection_drops()
```

### 4. Database Integration Tests
```python
# Test database operations
test_product_creation()
test_processing_stage_tracking()
test_batch_job_management()

# Test data consistency
test_product_data_integrity()
test_processing_stage_order()
test_batch_job_status_tracking()
```

## Running Tests

```bash
# Run all integration tests
python -m pytest tests/integration/ -v

# Run specific test categories
python -m pytest tests/integration/test_api_endpoints.py -v
python -m pytest tests/integration/test_websocket.py -v
python -m pytest tests/integration/test_database.py -v

# Run with coverage
python -m pytest tests/integration/ --cov=app --cov-report=html
```

## Test Data

Create test fixtures for:
- Valid product URLs from each retailer
- Invalid/malformed URLs
- Products with missing data
- Large batch datasets
- Edge case scenarios
