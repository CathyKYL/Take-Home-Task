# Processing Module

Business logic for inspecting and processing AP Excel files.

## inspect.py

### `inspect_ap_excel(ap_bytes: bytes) -> dict`

**READ-ONLY** inspection function that extracts schema and suggests mappings.

**Important:** This function does NOT transform or clean data - inspection only.

#### Returns:

```python
{
    "sheet_names": ["Sheet1", "Sheet2"],
    "selected_sheet": "Sheet1",
    "columns": ["Vendor Name", "Invoice Number", "Amount", ...],
    "normalized_columns": ["vendor name", "invoice number", "amount", ...],
    "total_rows": 150,
    "preview_rows": [
        {
            "Vendor Name": "ACME Corp",
            "Invoice Number": "INV-001",
            "Amount": 1500.00,
            ...
        },
        # ... up to 15 rows
    ],
    "mapping_suggestions": {
        "account_name": {
            "field": "account_name",
            "suggested_column": "Vendor Name",
            "confidence": "high",
            "score": 95.0,
            "reason": "Fuzzy match with 'vendor' (similarity: 95%)",
            "alternatives": [
                {"column": "Payee", "confidence": "medium", "score": 78.0}
            ]
        },
        "created_date": {...},
        "modified_date": {...}
    },
    "suggested_mapping": {
        "account_name": "Vendor Name",
        "created_date": "Created Date",
        "modified_date": "Last Modified"
    }
}
```

#### Field Candidates for Fuzzy Matching:

- **account_name**: "servicer: account name", "account name", "payee", "vendor", "supplier"
- **created_date**: "created date", "date created", "created_at"
- **modified_date**: "last modified date", "modified date", "updated_at", "date modified"

#### Confidence Levels:

- **high**: Score >= 90%
- **medium**: Score >= 75%
- **low**: Score >= 60%

#### Fuzzy Matching:

Uses `rapidfuzz` library with `fuzz.ratio` scorer for deterministic string similarity matching.

---

### `get_column_info(ap_bytes: bytes) -> List[dict]`

Extract detailed column information for API response.

#### Returns:

```python
[
    {
        "name": "Vendor Name",
        "data_type": "string",  # "string", "number", "date", "boolean"
        "sample_values": ["ACME Corp", "Tech Solutions Inc", "Office Supplies Ltd"],
        "null_count": 0,
        "total_count": 150
    },
    ...
]
```

---

---

## process.py

### `process_run(ap_bytes, hold_bytes, mapping, format_config, upload_date) -> (output_bytes, run_summary_dict)`

Processes AP Excel file and generates output with 4 tabs.

**CRITICAL DATA INTEGRITY:** Only modifies Created Date and Last Modified Date columns. All other values remain unchanged.

#### Parameters:

- `ap_bytes`: AP Excel file as bytes
- `hold_bytes`: Hold list Excel file as bytes (optional)
- `mapping`: Column mapping dict (e.g., `{"account_name": "Vendor Name", "created_date": "Created Date"}`)
- `format_config`: Format configuration (reserved for future use)
- `upload_date`: Date to stamp (date only, no time)

#### Process Flow:

1. Read AP file into `raw_df` (immutable)
2. Copy to `working_df` for processing
3. Load hold list into normalized set
4. Determine on_hold using normalized matching (original values preserved)
5. Split into `ready_df` and `hold_df`
6. Add/update Created Date and Last Modified Date columns with `upload_date`
7. Generate Excel with 4 tabs: **Ready_To_Pay**, **Payment_On_Hold**, **Hold_List**, **Raw**

#### Returns:

```python
(
    output_bytes,  # Excel file as bytes
    {
        "total_raw_rows": 150,
        "ready_to_pay_rows": 120,
        "payment_on_hold_rows": 30,
        "hold_list_rows": 15,
        "reconciliation_valid": True,
        "reconciliation_message": "Ready_To_Pay (120) + Payment_On_Hold (30) = Raw (150). ✓",
        "missing_account_name_count": 5
    }
)
```

#### Output Excel Tabs (Exact Order):

1. **Ready_To_Pay** - Transactions not on hold, with stamped dates
2. **Payment_On_Hold** - Transactions matching hold list, with stamped dates
3. **Hold_List** - Hold list values as simple table
4. **Raw** - Original AP data, completely unchanged

#### Date Stamping:

- Uses mapped column names if provided in mapping (`created_date`, `modified_date`)
- Otherwise creates columns named exactly: `"Created Date"` and `"Last Modified Date"`
- Sets both columns to `upload_date` (date only, no time component)

#### Hold List Matching:

- Normalized string matching (lowercase, stripped)
- Original values in data are NEVER modified
- Only matching logic uses normalization

---

## Data Integrity Rules

### inspect.py
✅ **NO data transformation** - Original values preserved  
✅ **NO data cleaning** - Inspect only  
✅ **JSON-serializable** - All output can be serialized to JSON  
✅ **Deterministic** - Same input always produces same output  
✅ **No AI APIs** - Pure fuzzy matching logic

### process.py
✅ **ONLY modify Created Date and Last Modified Date** - All other columns unchanged  
✅ **Raw tab immutability** - Raw tab is exact copy of input  
✅ **Reconciliation enforced** - Ready + Hold must equal Raw  
✅ **Date only stamping** - No time component  
✅ **Output tab order** - Exactly: Ready_To_Pay, Payment_On_Hold, Hold_List, Raw  
✅ **Auditability** - Full run summary with counts and validation

