# Test Suite

Comprehensive tests proving data integrity for the finance automation backend.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_data_integrity.py

# Run specific test
pytest tests/test_data_integrity.py::TestDataIntegrity::test_raw_sheet_equals_input_row_count

# Verbose output
pytest -v
```

## Test Categories

### Data Integrity Tests (`test_data_integrity.py`)

**CRITICAL FOR FINANCE** - These tests prove that processing only modifies the two date stamp columns.

#### Invariants Tested:

1. ✅ **Raw sheet row count equals input** - No rows lost or added
2. ✅ **Ready + Hold = Raw** - Perfect reconciliation
3. ✅ **Non-date columns unchanged** - All original data preserved
4. ✅ **Date stamps correct** - Upload date applied, date-only values
5. ✅ **Raw tab immutable** - Completely unchanged from input
6. ✅ **Hold matching preserves values** - Original case/formatting preserved

### Inspect Tests (`test_inspect.py`)

Tests for the inspection functionality:
- Correct data structure returned
- Row count detection
- Preview limited to 15 rows
- Mapping suggestions
- No data modification during inspection

### Error Handling Tests (`test_process_errors.py`)

Tests for proper error handling:
- Missing required mappings
- Invalid column names
- Processing without hold list

## Test Data

Tests use synthetic data defined in `conftest.py`:
- 5 sample AP transactions
- 2 vendors in hold list
- Realistic column names and data types

## Coverage Goals

- **100% coverage** for `app/processing/` (critical business logic)
- **90%+ coverage** for `app/services/` (Supabase integration)
- **Focus on invariants** over implementation details

## Continuous Integration

These tests should run on every commit to ensure data integrity is never compromised.


