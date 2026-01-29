# Quick Start Guide for Reviewers

Get the Finance Automation Backend running in under 5 minutes! 🚀

---

## Prerequisites Check

- ✅ Python 3.9+ installed
- ✅ Supabase account (free tier is fine)
- ✅ 5 minutes of your time

---

## Step 1: Install Dependencies (30 seconds)

```bash
pip install -r requirements.txt
```

---

## Step 2: Setup Environment (1 minute)

### Create `.env` file:

```bash
# Copy example and edit
cp .env.example .env
```

### Add your Supabase credentials to `.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
```

**Where to find these:**
1. Go to your Supabase project → Settings → API
2. Copy "Project URL" → `SUPABASE_URL`
3. Copy "anon/public key" → `SUPABASE_KEY`

---

## Step 3: Setup Supabase (2 minutes)

### A. Create Database Table

1. Open Supabase → **SQL Editor**
2. Copy all of `migrations/001_create_runs_table.sql`
3. Execute it

### B. Create Storage Buckets

1. Go to **Storage** → **New bucket**
2. Create: `uploads` (Private)
3. Create: `outputs` (Private)

---

## Step 4: Run the Demo (1 minute)

```bash
# Terminal 1: Start the API
uvicorn app.main:app --reload

# Terminal 2: Run the demo
python scripts/create_sample_data.py
python scripts/demo_run.py
```

---

## 🎉 What You'll See

The demo script will:

1. ✅ Create a run
2. ✅ Upload sample files (10 AP transactions, 3 on hold)
3. ✅ Inspect schema and suggest mappings
4. ✅ Confirm mapping
5. ✅ Process files
6. ✅ Show download URL and run summary

### Expected Output:

```
📊 Run Summary:
   Total Raw Rows:          10
   Ready to Pay Rows:       7
   Payment on Hold Rows:    3
   Hold List Rows:          3

✔️  Reconciliation: Ready_To_Pay (7) + Payment_On_Hold (3) = Raw (10). ✓

⚠️  Missing Account Names: 0
   Processing Time:         2.34s
```

---

## 🔍 Verify Data Integrity

Download the output Excel using the URL from the demo, and check:

1. **Ready_To_Pay** tab (7 rows)
   - Has "Created Date" and "Last Modified Date" columns
   - All other data is unchanged from input

2. **Payment_On_Hold** tab (3 rows)
   - Same date columns added
   - Original data preserved

3. **Hold_List** tab
   - Shows the 3 hold vendors

4. **Raw** tab (10 rows)
   - **Exact copy of input** - no changes at all

---

## 🧪 Run Tests

Prove data integrity with tests:

```bash
# Run all tests
pytest -v

# Run just the critical data integrity tests
pytest tests/test_data_integrity.py -v
```

These tests mathematically prove that only date columns are modified.

---

## 📖 Interactive API Docs

Visit: **http://localhost:8000/docs**

Try the endpoints interactively with Swagger UI!

---

## 🎯 Key Features Demonstrated

✅ **Deterministic fuzzy matching** - No AI, fully reproducible  
✅ **Data integrity** - Only 2 columns modified, all else preserved  
✅ **Reconciliation** - Automatic check: Ready + Hold = Raw  
✅ **Hold list matching** - Case-insensitive but preserves original values  
✅ **4 output tabs** - Proper separation of data  
✅ **Auditability** - Complete run summary with counts  

---

## 📚 More Documentation

- **[README.md](README.md)** - Full documentation with curl examples
- **[API_CONTRACT.md](API_CONTRACT.md)** - Complete API specification
- **[USAGE.md](USAGE.md)** - Detailed usage guide
- **[scripts/README.md](scripts/README.md)** - Demo script details
- **[tests/README.md](tests/README.md)** - Test suite documentation

---

## 🛠️ Troubleshooting

### "Cannot connect to API"
→ Make sure the API is running: `uvicorn app.main:app --reload`

### "SUPABASE_URL required"
→ Create `.env` file with your Supabase credentials

### "Bucket does not exist"
→ Create `uploads` and `outputs` buckets in Supabase Storage

### "Sample files not found"
→ Run: `python scripts/create_sample_data.py`

---

## 🏗️ Project Structure

```
├── app/                    # Main application
│   ├── routes/            # API endpoints
│   ├── services/          # Supabase integration
│   ├── processing/        # Business logic
│   └── models/            # Pydantic schemas
├── migrations/            # SQL migrations
├── tests/                 # Test suite (data integrity proofs)
├── scripts/               # Demo scripts
├── requirements.txt       # Dependencies
└── .env                   # Your credentials (not committed)
```

---

**Ready to explore? Start with the demo script!** 🚀

```bash
python scripts/demo_run.py
```

