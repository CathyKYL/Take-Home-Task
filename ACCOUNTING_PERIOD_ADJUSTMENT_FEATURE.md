# Accounting Period Adjustment Feature

**Date:** 2026-01-29  
**Status:** ✅ Complete & Ready for Deployment

---

## 📋 **Overview:**

The **Accounting Period Adjustment** feature allows users to conditionally modify dates based on a cutoff date. This is essential for accounting period cutoffs where old transactions need to be moved into the current period while preserving recent transactions.

### **Key Difference from Previous Implementation:**
- **Old Feature:** "Date Stamping" - blanket replacement of ALL dates
- **New Feature:** "Accounting Period Adjustment" - conditional replacement of ONLY dates before cutoff

---

## 🎯 **Use Case Example:**

**Scenario:** It's September 1, 2026, and you're closing the August accounting period.

**Problem:** AP data contains transactions from July, August, and September. You need to move all pre-September transactions into the September period.

**Solution:**
1. Set **Cutoff Date**: September 1, 2026
2. Set **New Date**: September 1, 2026
3. Select tabs and columns to check
4. Run processing

**Result:**
- ✅ Transactions dated **July 15** → Changed to **September 1**
- ✅ Transactions dated **August 28** → Changed to **September 1**
- ✅ Transactions dated **September 5** → **Kept as September 5** (unchanged)

---

## 🔧 **How It Works:**

### **Conditional Logic:**

```python
IF (date in column) < cutoff_date:
    change_to(new_date)
ELSE:
    keep_original_date()
```

### **Example with Dates:**

| Original Date | Cutoff Date | New Date | Result |
|---------------|-------------|----------|--------|
| 2026-07-15 | 2026-09-01 | 2026-09-01 | **2026-09-01** (changed) |
| 2026-08-28 | 2026-09-01 | 2026-09-01 | **2026-09-01** (changed) |
| 2026-09-01 | 2026-09-01 | 2026-09-01 | **2026-09-01** (unchanged, equal to cutoff) |
| 2026-09-05 | 2026-09-01 | 2026-09-01 | **2026-09-05** (unchanged, after cutoff) |
| 2026-10-12 | 2026-09-01 | 2026-09-01 | **2026-10-12** (unchanged, after cutoff) |

---

## 🎨 **User Interface:**

### **Location:** Step 3 (Confirm & Continue)

### **UI Components:**

```
┌─────────────────────────────────────────────────────┐
│ Accounting Period Adjustment            [Toggle]    │
│ Conditionally update dates before a cutoff          │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Cutoff Date (dates before this will be modified)    │
│ [2026-09-01] ← Calendar picker                      │
│                                                      │
│ New Date (what to change old dates to)              │
│ [2026-09-01] ← Calendar picker                      │
│                                                      │
│ Apply to Output Tabs:                               │
│ ☑ Ready for Payment                                 │
│ ☑ Payment On Hold                                   │
│                                                      │
│ Date Columns to Check:                              │
│ ☑ Created Date                                      │
│ ☑ Last Modified Date                                │
│                                                      │
│ ┌───────────────────────────────────────────────┐   │
│ │ Summary: Will change dates before 2026-09-01  │   │
│ │ to 2026-09-01 in Created Date and Last        │   │
│ │ Modified Date for Ready for Payment and       │   │
│ │ Payment On Hold. Dates on or after 2026-09-01 │   │
│ │ will remain unchanged.                         │   │
│ └───────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### **Default Values:**
- **Toggle:** OFF
- **Cutoff Date:** Today's date
- **New Date:** Today's date
- **Tabs:** None selected
- **Columns:** None selected

---

## 🏗️ **Technical Implementation:**

### **1. Backend Model (`app/models/api_models.py`)**

```python
class AccountingPeriodAdjustment(BaseModel):
    enabled: bool = False
    cutoff_date: Optional[str] = None  # YYYY-MM-DD
    new_date: Optional[str] = None  # YYYY-MM-DD
    apply_to_tabs: List[str] = []  # ['ready_to_pay', 'payment_on_hold']
    columns_to_check: List[str] = []  # ['created_date', 'modified_date']
```

### **2. Backend Processing (`app/processing/process.py`)**

**Key Logic:**

```python
# Convert column to datetime
df[column] = pd.to_datetime(df[column], errors='coerce')

# Create mask for dates BEFORE cutoff
mask = df[column].notna() & (df[column].dt.date < cutoff_date)

# Apply new date ONLY to rows matching mask
df.loc[mask, column] = pd.Timestamp(new_date)
```

**Features:**
- ✅ Independent processing for each tab
- ✅ Independent processing for each column
- ✅ Handles NaT/None values gracefully
- ✅ Tracks changed vs preserved counts
- ✅ Detailed audit trail

### **3. Frontend (`components/ConfirmStep.tsx`)**

**State Variables:**
```typescript
const [adjustmentEnabled, setAdjustmentEnabled] = useState(false)
const [cutoffDate, setCutoffDate] = useState<string>(today)
const [newDate, setNewDate] = useState<string>(today)
const [applyToTabs, setApplyToTabs] = useState<string[]>([])
const [columnsToCheck, setColumnsToCheck] = useState<string[]>([])
```

**Submission:**
```typescript
const adjustmentConfig = adjustmentEnabled ? {
  enabled: true,
  cutoff_date: cutoffDate,
  new_date: newDate,
  apply_to_tabs: applyToTabs,
  columns_to_check: columnsToCheck
} : { enabled: false, ... }

await saveMapping(runId, {
  mapping: { account_name: detectedAccountColumn },
  manual_hold_mappings: manualHoldMappings,
  accounting_period_adjustment: adjustmentConfig
})
```

### **4. API Types (`lib/api.ts`)**

```typescript
export interface AccountingPeriodAdjustment {
  enabled: boolean
  cutoff_date: string | null
  new_date: string | null
  apply_to_tabs: string[]
  columns_to_check: string[]
}
```

### **5. Database Storage**

**Column:** `date_stamping_config_json` (reused from previous feature)

**Content:**
```json
{
  "enabled": true,
  "cutoff_date": "2026-09-01",
  "new_date": "2026-09-01",
  "apply_to_tabs": ["ready_to_pay", "payment_on_hold"],
  "columns_to_check": ["created_date", "modified_date"]
}
```

---

## 📊 **Audit Trail:**

### **When Applied:**

```json
{
  "action": "Accounting Period Adjustment",
  "action_type": "accounting_period_adjustment",
  "details": "Adjusted dates before 2026-09-01 to 2026-09-01 in Ready_To_Pay, Payment_On_Hold (Created Date, Last Modified Date). Changed: 856, Preserved: 250",
  "rows_affected": 856
}
```

**Key Metrics:**
- **Changed:** Number of date values modified (< cutoff)
- **Preserved:** Number of date values kept unchanged (>= cutoff)

### **When Disabled:**

```json
{
  "action": "Accounting Period Adjustment Skipped",
  "action_type": "accounting_adjustment_skip",
  "details": "User chose not to apply accounting period adjustment",
  "rows_affected": 0
}
```

---

## 🎯 **Use Cases:**

### **Use Case 1: Standard Period Close**
**Scenario:** Close August period on Sept 1

**Settings:**
- Cutoff: Sept 1, 2026
- New Date: Sept 1, 2026
- Tabs: Both
- Columns: Both

**Result:** All August and earlier transactions moved to Sept 1

---

### **Use Case 2: Backdating for Corrections**
**Scenario:** Need to backdate transactions to July 31 for corrections

**Settings:**
- Cutoff: Aug 1, 2026
- New Date: July 31, 2026
- Tabs: Ready for Payment only
- Columns: Last Modified Date only

**Result:** Only Ready for Payment transactions dated before Aug 1 get Modified Date changed to July 31

---

### **Use Case 3: No Adjustment Needed**
**Scenario:** Current period data, no adjustment needed

**Settings:**
- Toggle: OFF

**Result:** All original dates preserved

---

## ✅ **Validation:**

### **Frontend:**
- ✅ Both dates default to today
- ✅ No enforcement of cutoff < new date (user choice)
- ✅ Summary preview shows exact behavior

### **Backend:**
- ✅ Date parsing with fallback to upload_date
- ✅ Handles invalid dates gracefully
- ✅ Handles NaT/None values (skip comparison)
- ✅ Independent column processing

---

## 🔒 **Data Integrity:**

### **Guarantees:**
1. ✅ **Raw tab never modified** - always original data
2. ✅ **Only specified columns modified** - others untouched
3. ✅ **Only specified tabs modified** - others untouched
4. ✅ **Only dates < cutoff modified** - others preserved
5. ✅ **Reconciliation still passes** - row counts match

### **No Side Effects:**
- ❌ No rounding, truncation, or formatting changes
- ❌ No modification of non-date columns
- ❌ No modification of Raw tab
- ❌ No modification of dates >= cutoff

---

## 🚀 **Deployment:**

### **Backend:**
1. ✅ Code changes ready
2. ⏳ Push to GitHub
3. ⏳ Auto-deploy on Render

### **Frontend:**
1. ✅ Code changes ready
2. ⏳ Push to GitHub
3. ⏳ Auto-deploy on Netlify

### **Database:**
- ✅ No new migration needed (reusing existing column)

---

## 🧪 **Testing Scenarios:**

### **Test 1: Basic Functionality**
1. Upload AP data with mixed dates (past, present, future)
2. Toggle ON
3. Set cutoff to today
4. Set new date to today
5. Select all tabs and columns
6. Process and download
7. **Verify:** Past dates changed, today/future dates unchanged

### **Test 2: Selective Application**
1. Toggle ON
2. Select only Ready for Payment tab
3. Select only Created Date column
4. **Verify:** Only Ready tab's Created Date column modified

### **Test 3: Disabled (Default)**
1. Leave toggle OFF
2. Process and download
3. **Verify:** All original dates preserved

### **Test 4: Audit Trail**
1. Enable adjustment
2. Process files
3. Download and check audit trail
4. **Verify:** Shows "Changed: X, Preserved: Y"

---

## 📝 **Files Changed:**

### **Backend:**
```
app/models/api_models.py       # New AccountingPeriodAdjustment model
app/processing/process.py      # Conditional date modification logic
app/routes/runs.py             # Extract and pass adjustment config
```

### **Frontend:**
```
components/ConfirmStep.tsx     # New UI with 2 date pickers, updated logic
lib/api.ts                     # New API types
```

---

## 📚 **User Documentation:**

### **Quick Guide:**

**What is it?**  
Accounting Period Adjustment lets you update old dates to a new date while keeping recent dates unchanged.

**When to use it?**  
- Closing accounting periods
- Moving old transactions into current period
- Backdating for corrections

**How to use it:**
1. Toggle ON the "Accounting Period Adjustment"
2. Set **Cutoff Date** - dates before this will change
3. Set **New Date** - what to change old dates to
4. Select which tabs to apply to
5. Select which date columns to check
6. Review the summary
7. Run processing

**Example:**  
If cutoff is Sept 1 and new date is Sept 1:
- July dates → Changed to Sept 1 ✓
- August dates → Changed to Sept 1 ✓
- Sept 1+ dates → Unchanged ✓

---

**Accounting Period Adjustment Feature - Complete!** 🎉

Users now have precise, conditional control over date modifications for accounting period management.

