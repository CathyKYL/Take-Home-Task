# Quick Start - Test the Frontend NOW

## 🚀 Start Testing in 2 Minutes (No Backend Required!)

### Step 1: Install & Run

```bash
npm install
npm run dev
```

### Step 2: Open Browser

Go to: **http://localhost:3000?mock=true**

That's it! Mock mode is enabled automatically.

---

## 🎯 What You'll See

### Yellow Banner at Top
```
⚠️ Mock Mode Active - Testing UI Without Backend
[Disable] [Go to Upload] [Jump to Confirm] [Jump to Download]
```

### Quick Navigation Buttons

- **Go to Upload** - Test file upload UI
- **Jump to Confirm** - See the full confirmation page with data
- **Jump to Download** - View download page with audit trail

---

## 🧪 Test Each Feature

### 1️⃣ Upload Step (Step 1 of 4)

**Test:**
- Drag files into upload boxes
- Click to browse files
- Try invalid file types (should show error)
- Try files > 10MB (should show error)
- Select processing date
- Watch "Start Processing" button enable/disable

**Note:** Files are validated locally but not actually uploaded (no backend)

### 2️⃣ Jump to Confirm (Step 3 of 4)

Click **"Jump to Confirm"** button

**See:**
- ✅ Run summary with counts
- ✅ Detected column mappings (Account Name, Created Date, Modified Date)
- ✅ Data preview table (first 3 rows)
- ✅ Column confirmation dropdowns
- ✅ Unmatched hold names warning (3 names)
- ✅ Manual matching options

**Test Manual Vendor Name Mapping:**
1. Click **"Manual Match"** button
2. See manual matching mode
3. Select "ACME LLC" from left dropdown
4. Select "Acme, LLC" from right dropdown
5. Click **"Add Mapping"**
6. See mapping in table below
7. Click trash icon to remove

**Test Manual Hold Rules:**
1. Scroll to purple "Manual Match (By Identifier)" section
2. Select "Case Number" from dropdown
3. Type "12345" in value field
4. Click **"Add Forced Hold Rule"**
5. See rule in table below
6. Click trash icon to remove

**Test Process:**
1. Ensure Account Name column is selected
2. Optionally add mappings/rules
3. Click **"Run Processing"** button
4. Shows "Processing & Running..." spinner
5. Jumps to Download step

### 3️⃣ Jump to Download (Step 4 of 4)

Click **"Jump to Download"** button

**See:**
- ✅ Green success banner
- ✅ Run summary (150 total, 120 matched, 10 unmatched, 20 holds)
- ✅ Three download buttons:
  - Excel Output File (blue)
  - PDF Report (red)
  - Audit Trail (purple)
- ✅ Audit trail table with 8 entries
- ✅ Scrollable table with color-coded actions
- ✅ Information note about data integrity

**Test:**
- Click download buttons (opens example URLs)
- Scroll audit trail table
- See color-coded action badges
- Click **"Process Another File"** to reset

---

## ✅ Feature Checklist

Test everything works:

### Visual Design
- [ ] Clean, professional UI
- [ ] Consistent colors (blue primary, purple accents)
- [ ] Proper spacing and alignment
- [ ] Readable fonts and sizes
- [ ] Icons display correctly

### Upload Step
- [ ] File upload boxes appear
- [ ] Drag & drop zones work
- [ ] Click to browse works
- [ ] Selected files show name & size
- [ ] Remove file button works
- [ ] Date picker shows today by default
- [ ] Can change date
- [ ] Button enables only when both files selected
- [ ] Validation messages show

### Confirm Step
- [ ] Summary counts display
- [ ] Column mappings show
- [ ] Data preview table renders
- [ ] All columns visible
- [ ] Column dropdowns work
- [ ] Can change column selections
- [ ] Unmatched warning appears
- [ ] Manual match button works
- [ ] Vendor mapping UI works
- [ ] Add/remove mappings works
- [ ] Identifier hold rules work
- [ ] Add/remove rules works
- [ ] Process button disables if no account column
- [ ] Status messages update

### Download Step
- [ ] Success banner shows
- [ ] Summary counts correct
- [ ] Download buttons appear
- [ ] Button hover effects work
- [ ] Audit trail table displays
- [ ] Table scrolls smoothly
- [ ] Action badges color-coded
- [ ] Timestamps formatted nicely
- [ ] Row counts show
- [ ] Info note displays
- [ ] Start over button works

### Responsive Design
- [ ] Works on desktop (1920px+)
- [ ] Works on laptop (1366px)
- [ ] Works on tablet (768px)
- [ ] Works on mobile (375px)

---

## 🔄 Test the Full Flow

### Scenario 1: No Issues
1. Start at Upload
2. "Select" two files (just click upload boxes)
3. In mock mode, click through to Confirm step manually
4. Review data
5. Ensure account column selected
6. Click "Run Processing"
7. See download page
8. View audit trail

### Scenario 2: With Manual Matching
1. Jump to Confirm
2. Click "Manual Match"
3. Add 2 vendor name mappings
4. Add 1 forced hold rule
5. Click "Done - Proceed with 3 Overrides"
6. Click "Run Processing"
7. See success

### Scenario 3: Skip Manual Matching
1. Jump to Confirm
2. See unmatched warning
3. Click "Proceed Anyway"
4. Click "Run Processing"
5. See warning about unmatched names
6. Still proceeds to download

---

## 🎨 Visual Tour

### Upload Page
```
┌─────────────────────────────────────┐
│ Bill.com Processing                 │
│ Process Bill.com vendor payments... │
│                                     │
│ [Yellow Banner - Mock Mode Active] │
│                                     │
│ Step 1 of 4                         │
│                                     │
│ ○ File Upload                       │
│                                     │
│ Input Files                         │
│ Vendor Payment Excel File *         │
│ [Drop file or click to browse]     │
│                                     │
│ Payment Hold List File *            │
│ [Drop file or click to browse]     │
│                                     │
│ Parameters                          │
│ Processing Date                     │
│ [01/29/2026 📅]                     │
│                                     │
│ ⚠️ Both files required to proceed  │
│                                     │
│ [Start Processing] (disabled)       │
└─────────────────────────────────────┘
```

### Confirm Page (with warnings)
```
┌─────────────────────────────────────┐
│ Step 3 of 4                         │
│                                     │
│ Confirm / Manual Match              │
│                                     │
│ [Gray] Summary (6 metrics)          │
│ [Blue] Column Mappings              │
│ [White] Column Selection            │
│ [Table] Data Preview                │
│                                     │
│ [Orange] ⚠️ 3 Hold Names Not Found │
│ • ACME LLC                          │
│ • ABC Industries                    │
│ • Tech Solutions Inc                │
│                                     │
│ [Manual Match] [Proceed] [Skip]     │
└─────────────────────────────────────┘
```

### Download Page
```
┌─────────────────────────────────────┐
│ Step 4 of 4                         │
│                                     │
│ Processing Complete                 │
│                                     │
│ [Green] ✓ Success                   │
│                                     │
│ [Gray] Summary (4 metrics)          │
│                                     │
│ Download Output Files               │
│ [Blue Card]   Excel Output [⬇]     │
│ [Red Card]    PDF Report [⬇]       │
│ [Purple Card] Audit Trail [⬇]      │
│                                     │
│ Audit Trail (8 entries)             │
│ [Scrollable Table]                  │
│ Time | Action | Details | Rows      │
│ ...                                 │
│                                     │
│ ℹ️ No raw data modified             │
│                                     │
│ [Process Another File]              │
└─────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Mock mode not working?
```bash
# Clear and retry
localStorage.clear()
window.location.href = 'http://localhost:3000?mock=true'
```

### Changes not showing?
```bash
# Hard refresh
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)

# Or restart dev server
npm run dev
```

### Port already in use?
```bash
# Kill process on port 3000
npx kill-port 3000

# Or use different port
npm run dev -- -p 3001
```

---

## ✨ Next Steps

After testing in mock mode:

1. ✅ **Satisfied with UI?** Great! Backend team can start on Prompts A-D
2. ✅ **Want to test with real backend?** See `TESTING_GUIDE.md` Option 2
3. ✅ **Ready to deploy?** See `TESTING_GUIDE.md` Option 3

---

## 📝 Quick Commands

```bash
# Start with mock mode
npm run dev
# Then open: http://localhost:3000?mock=true

# Build for production
npm run build

# Test production build locally
npx serve out

# Deploy to Netlify
npx netlify-cli deploy --prod --dir=out
```

---

**Have fun testing! 🎉**

The entire UI is functional in mock mode. You can click through everything, add mappings, view the audit trail, etc. No backend required!


