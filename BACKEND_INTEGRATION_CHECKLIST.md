# Backend Integration Checklist

## Frontend Status: ✅ COMPLETE

The frontend is fully implemented and ready to display audit trails.

## Backend Requirements

### Phase 1: Override Support (From Previous Prompts)

#### ✅ Already Requested - Prompt A
**Extend `/mapping` schema to accept overrides**

```python
# Add to Pydantic model for POST /runs/{run_id}/mapping
class MappingRequest(BaseModel):
    account_name_column: str
    created_date_column: Optional[str] = None
    modified_date_column: Optional[str] = None
    overrides: Optional[Overrides] = None

class Overrides(BaseModel):
    hold_name_to_ap_name: dict[str, str] = {}
    row_level_holds: list[RowLevelHold] = []

class RowLevelHold(BaseModel):
    match_field: str
    match_value: str
    force_on_hold: bool
```

#### ✅ Already Requested - Prompt B
**Apply overrides in `process()` safely**

1. When normalizing vendor names, if hold name → AP name mapping exists, treat that AP account as "on hold"
2. For row_level_holds, force rows matching criteria to have on_hold = true
3. Don't modify original columns, only adjust processing logic

### Phase 2: Audit Trail Support (NEW)

#### Backend Prompt C - Add Audit Trail Logging

```
Add audit trail logging throughout the processing workflow:

1. Create an AuditTrail class that collects timestamped events with:
   - timestamp (ISO 8601)
   - action (string, e.g. "File Upload", "Vendor Name Mapping")
   - details (human-readable description)
   - user (optional, from auth context)
   - affected_rows (optional, count of rows impacted)

2. Log these key events:
   - File upload (with row count)
   - Column detection results
   - Each vendor name mapping applied (with affected row count)
   - Each forced hold rule applied (with affected row count)
   - Hold detection summary
   - Split processing results (proceed vs. on hold counts)
   - Processing completion

3. Store audit trail entries in:
   - Database table (for querying/analytics)
   - JSON file in storage (for download)
   - Or both

4. Important: Log WHAT was changed, not the actual payment data (PII protection)

Example log entries:
- "Mapped 'ACME LLC' → 'Acme, LLC' (5 rows affected)"
- "Force hold on Case Number = '12345' (3 rows affected)"
- "Split processing: 130 proceed, 20 on hold"
```

#### Backend Prompt D - Return Audit Trail in Download Endpoint

```
Update GET /runs/{run_id}/download endpoint to include audit trail:

Option 1 (Small runs < 100 entries):
Return audit_trail array directly in response:

{
  "excel_file_url": "...",
  "pdf_file_url": "...",
  "summary": { ... },
  "audit_trail": [
    {
      "timestamp": "2026-01-29T14:30:00Z",
      "action": "File Upload",
      "details": "Uploaded AP file (150 rows)",
      "affected_rows": 150
    },
    ...
  ]
}

Option 2 (Large runs > 100 entries):
Generate audit trail JSON file and return signed URL:

{
  "excel_file_url": "...",
  "pdf_file_url": "...",
  "audit_trail_url": "https://signed-url.com/audit_trail.json",
  "summary": { ... }
}

Option 3 (Best):
Return both - inline summary (last 20 entries) + full file download URL
```

## Implementation Priority

### Must Have (Required for basic functionality)
1. ✅ Override schema support (Prompt A)
2. ✅ Override application in processing (Prompt B)

### Should Have (Required for audit compliance)
3. ⚠️ Audit trail logging (Prompt C) - **NEW**
4. ⚠️ Audit trail in download response (Prompt D) - **NEW**

### Nice to Have (Enhanced audit features)
5. Audit trail search/filter API
6. Audit trail export in multiple formats (CSV, PDF)
7. Audit trail analytics/reporting

## Testing Checklist

### Test Override Functionality
- [ ] Vendor name mapping correctly matches holds
- [ ] Row-level forced holds work by identifier
- [ ] Multiple overrides can be applied together
- [ ] Overrides don't modify raw data

### Test Audit Trail
- [ ] All processing events are logged
- [ ] Timestamps are accurate and in ISO format
- [ ] Affected row counts are correct
- [ ] User attribution works (if applicable)
- [ ] Audit trail appears in download response
- [ ] Downloadable audit trail file works (if implemented)
- [ ] Frontend displays audit trail correctly

## Frontend Features Already Implemented

### Download Page Shows:
✅ Run summary (counts)
✅ Excel output download button
✅ PDF output download button (if available)
✅ **Audit trail download button** (purple card, if backend provides URL)
✅ **Audit trail table** (scrollable, color-coded, if backend provides data)
✅ Information note about audit transparency

### Audit Trail Display Features:
✅ Scrollable table (max 384px height)
✅ Color-coded action badges (blue/purple/green/red/yellow/gray)
✅ Formatted timestamps
✅ Rows affected count
✅ Action types: Upload, Mapping, Override, Processing, Hold, Complete
✅ Mobile responsive
✅ Information tooltip explaining no raw data was modified

## Example API Responses

### Minimal Response (No Audit Trail)
```json
{
  "excel_file_url": "https://storage.com/output.xlsx",
  "summary": {
    "total_payments": 150,
    "matched": 120,
    "unmatched": 10,
    "holds": 20
  }
}
```

### With Inline Audit Trail
```json
{
  "excel_file_url": "https://storage.com/output.xlsx",
  "pdf_file_url": "https://storage.com/report.pdf",
  "summary": {
    "total_payments": 150,
    "matched": 120,
    "unmatched": 10,
    "holds": 20
  },
  "audit_trail": [
    {
      "timestamp": "2026-01-29T14:30:00Z",
      "action": "File Upload",
      "details": "Uploaded AP file: Example_AP_run_data.xlsx (150 rows)",
      "user": "user@example.com",
      "affected_rows": 150
    },
    {
      "timestamp": "2026-01-29T14:30:05Z",
      "action": "Column Detection",
      "details": "Detected Account Name column: 'Account Name'"
    },
    {
      "timestamp": "2026-01-29T14:30:30Z",
      "action": "Vendor Name Mapping",
      "details": "Mapped 'ACME LLC' → 'Acme, LLC'",
      "affected_rows": 5
    },
    {
      "timestamp": "2026-01-29T14:30:31Z",
      "action": "Forced Hold Rule",
      "details": "Force hold on Case Number = '12345'",
      "affected_rows": 3
    },
    {
      "timestamp": "2026-01-29T14:30:45Z",
      "action": "Split Processing",
      "details": "Split into: 130 proceed, 20 on hold",
      "affected_rows": 150
    },
    {
      "timestamp": "2026-01-29T14:30:50Z",
      "action": "Processing Complete",
      "details": "Generated output files successfully"
    }
  ]
}
```

### With Audit Trail File Download
```json
{
  "excel_file_url": "https://storage.com/output.xlsx",
  "pdf_file_url": "https://storage.com/report.pdf",
  "audit_trail_url": "https://storage.com/audit_trail.json",
  "summary": {
    "total_payments": 150,
    "matched": 120,
    "unmatched": 10,
    "holds": 20
  }
}
```

## Next Steps

1. **Implement Override Support** (if not done yet)
   - Run Backend Prompt A in your backend codebase
   - Run Backend Prompt B in your backend codebase
   - Test override functionality

2. **Implement Audit Trail** (new requirement)
   - Run Backend Prompt C (create audit trail logging)
   - Run Backend Prompt D (return audit trail in download response)
   - Test audit trail display in frontend

3. **Deploy & Test**
   - Deploy backend changes
   - Test full workflow in frontend
   - Verify audit trail appears correctly
   - Verify overrides work as expected

## Questions?

See `AUDIT_TRAIL_REQUIREMENTS.md` for detailed technical specifications on the audit trail implementation.

