# Finance Automation Backend

Automates Accounts Payable processing with **guaranteed data integrity** - only modifies date stamp columns while preserving all original financial data.

---

## 📋 Prerequisites

- **Python 3.9+**
- **Supabase account** (free tier works)
- **Excel files** for testing (AP transactions + optional hold list)

---

## ⚙️ Setup

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

Get these from your Supabase project:
1. Go to **Project Settings** → **API**
2. Copy **Project URL** → `SUPABASE_URL`
3. Copy **anon/public key** → `SUPABASE_KEY`

### 3. Setup Supabase Database

Run the SQL migration in Supabase SQL Editor:

1. Open your Supabase project → **SQL Editor**
2. Copy contents of `migrations/001_create_runs_table.sql`
3. Execute the SQL

### 4. Create Supabase Storage Buckets

Create two storage buckets:

1. Go to **Storage** in Supabase dashboard
2. Click **New bucket**
3. Create bucket named: `uploads` (Private)
4. Create bucket named: `outputs` (Private)

---

## 🚀 Run the API Locally

```bash
# Start the server
uvicorn app.main:app --reload

# Or use the startup script
python run.py
```

Server runs at: **http://localhost:8000**  
API docs at: **http://localhost:8000/docs**

---

## 🔄 Complete Workflow (curl examples)

### Step 1: Create a Run

```bash
curl -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "upload_date": "2026-01-29",
  "status": "uploaded",
  "created_at": "2026-01-29T10:30:00Z"
}
```

*Save the `run_id` for next steps!*

---

### Step 2: Upload Files

```bash
curl -X POST http://localhost:8000/runs/{run_id}/upload \
  -F "ap_file=@/path/to/your/ap_transactions.xlsx" \
  -F "hold_file=@/path/to/your/hold_list.xlsx"
```

**Response:**
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "uploaded",
  "ap_upload_path": "550e8400-e29b-41d4-a716-446655440000/ap_transactions.xlsx",
  "hold_upload_path": "550e8400-e29b-41d4-a716-446655440000/hold_list.xlsx",
  "message": "Files uploaded successfully"
}
```

---

### Step 3: Inspect Schema & Get Mapping Suggestions

```bash
curl http://localhost:8000/runs/{run_id}/inspect
```

**Response includes:**
- Detected columns with data types
- Preview of first 15 rows
- **Suggested mappings** for required fields

```json
{
  "detected_columns": [...],
  "suggested_mapping": {
    "account_name": "Vendor Name",
    "created_date": "Created Date",
    "modified_date": "Last Modified Date"
  },
  "preview_data": [...]
}
```

---

### Step 4: Confirm Column Mapping

```bash
curl -X POST http://localhost:8000/runs/{run_id}/mapping \
  -H "Content-Type: application/json" \
  -d '{
    "mapping": {
      "account_name": "Vendor Name",
      "created_date": "Created Date",
      "modified_date": "Last Modified Date"
    },
    "format_config": {}
  }'
```

---

### Step 5: Process & Generate Output

```bash
curl -X POST http://localhost:8000/runs/{run_id}/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response with run summary:**
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "output_path": "550e8400-e29b-41d4-a716-446655440000/ap_output.xlsx",
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
  }
}
```

---

### Step 6: Download Output File

```bash
curl http://localhost:8000/runs/{run_id}/download
```

**Response:**
```json
{
  "download_url": "https://...signed-url-expires-in-1-hour...",
  "expires_in_seconds": 3600,
  "file_name": "ap_output.xlsx",
  "file_size_bytes": 45678
}
```

Use the `download_url` to download your processed Excel file!

---

## 🛡️ Data Integrity Guarantee

### The Golden Rule: **Only Date Columns Are Modified**

This system is designed for **financial data integrity**. Here's what happens:

#### ✅ What Gets Modified:
- **Created Date** column → Set to `upload_date` (date only, no time)
- **Last Modified Date** column → Set to `upload_date` (date only, no time)

#### ❌ What NEVER Gets Modified:
- Vendor names, amounts, invoice numbers, PO numbers, descriptions
- **ALL other financial data** remains **exactly as in the input file**
- No trimming, rounding, formatting changes, or type conversions

### Output Excel Structure (4 Tabs):

1. **Ready_To_Pay** - Transactions not on hold (with date stamps)
2. **Payment_On_Hold** - Transactions matching hold list (with date stamps)
3. **Hold_List** - Hold list values
4. **Raw** - **Exact copy of input** (completely unchanged)

### Reconciliation Check:

Every run includes automatic reconciliation:

```
Ready_To_Pay rows + Payment_On_Hold rows = Raw rows
```

If this doesn't match, the system flags it immediately. This ensures **no financial data is lost or duplicated**.

### How We Prove It:

Run the test suite to see mathematical proof:

```bash
pytest tests/test_data_integrity.py -v
```

These tests compare every cell in every row to prove only date columns changed.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run data integrity tests (the critical ones)
pytest tests/test_data_integrity.py -v

# Run with coverage report
pytest --cov=app --cov-report=html
```

**6 Critical Invariants Tested:**
1. Raw sheet row count = input row count
2. Ready + Hold = Raw (reconciliation)
3. **All non-date columns unchanged** (cell-by-cell comparison)
4. Date stamps = upload_date (date only)
5. Raw tab completely unchanged
6. Hold matching preserves original values

---

## 📊 API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/runs` | Create new run (sets upload_date to today) |
| POST | `/runs/{id}/upload` | Upload AP Excel + optional hold list |
| GET | `/runs/{id}/inspect` | Detect schema, suggest mappings |
| POST | `/runs/{id}/mapping` | Confirm column mappings |
| POST | `/runs/{id}/run` | Process files, generate output |
| GET | `/runs/{id}/download` | Get signed download URL (expires 1h) |
| GET | `/health` | Health check |

Interactive docs: **http://localhost:8000/docs**

---

## 🎬 Quick Demo (For Reviewers)

Want to see it in action? Run the demo script:

```bash
# 1. Create sample data
python scripts/create_sample_data.py

# 2. Start the API (in another terminal)
uvicorn app.main:app --reload

# 3. Run the demo
python scripts/demo_run.py
```

This runs the complete workflow with sample data and shows:
- Schema detection & mapping suggestions
- Data processing & reconciliation
- Download URL for the output Excel

See [`scripts/README.md`](scripts/README.md) for details.

---

## 🔧 Tech Stack

- **FastAPI** - Modern Python API framework
- **Supabase** - Postgres database + file storage
- **Pandas & openpyxl** - Excel processing
- **rapidfuzz** - Deterministic fuzzy matching (no AI)
- **pytest** - Testing framework

---

## 📁 Project Structure

```
├── app/
│   ├── main.py              # FastAPI app
│   ├── routes/runs.py       # API endpoints
│   ├── services/            # Supabase integration
│   ├── processing/          # Inspect & process logic
│   └── models/              # Pydantic schemas
├── migrations/              # Database migrations
├── tests/                   # Data integrity tests
├── requirements.txt
└── .env                     # Your credentials (not committed)
```

---

## 🔐 Security

- ✅ Secrets via environment variables only
- ✅ `.env` file is gitignored
- ✅ Signed URLs expire in 1 hour
- ✅ No hardcoded credentials

---

## 📖 Additional Documentation

- **[API_CONTRACT.md](API_CONTRACT.md)** - Complete API specification
- **[USAGE.md](USAGE.md)** - Detailed usage guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Implementation details

---

## 🎯 Key Features

✅ **Deterministic processing** - No AI, fully reproducible  
✅ **Data integrity enforced** - Only date columns modified  
✅ **Automatic reconciliation** - Ensures no data loss  
✅ **Fuzzy column matching** - Suggests mappings automatically  
✅ **Cloud-native** - Supabase for storage & database  
✅ **Fully tested** - Comprehensive test suite  

---

**Ready to process your AP files with confidence! 🚀**

