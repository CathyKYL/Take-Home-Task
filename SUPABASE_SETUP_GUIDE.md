# Supabase Setup Guide - Step by Step

Follow these exact steps to set up your Supabase for the finance automation backend.

---

## Part 1: Create Storage Buckets (5 minutes)

### Step 1: Go to Storage

1. Open your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project: `fdyenyuevcdteropgoqi`
3. Click **Storage** in the left sidebar

### Step 2: Create `uploads` Bucket

1. Click **"New bucket"** (green button)
2. Fill in:
   - **Name**: `uploads`
   - **Public bucket**: ❌ UNCHECK (keep it private)
   - **File size limit**: Leave default (50 MB is fine)
3. Click **"Create bucket"**

### Step 3: Create `outputs` Bucket

1. Click **"New bucket"** again
2. Fill in:
   - **Name**: `outputs`
   - **Public bucket**: ❌ UNCHECK (keep it private)
   - **File size limit**: Leave default
3. Click **"Create bucket"**

✅ You should now see two buckets: `uploads` and `outputs`

---

## Part 2: Add Storage Policies (10 minutes)

Storage buckets are private by default. We need to add policies so your backend can access them.

### For `uploads` Bucket:

1. Click on the **`uploads`** bucket
2. Go to the **"Policies"** tab
3. Click **"New Policy"**
4. Click **"For full customization"** or **"Create policy"**

#### Policy 1: Service Role Full Access

```sql
-- Name: Service role full access
-- Allowed operation: ALL

CREATE POLICY "Service role full access"
ON storage.objects FOR ALL
TO service_role
USING (bucket_id = 'uploads');
```

**How to add:**
- Policy name: `Service role full access`
- Target roles: Select `service_role`
- Policy definition: `SELECT`, `INSERT`, `UPDATE`, `DELETE` (check all)
- WITH CHECK expression: `bucket_id = 'uploads'`
- USING expression: `bucket_id = 'uploads'`

Click **"Review"** then **"Save policy"**

---

### For `outputs` Bucket:

1. Click on the **`outputs`** bucket
2. Go to the **"Policies"** tab
3. Click **"New Policy"**

#### Policy 1: Service Role Full Access

```sql
-- Name: Service role full access
-- Allowed operation: ALL

CREATE POLICY "Service role full access"
ON storage.objects FOR ALL
TO service_role
USING (bucket_id = 'outputs');
```

**How to add:**
- Policy name: `Service role full access`
- Target roles: Select `service_role`
- Policy definition: Check all operations
- WITH CHECK expression: `bucket_id = 'outputs'`
- USING expression: `bucket_id = 'outputs'`

Click **"Review"** then **"Save policy"**

---

## Part 3: Enable Row Level Security on `runs` Table (3 minutes)

### Step 1: Enable RLS

1. Go to **Table Editor** in the left sidebar
2. Find and click on the **`runs`** table
3. Click the **🛡️ shield icon** at the top (or "Enable RLS" button)
4. Toggle **"Enable RLS"** ON

### Step 2: Add Service Role Policy

1. Still in the `runs` table, click **"Policies"** tab (or go to Authentication → Policies)
2. Click **"New Policy"**
3. Click **"Create a policy"** → **"For full customization"**

```sql
-- Name: Service role full access
-- Allowed operation: ALL

CREATE POLICY "Service role full access"
ON runs FOR ALL
TO service_role
USING (true);
```

**How to add:**
- Policy name: `Service role full access`
- Target roles: Select `service_role`
- Policy definition: Check ALL operations (SELECT, INSERT, UPDATE, DELETE)
- USING expression: `true`
- WITH CHECK expression: `true`

Click **"Review"** then **"Save policy"**

---

## Part 4: Verify Setup

### Quick Verification Checklist:

Go through each item and check:

**Storage:**
- [ ] `uploads` bucket exists and is private
- [ ] `uploads` bucket has "Service role full access" policy
- [ ] `outputs` bucket exists and is private
- [ ] `outputs` bucket has "Service role full access" policy

**Database:**
- [ ] `runs` table exists (from migration)
- [ ] `runs` table has RLS enabled
- [ ] `runs` table has "Service role full access" policy

**Visual Check:**

Storage → uploads → Policies:
```
✓ Service role full access (ALL operations)
```

Storage → outputs → Policies:
```
✓ Service role full access (ALL operations)
```

Table Editor → runs → RLS:
```
🛡️ RLS is enabled
✓ Service role full access (ALL operations)
```

---

## Part 5: Test the Setup (Optional but Recommended)

After setup, test that everything works:

```bash
# 1. Start your backend
uvicorn app.main:app --reload

# 2. In another terminal, run the demo
python scripts/demo_run.py
```

### Expected Results:

**In Terminal:**
- ✓ Run created
- ✓ Files uploaded
- ✓ Processing completed
- ✓ Download URL generated

**In Supabase Dashboard:**

1. **Table Editor → runs:**
   - Should see 1 new row
   - Status: "completed"
   - Has upload_date, file paths, run summary

2. **Storage → uploads:**
   - Should see a folder named with UUID (run_id)
   - Inside: 2 Excel files

3. **Storage → outputs:**
   - Should see a folder named with UUID (run_id)
   - Inside: 1 processed Excel file

---

## Troubleshooting

### "bucket does not exist"
- Make sure bucket names are exactly: `uploads` and `outputs` (lowercase, plural)

### "new row violates row-level security policy"
- Make sure RLS policies use `service_role` not `authenticated`
- Make sure USING expression is `true` not empty

### "insufficient permissions"
- Check that you're using the correct SUPABASE_KEY in your .env
- Make sure it's the service_role key, not the anon key

### "storage object not found"
- Check bucket policies include ALL operations
- Verify bucket_id in policy matches bucket name

---

## Summary

After completing these steps, you'll have:

✅ Two storage buckets for file uploads and outputs
✅ Proper policies allowing your backend to access them
✅ RLS enabled on runs table with service role access
✅ A working backend that can store data in Supabase

**Total time:** ~15-20 minutes

Once verified, you're ready to:
1. Deploy your backend (Render/Railway)
2. Build your frontend
3. Deploy to Netlify

---

## Need Help?

If you get stuck on any step, let me know which step and what error message you see!


