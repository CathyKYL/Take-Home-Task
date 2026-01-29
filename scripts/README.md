# Demo Scripts

Quick demo scripts for testing and reviewing the Finance Automation Backend.

## 🚀 Quick Start (For Reviewers)

### 1. Create Sample Data

```bash
python scripts/create_sample_data.py
```

This creates:
- `sample_data/sample_ap_transactions.xlsx` (10 transactions)
- `sample_data/sample_hold_list.xlsx` (3 vendors on hold)

### 2. Start the API Server

```bash
# In a separate terminal
uvicorn app.main:app --reload
```

### 3. Run the Demo

```bash
python scripts/demo_run.py
```

## 📋 What the Demo Does

The `demo_run.py` script demonstrates the complete workflow:

1. ✅ **Create Run** - Creates a new processing run
2. ✅ **Upload Files** - Uploads sample AP transactions and hold list
3. ✅ **Inspect Schema** - Detects columns and suggests mappings
4. ✅ **Confirm Mapping** - Confirms the suggested column mapping
5. ✅ **Process Files** - Processes data and generates output
6. ✅ **Download Output** - Gets signed URL for downloading result

## 📊 Sample Data

### AP Transactions (10 rows)
- **Columns**: Vendor Name, Invoice Number, Amount, Description, Due Date, PO Number, Invoice Date
- **Total Amount**: $23,820.25
- **Expected Output**:
  - Ready to Pay: 7 transactions
  - Payment on Hold: 3 transactions (Tech Solutions Inc, Hardware Store Co, Legal Services LLP)

### Hold List (3 vendors)
- Tech Solutions Inc
- Hardware Store Co
- Legal Services LLP

## 🎯 Expected Results

After running the demo, you should see:

```
📊 Run Summary:
   Total Raw Rows:          10
   Ready to Pay Rows:       7
   Payment on Hold Rows:    3
   Hold List Rows:          3

✔️  Reconciliation: Ready_To_Pay (7) + Payment_On_Hold (3) = Raw (10). ✓
```

## 🔍 Verification

The demo proves:

1. **Data Integrity** - Only date columns modified
2. **Reconciliation** - Ready + Hold = Raw (7 + 3 = 10)
3. **Hold List Matching** - 3 vendors correctly identified
4. **Output Structure** - 4 tabs generated

Download the output Excel file using the provided URL and verify:
- Ready_To_Pay tab has 7 rows with "Created Date" and "Last Modified Date" stamped
- Payment_On_Hold tab has 3 rows with date stamps
- Hold_List tab has the 3 hold vendors
- Raw tab has all 10 original rows unchanged

## 🛠️ Troubleshooting

### "Cannot connect to API"
Make sure the server is running:
```bash
uvicorn app.main:app --reload
```

### "Sample files not found"
Run the sample data creation script first:
```bash
python scripts/create_sample_data.py
```

### "SUPABASE_URL environment variable is required"
Create a `.env` file with your Supabase credentials (see main README).

## 📝 Notes

- The demo uses real API calls (not mocked)
- Sample data is realistic but minimal for quick demos
- Download URLs expire in 1 hour
- Run summary includes reconciliation check


