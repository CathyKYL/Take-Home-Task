# Testing Guide

## Quick Answer

**✅ Test Locally First** - Faster, easier debugging, no cost

**🚀 Deploy to Netlify After** - Once backend is ready and local testing is complete

---

## Option 1: Local Testing WITH Mock Mode (No Backend Needed)

### Step 1: Start Development Server

```bash
npm install  # If you haven't already
npm run dev
```

### Step 2: Open Browser

Navigate to: **http://localhost:3000**

### Step 3: Enable Mock Mode

You'll see a small "Enable Mock Mode" link in the top right.

**Or** add `?mock=true` to the URL:
```
http://localhost:3000?mock=true
```

### Step 4: Test UI Features

With mock mode enabled, you get a yellow banner with quick navigation:

```
⚠️ Mock Mode Active - Testing UI Without Backend
[Disable] [Go to Upload] [Jump to Confirm] [Jump to Download]
```

**What You Can Test:**

✅ **Upload Step:**
- File selection (drag & drop)
- File validation (type, size)
- Processing date picker
- Button states

✅ **Confirm Step** (Jump to Confirm):
- View detected column mappings
- Column selection dropdowns
- Data preview table
- Summary counts
- Manual vendor name mapping
  - Add mappings
  - Remove mappings
  - Table display
- Manual hold rules by identifier
  - Add forced hold rules
  - Remove rules
  - Table display
- Process button states
- Warning messages

✅ **Download Step** (Jump to Download):
- Success banner
- Run summary display
- Download buttons (Excel, PDF, Audit Trail)
- Audit trail table
  - Scrolling
  - Color-coded actions
  - Formatted timestamps
  - Row counts
- "Process Another File" button

**What You CANNOT Test:**
❌ Actual file upload to server
❌ Real backend processing
❌ Actual file downloads (buttons open example URLs)
❌ Real API error handling

---

## Option 2: Local Testing WITH Real Backend

### Prerequisites

1. Backend is running locally (e.g., `http://localhost:8000`)
2. Backend has implemented Prompts A, B, C, D

### Step 1: Configure API URL

Create `.env.local` file:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Step 2: Start Both Servers

**Terminal 1 - Backend:**
```bash
cd ../backend  # or your backend directory
# Start your backend server (varies by framework)
python main.py  # or uvicorn, flask, etc.
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

### Step 3: Test Full Workflow

1. Open **http://localhost:3000**
2. **DO NOT** enable mock mode
3. Upload real files:
   - Your AP Excel file
   - Your Hold List Excel file
4. Select processing date
5. Click "Start Processing"
6. Watch inspection phase
7. Review and confirm mappings
8. Add manual overrides if needed
9. Click "Run Processing"
10. View download page with audit trail

### Step 4: Check Backend Logs

Monitor your backend terminal for:
- API calls being received
- Processing events
- Any errors

---

## Option 3: Deploy to Netlify (Production Testing)

### When to Deploy:

✅ After local testing is complete
✅ After backend is deployed to production
✅ To test with real production URLs
✅ To share with team/stakeholders

### Step 1: Build Production Version

```bash
npm run build
```

This creates the `out/` directory with static files.

### Step 2: Test Production Build Locally (Optional)

```bash
# Install a simple HTTP server
npm install -g serve

# Serve the production build
serve out

# Open http://localhost:3000
```

### Step 3: Deploy to Netlify

**Option A: Drag & Drop (Easiest)**

1. Go to https://app.netlify.com
2. Log in
3. Click "Add new site" → "Deploy manually"
4. Drag the `out/` folder into the upload area
5. Wait for deployment
6. Get your site URL (e.g., `https://your-site.netlify.app`)

**Option B: Netlify CLI**

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
netlify deploy --prod --dir=out
```

**Option C: Git Integration (Best for Production)**

1. Push code to GitHub/GitLab/Bitbucket
2. Connect repository to Netlify
3. Configure build settings:
   - Build command: `npm run build`
   - Publish directory: `out`
4. Add environment variable:
   - Key: `NEXT_PUBLIC_API_BASE_URL`
   - Value: Your production backend URL (e.g., `https://api.yourapp.com`)
5. Deploy automatically on push

### Step 4: Test on Netlify

1. Open your Netlify URL
2. Test full workflow with real files
3. Verify:
   - File uploads work
   - Processing completes
   - Downloads work
   - Audit trail displays
   - All URLs are correct

---

## Recommended Testing Flow

### Phase 1: UI Testing (Mock Mode)
```
1. npm run dev
2. Enable mock mode
3. Test all UI interactions
4. Verify visual design
5. Check responsiveness (mobile, tablet, desktop)
```

### Phase 2: Local Integration Testing
```
1. Start backend locally
2. Configure .env.local
3. npm run dev
4. Upload small test files
5. Verify API communication
6. Check error handling
7. Test edge cases
```

### Phase 3: Production Testing
```
1. Deploy backend to production
2. npm run build
3. Deploy to Netlify
4. Test with production URLs
5. Verify CORS settings
6. Test with realistic file sizes
7. Performance testing
```

---

## Common Issues & Solutions

### Issue: "Failed to fetch" errors

**Cause:** Backend not running or wrong URL

**Solution:**
- Check backend is running: `curl http://localhost:8000/health`
- Verify `.env.local` has correct URL
- Check CORS settings in backend

### Issue: Mock mode won't disable

**Solution:**
```javascript
// Open browser console and run:
localStorage.removeItem('mockMode')
window.location.reload()
```

### Issue: Files not uploading

**Possible causes:**
- File size > 10MB
- Wrong file type (not .xlsx, .xls, .xlsm)
- Backend endpoint not accepting multipart/form-data
- CORS issues

**Debug:**
1. Open DevTools → Network tab
2. Try upload
3. Check request/response
4. Look for error messages

### Issue: Netlify build fails

**Common causes:**
- Missing dependencies: Run `npm install` first
- TypeScript errors: Run `npm run build` locally first
- Environment variables: Add them in Netlify dashboard

**Solution:**
```bash
# Test build locally first
npm run build

# If it works locally but fails on Netlify:
# - Check Netlify build logs
# - Verify all dependencies are in package.json
# - Not in devDependencies if needed for build
```

---

## Testing Checklist

### Before Deployment

- [ ] All components render without errors
- [ ] Form validation works
- [ ] File upload UI works
- [ ] Step navigation works
- [ ] Manual mapping UI works
- [ ] Error states display correctly
- [ ] Loading states show properly
- [ ] Mobile responsive
- [ ] No console errors
- [ ] Production build succeeds (`npm run build`)

### After Deployment

- [ ] Site loads on Netlify URL
- [ ] Environment variables set correctly
- [ ] Can upload files
- [ ] Processing completes
- [ ] Downloads work
- [ ] Audit trail displays
- [ ] Error handling works
- [ ] All links/buttons work
- [ ] Performance is acceptable
- [ ] HTTPS works correctly

---

## Performance Tips

### For Local Testing:
- Use small test files (10-50 rows)
- Clear browser cache if seeing old data
- Use DevTools for debugging

### For Production:
- Test with realistic file sizes
- Monitor Netlify bandwidth
- Check load times
- Test on different networks
- Verify mobile performance

---

## Need Help?

### Debugging Mode

Add this to any page to see what's happening:

```typescript
console.log('Current Step:', currentStep)
console.log('Run ID:', runId)
console.log('Inspect Data:', inspectData)
console.log('Error:', error)
```

### Network Debugging

1. Open DevTools (F12)
2. Go to Network tab
3. Filter by "Fetch/XHR"
4. Watch API calls in real-time
5. Click any request to see details

### Mock Data Inspection

In browser console:
```javascript
import { MOCK_INSPECT_DATA } from './components/MockDataProvider'
console.log(MOCK_INSPECT_DATA)
```

---

## Summary

**🏠 Local Testing (Recommended First)**
- ✅ Fast iteration
- ✅ Easy debugging
- ✅ Mock mode for UI testing
- ✅ Real backend testing if available

**🚀 Netlify Deployment (Do Later)**
- ✅ Production testing
- ✅ Stakeholder sharing
- ✅ Real-world performance
- ✅ CI/CD integration

**Start locally, deploy when ready!**


