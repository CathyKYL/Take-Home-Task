# Audit Trail Requirements

## Overview

The frontend now displays a comprehensive audit trail on the Download page, showing all processing actions, overrides, and data transformations applied during the run.

## Backend Implementation Required

### 1. Audit Trail Data Collection

The backend should track and log the following events during processing:

#### Upload Phase
```json
{
  "timestamp": "2026-01-29T14:30:00Z",
  "action": "File Upload",
  "details": "Uploaded AP file: Example_AP_run_data.xlsx (150 rows)",
  "affected_rows": 150
}
```

#### Inspection Phase
```json
{
  "timestamp": "2026-01-29T14:30:05Z",
  "action": "Column Detection",
  "details": "Detected Account Name column: 'Account Name'",
  "affected_rows": null
}
```

#### Mapping Phase
```json
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
}
```

#### Processing Phase
```json
{
  "timestamp": "2026-01-29T14:30:45Z",
  "action": "Hold Detection",
  "details": "Matched 120 payments to hold list",
  "affected_rows": 120
},
{
  "timestamp": "2026-01-29T14:30:46Z",
  "action": "Override Applied",
  "details": "Applied 2 vendor name mappings",
  "affected_rows": 8
},
{
  "timestamp": "2026-01-29T14:30:47Z",
  "action": "Split Processing",
  "details": "Split into: 130 proceed, 20 on hold",
  "affected_rows": 150
}
```

#### Completion Phase
```json
{
  "timestamp": "2026-01-29T14:30:50Z",
  "action": "Processing Complete",
  "details": "Generated output files successfully",
  "affected_rows": null
}
```

### 2. Storage Options

The backend can provide audit trail data in two ways:

#### Option A: Inline in Download Response (Recommended for small runs)

Include `audit_trail` array directly in the GET `/runs/{runId}/download` response:

```json
{
  "excel_file_url": "https://...",
  "pdf_file_url": "https://...",
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
      "timestamp": "2026-01-29T14:30:30Z",
      "action": "Vendor Name Mapping",
      "details": "Mapped 'ACME LLC' → 'Acme, LLC'",
      "user": "user@example.com",
      "affected_rows": 5
    }
    // ... more entries
  ]
}
```

#### Option B: Separate Audit Trail File (Recommended for large runs)

Provide a signed URL to download the full audit trail as a JSON file:

```json
{
  "excel_file_url": "https://...",
  "pdf_file_url": "https://...",
  "audit_trail_url": "https://signed-url.com/audit_trail.json",
  "summary": {
    "total_payments": 150,
    "matched": 120,
    "unmatched": 10,
    "holds": 20
  }
}
```

The audit trail JSON file structure:
```json
{
  "run_id": "abc123",
  "created_at": "2026-01-29T14:30:00Z",
  "completed_at": "2026-01-29T14:30:50Z",
  "user": "user@example.com",
  "entries": [
    {
      "timestamp": "2026-01-29T14:30:00Z",
      "action": "File Upload",
      "details": "Uploaded AP file: Example_AP_run_data.xlsx (150 rows)",
      "affected_rows": 150
    }
    // ... more entries
  ]
}
```

#### Option C: Both (Best Practice)

Provide both inline summary entries and downloadable detailed log:
- Include key audit trail entries inline (last 20-50 entries)
- Provide complete audit trail as downloadable file

### 3. TypeScript Interface (Already Implemented in Frontend)

```typescript
interface AuditTrailEntry {
  timestamp: string        // ISO 8601 format
  action: string          // Action type (e.g., "File Upload", "Mapping Applied")
  details: string         // Human-readable description
  user?: string           // Optional: user who performed action
  affected_rows?: number  // Optional: number of rows affected
}

interface DownloadResponse {
  excel_file_url: string
  pdf_file_url?: string
  audit_trail_url?: string        // URL to download full audit trail
  summary?: {
    total_payments?: number
    matched?: number
    unmatched?: number
    holds?: number
  }
  audit_trail?: AuditTrailEntry[]  // Inline audit trail entries
}
```

## Recommended Audit Trail Events

### Essential Events (Must Track)

1. **File Upload**
   - Files received
   - Row counts
   - Processing date

2. **Column Mapping**
   - Detected columns
   - User confirmations/changes
   - Account name column selection

3. **Overrides Applied**
   - Vendor name mappings (each mapping)
   - Forced hold rules (each rule)
   - Number of rows affected by each

4. **Hold Detection**
   - How many rows matched hold list
   - Which matching logic was used

5. **Split Processing**
   - Final counts: proceed vs. on hold
   - Any warnings or issues

6. **Output Generation**
   - Files created
   - Completion status

### Optional Events (Nice to Have)

- Data validation steps
- Column normalization actions
- Date format conversions
- Error/warning occurrences
- Performance metrics (processing time)

## Backend Implementation Guide

### Python Example (FastAPI/Pydantic)

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class AuditTrailEntry(BaseModel):
    timestamp: str
    action: str
    details: str
    user: Optional[str] = None
    affected_rows: Optional[int] = None

class AuditTrail:
    def __init__(self, run_id: str, user: str = None):
        self.run_id = run_id
        self.user = user
        self.entries: List[AuditTrailEntry] = []
    
    def log(self, action: str, details: str, affected_rows: int = None):
        entry = AuditTrailEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            action=action,
            details=details,
            user=self.user,
            affected_rows=affected_rows
        )
        self.entries.append(entry)
        return entry
    
    def to_dict(self):
        return [entry.dict() for entry in self.entries]

# Usage in processing
def process_run(run_id: str):
    audit = AuditTrail(run_id, user="user@example.com")
    
    # Log file upload
    audit.log("File Upload", f"Uploaded AP file: {filename} ({row_count} rows)", row_count)
    
    # Log column detection
    audit.log("Column Detection", f"Detected Account Name column: '{account_col}'")
    
    # Log each override
    for hold_name, ap_name in overrides.hold_name_to_ap_name.items():
        affected = count_affected_rows(hold_name, ap_name)
        audit.log("Vendor Name Mapping", f"Mapped '{hold_name}' → '{ap_name}'", affected)
    
    for rule in overrides.row_level_holds:
        affected = count_matching_rows(rule.match_field, rule.match_value)
        audit.log("Forced Hold Rule", 
                 f"Force hold on {rule.match_field} = '{rule.match_value}'", 
                 affected)
    
    # Log processing results
    audit.log("Split Processing", 
             f"Split into: {proceed_count} proceed, {hold_count} on hold", 
             total_count)
    
    audit.log("Processing Complete", "Generated output files successfully")
    
    return audit.to_dict()
```

## Frontend Display

The frontend will display the audit trail as:

1. **Downloadable File** (if `audit_trail_url` provided)
   - Purple download card
   - "Audit Trail" button
   - Opens signed URL in new tab

2. **Inline Table** (if `audit_trail` array provided)
   - Scrollable table (max height 384px)
   - Columns: Timestamp | Action | Details | Rows Affected
   - Color-coded action badges:
     - Blue: Upload/Start actions
     - Purple: Mapping/Override actions
     - Green: Processing/Complete actions
     - Red: Hold/Force actions
     - Yellow: Match actions
     - Gray: Other actions

3. **Information Box**
   - Note explaining that no raw data was modified
   - Emphasizes audit transparency

## Testing

### Test Case 1: Simple Run (No Overrides)
Expected audit trail:
- File Upload
- Column Detection
- Hold Detection
- Split Processing
- Processing Complete

### Test Case 2: With Vendor Name Mappings
Additional entries:
- Vendor Name Mapping (one per mapping)
- Override Applied summary

### Test Case 3: With Forced Hold Rules
Additional entries:
- Forced Hold Rule (one per rule)
- Override Applied summary

### Test Case 4: Combined
All of the above entries in chronological order

## Security Considerations

1. **PII Protection**: Don't log sensitive payment details
2. **User Attribution**: Include user email/ID for accountability
3. **Immutability**: Audit trail should be append-only
4. **Retention**: Define how long audit trails are stored
5. **Access Control**: Only authorized users can view audit trails

## Performance Considerations

1. For runs with < 100 audit entries: Include inline in download response
2. For runs with > 100 audit entries: Use separate file download
3. Consider pagination for very large audit trails (frontend supports scrolling)
4. Cache generated audit trail files to avoid regeneration

---

## Summary

The frontend is **ready** to display audit trails. The backend needs to:

1. ✅ Track processing events in an audit log
2. ✅ Include overrides in the audit trail
3. ✅ Return audit trail in GET `/runs/{runId}/download` response
4. ✅ Optionally provide downloadable audit trail file

This maintains complete transparency and audit compliance while never modifying raw data.

