# Usage Guide

Complete guide for running and using the Finance Automation Backend.

## Prerequisites

1. **Python 3.9+** installed
2. **Supabase project** with:
   - `runs` table created (see `migrations/001_create_runs_table.sql`)
   - Storage buckets created: `uploads` and `outputs`
3. **Environment variables** configured (see Setup below)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key
```

### 3. Create Supabase Storage Buckets

In your Supabase dashboard:
1. Go to Storage
2. Create bucket: `uploads` (private)
3. Create bucket: `outputs` (private)

### 4. Run Database Migration

Copy the contents of `migrations/001_create_runs_table.sql` and execute in Supabase SQL Editor.

## Running the Server

### Development Mode

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Complete Workflow Example

### Step 1: Create a Run

```bash
curl -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response:
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "upload_date": "2026-01-29",
  "status": "uploaded",
  "created_at": "2026-01-29T10:30:00Z"
}
```

### Step 2: Upload Files

```bash
curl -X POST http://localhost:8000/runs/550e8400-e29b-41d4-a716-446655440000/upload \
  -F "ap_file=@/path/to/ap_file.xlsx" \
  -F "hold_file=@/path/to/hold_list.xlsx"
```

Response:
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "uploaded",
  "ap_upload_path": "550e8400-e29b-41d4-a716-446655440000/ap_file.xlsx",
  "hold_upload_path": "550e8400-e29b-41d4-a716-446655440000/hold_list.xlsx",
  "message": "Files uploaded successfully"
}
```

### Step 3: Inspect Schema

```bash
curl http://localhost:8000/runs/550e8400-e29b-41d4-a716-446655440000/inspect
```

Response includes:
- Detected columns with data types
- Preview of first 15 rows
- Suggested column mappings

### Step 4: Confirm Mapping

```bash
curl -X POST http://localhost:8000/runs/550e8400-e29b-41d4-a716-446655440000/mapping \
  -H "Content-Type: application/json" \
  -d '{
    "mapping": {
      "account_name": "Vendor Name",
      "created_date": "Created Date",
      "modified_date": "Last Modified Date"
    },
    "format_config": {
      "date_format": "YYYY-MM-DD"
    }
  }'
```

### Step 5: Process and Generate Output

```bash
curl -X POST http://localhost:8000/runs/550e8400-e29b-41d4-a716-446655440000/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response includes:
- Run summary with row counts
- Reconciliation validation (Ready + Hold = Raw)
- Missing account name count
- Processing time and file size

### Step 6: Download Output

```bash
curl http://localhost:8000/runs/550e8400-e29b-41d4-a716-446655440000/download
```

Response:
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "download_url": "https://...signed-url...",
  "expires_in_seconds": 3600,
  "file_name": "ap_output.xlsx",
  "file_size_bytes": 45678
}
```

Use the `download_url` to download the processed Excel file.

## Status Flow

```
created → uploaded → inspected → mapped → processing → completed
                                                     ↓
                                                  failed
```

## Output Excel Structure

The generated output file contains exactly 4 tabs:

1. **Ready_To_Pay** - Transactions not on hold (with stamped dates)
2. **Payment_On_Hold** - Transactions matching hold list (with stamped dates)
3. **Hold_List** - Hold list values
4. **Raw** - Original AP data (completely unchanged)

## Data Integrity Guarantees

✅ Only `Created Date` and `Last Modified Date` columns are modified  
✅ Raw tab is identical to input  
✅ Ready_To_Pay + Payment_On_Hold rows = Raw rows (reconciliation)  
✅ Date stamps use upload_date (date only, no time)  
✅ All other data values remain unchanged

## Running Tests

```bash
# Run all tests
pytest

# Run data integrity tests
pytest tests/test_data_integrity.py -v

# Run with coverage
pytest --cov=app --cov-report=html
```

## Troubleshooting

### "SUPABASE_URL environment variable is required"

Make sure you have a `.env` file in the root directory with your Supabase credentials.

### "Failed to create Supabase client"

Verify your `SUPABASE_URL` and `SUPABASE_KEY` are correct.

### "Bucket does not exist"

Create the `uploads` and `outputs` buckets in your Supabase Storage dashboard.

### "Table 'runs' does not exist"

Run the database migration from `migrations/001_create_runs_table.sql`.

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/runs` | Create new run |
| POST | `/runs/{run_id}/upload` | Upload files |
| GET | `/runs/{run_id}/inspect` | Inspect schema |
| POST | `/runs/{run_id}/mapping` | Confirm mapping |
| POST | `/runs/{run_id}/run` | Process files |
| GET | `/runs/{run_id}/download` | Get download URL |
| GET | `/runs/{run_id}` | Get run status |
| GET | `/` | Health check |

## Next Steps

Once the backend is running:
1. Test with sample AP files
2. Verify data integrity using the test suite
3. Build frontend to interact with these endpoints
4. Deploy to production environment

