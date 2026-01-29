# API Contract Documentation

Backend API for finance/accounting automation with Supabase.

## Base URL
```
http://localhost:8000
```

---

## Endpoints

### 1. Create Run
**POST** `/runs`

Creates a new processing run and sets upload_date to today's UTC date.

**Request Body:**
```json
{
  "upload_date": "2026-01-29"  // Optional, defaults to today UTC
}
```

**Response:** `201 Created`
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "upload_date": "2026-01-29",
  "status": "uploaded",
  "created_at": "2026-01-29T10:30:00Z"
}
```

---

### 2. Upload Files
**POST** `/runs/{run_id}/upload`

Upload AP Excel file and optional Hold List file to Supabase Storage.

**Request:** `multipart/form-data`
- `ap_file`: Excel file (required)
- `hold_file`: Excel file (optional)

**Response:** `200 OK`
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "uploaded",
  "ap_upload_path": "uploads/550e8400-e29b-41d4-a716-446655440000/ap_file.xlsx",
  "hold_upload_path": "uploads/550e8400-e29b-41d4-a716-446655440000/hold_list.xlsx",
  "message": "Files uploaded successfully"
}
```

---

### 3. Inspect Schema & Preview
**GET** `/runs/{run_id}/inspect`

Analyzes uploaded file, detects schema, provides preview, and suggests column mappings using deterministic fuzzy matching.

**Response:** `200 OK`
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "inspected",
  "detected_columns": [
    {
      "name": "Vendor Name",
      "data_type": "string",
      "sample_values": ["ACME Corp", "Tech Solutions Inc", "Office Supplies Ltd"],
      "null_count": 0,
      "total_count": 150
    },
    {
      "name": "Invoice Number",
      "data_type": "string",
      "sample_values": ["INV-001", "INV-002", "INV-003"],
      "null_count": 0,
      "total_count": 150
    },
    {
      "name": "Amount",
      "data_type": "number",
      "sample_values": [1500.00, 2300.50, 750.00],
      "null_count": 0,
      "total_count": 150
    },
    {
      "name": "Due Date",
      "data_type": "date",
      "sample_values": ["2026-02-15", "2026-03-01", "2026-02-28"],
      "null_count": 5,
      "total_count": 150
    }
  ],
  "total_rows": 150,
  "required_fields": [
    "vendor_name",
    "invoice_number",
    "amount",
    "due_date",
    "account_name",
    "description"
  ],
  "suggested_mapping": {
    "vendor_name": "Vendor Name",
    "invoice_number": "Invoice Number",
    "amount": "Amount",
    "due_date": "Due Date",
    "account_name": "Account",
    "description": "Description"
  },
  "suggestions": [
    {
      "required_field": "vendor_name",
      "suggested_column": "Vendor Name",
      "confidence": "high",
      "reason": "Exact match found"
    },
    {
      "required_field": "account_name",
      "suggested_column": "Account",
      "confidence": "medium",
      "reason": "Fuzzy match (similarity: 85%)"
    }
  ],
  "preview_data": [
    {
      "Vendor Name": "ACME Corp",
      "Invoice Number": "INV-001",
      "Amount": 1500.00,
      "Due Date": "2026-02-15",
      "Account": "Office Expenses",
      "Description": "Monthly supplies"
    },
    {
      "Vendor Name": "Tech Solutions Inc",
      "Invoice Number": "INV-002",
      "Amount": 2300.50,
      "Due Date": "2026-03-01",
      "Account": "IT Services",
      "Description": "Software licenses"
    }
  ]
}
```

---

### 4. Confirm Mapping
**POST** `/runs/{run_id}/mapping`

Save user-confirmed column mapping and format configuration.

**Request Body:**
```json
{
  "mapping": {
    "vendor_name": "Vendor Name",
    "invoice_number": "Invoice Number",
    "amount": "Amount",
    "due_date": "Due Date",
    "account_name": "Account",
    "description": "Description",
    "invoice_date": "Invoice Date",
    "po_number": "PO #"
  },
  "format_config": {
    "date_format": "YYYY-MM-DD",
    "currency_symbol": "$",
    "decimal_places": 2
  }
}
```

**Response:** `200 OK`
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "inspected",
  "confirmed_mapping": {
    "vendor_name": "Vendor Name",
    "invoice_number": "Invoice Number",
    "amount": "Amount",
    "due_date": "Due Date",
    "account_name": "Account",
    "description": "Description",
    "invoice_date": "Invoice Date",
    "po_number": "PO #"
  },
  "format_config": {
    "date_format": "YYYY-MM-DD",
    "currency_symbol": "$",
    "decimal_places": 2
  },
  "message": "Mapping confirmed and saved"
}
```

---

### 5. Process & Generate Output
**POST** `/runs/{run_id}/run`

Processes the uploaded files with confirmed mapping, generates output Excel with tabs (Ready_To_Pay, Payment_On_Hold, Hold_List, Raw), and uploads to Supabase Storage.

**Request Body:** (optional, for future extensions)
```json
{}
```

**Response:** `200 OK`
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "output_path": "outputs/550e8400-e29b-41d4-a716-446655440000/processed_output.xlsx",
  "run_summary": {
    "total_raw_rows": 150,
    "ready_to_pay_rows": 120,
    "payment_on_hold_rows": 30,
    "hold_list_rows": 15,
    "reconciliation_valid": true,
    "reconciliation_message": "Ready_To_Pay (120) + Payment_On_Hold (30) = Raw (150). ✓",
    "missing_account_name_count": 5,
    "processing_time_seconds": 2.34,
    "output_file_size_bytes": 45678
  },
  "error_message": null
}
```

**Response (Failed):** `200 OK`
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "output_path": null,
  "run_summary": null,
  "error_message": "Missing required column: 'vendor_name' not found in uploaded file"
}
```

---

### 6. Download Output
**GET** `/runs/{run_id}/download`

Returns a signed URL for downloading the processed output Excel file from Supabase Storage.

**Response:** `200 OK`
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "download_url": "https://fdyenyuevcdteropgoqi.supabase.co/storage/v1/object/sign/outputs/550e8400-e29b-41d4-a716-446655440000/processed_output.xlsx?token=eyJ...",
  "expires_in_seconds": 3600,
  "file_name": "processed_output.xlsx",
  "file_size_bytes": 45678
}
```

---

## Error Responses

All endpoints may return error responses:

**400 Bad Request:**
```json
{
  "error": "Invalid request",
  "detail": "Missing required field: mapping",
  "run_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**404 Not Found:**
```json
{
  "error": "Run not found",
  "detail": "No run exists with id: 550e8400-e29b-41d4-a716-446655440000",
  "run_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error",
  "detail": "Failed to connect to Supabase Storage",
  "run_id": null
}
```

---

## Data Integrity Rules

1. **Raw tab immutability**: The Raw tab reflects the imported AP sheet exactly as read
2. **Date stamping**: Created Date and Last Modified Date use `upload_date` (date only, no time)
3. **Output tabs**: Exactly four tabs - Ready_To_Pay, Payment_On_Hold, Hold_List, Raw
4. **Auditability**: Every run produces a summary with row counts and reconciliation check
5. **Reconciliation**: `ready_to_pay_rows + payment_on_hold_rows` must equal `total_raw_rows`


