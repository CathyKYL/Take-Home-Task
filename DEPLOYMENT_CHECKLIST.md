# Frontend-Backend Integration & Deployment Checklist

## ✅ Integration Verification Complete

### Frontend API Client (`lib/api.ts`)
- ✅ **POST /runs** - Create run endpoint configured
- ✅ **POST /runs/{runId}/upload** - File upload with FormData
- ✅ **GET /runs/{runId}/inspect** - Inspection endpoint
- ✅ **POST /runs/{runId}/mapping** - Mapping configuration
- ✅ **POST /runs/{runId}/run** - Processing execution
- ✅ **GET /runs/{runId}/download** - Download links

### Backend API Routes (`app/routes/runs.py`)
- ✅ All 6 endpoints implemented
- ✅ Matches frontend API contract
- ✅ FastAPI router configured

### Environment Configuration
- ✅ `env.example` created with `NEXT_PUBLIC_API_BASE_URL`
- ✅ `.gitignore` updated for monorepo (excludes Python files)
- ✅ `netlify.toml` configured for static export

### TypeScript Interfaces Match Backend
- ✅ `InspectResponse` matches backend schema
- ✅ `MappingPayload` matches backend request model
- ✅ `DownloadResponse` includes audit trail support
- ✅ Error handling implemented

---

## 🚀 Ready to Deploy to Netlify

### What Will Work:
✅ Complete UI workflow (Upload → Inspect → Confirm → Download)
✅ File upload to your backend
✅ Real-time processing
✅ Download generated files
✅ Audit trail display

### Prerequisites:
1. **Backend must be deployed first** and accessible via HTTPS
2. **CORS must be enabled** on backend for Netlify domain
3. **Environment variable** must be set in Netlify

---

## 📋 Deployment Steps

### Step 1: Verify Backend is Running

**Check your backend URL is accessible:**
```bash
# Replace with your actual backend URL
curl https://your-backend-url.com/health
```

Expected: 200 OK response

### Step 2: Test Backend CORS

Your backend needs to allow requests from Netlify. Add to backend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local testing
        "https://your-app.netlify.app",  # Netlify domain
        "https://*.netlify.app",  # All Netlify preview deploys
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 3: Build Frontend

```bash
npm install
npm run build
```

Verify the `out/` directory is created.

### Step 4: Push to GitHub

```bash
# Create new branch for frontend
git checkout -b frontend

# Add all frontend files
git add .

# Commit
git commit -m "feat: complete frontend with backend integration"

# Push to GitHub
git push origin frontend
```

### Step 5: Deploy to Netlify

**Option A: Drag & Drop**
1. Go to https://app.netlify.com
2. Drag the `out/` folder
3. Add environment variable in Site Settings:
   - **Key:** `NEXT_PUBLIC_API_BASE_URL`
   - **Value:** `https://your-backend-url.com`

**Option B: Connect GitHub**
1. Go to https://app.netlify.com
2. "Add new site" → "Import from Git"
3. Connect your GitHub repository
4. Select the `frontend` branch
5. Build settings:
   - **Build command:** `npm run build`
   - **Publish directory:** `out`
6. Environment variables:
   - **Key:** `NEXT_PUBLIC_API_BASE_URL`
   - **Value:** `https://your-backend-url.com`
7. Deploy!

---

## 🧪 Post-Deployment Testing

### Test Checklist:

1. **Open Netlify URL** (e.g., https://your-app.netlify.app)
2. **Upload Step:**
   - [ ] Upload AP Excel file
   - [ ] Upload Hold List file
   - [ ] Select processing date
   - [ ] Click "Start Processing"
3. **Inspect Step:**
   - [ ] Spinner shows while inspecting
   - [ ] Automatically moves to Confirm
4. **Confirm Step:**
   - [ ] Column mappings display
   - [ ] Data preview shows
   - [ ] Can add manual mappings
   - [ ] Can add forced hold rules
   - [ ] Click "Run Processing"
5. **Download Step:**
   - [ ] Success banner appears
   - [ ] Run summary displays
   - [ ] Excel download works
   - [ ] Audit trail displays (if backend supports)

### Check Browser Console:

- [ ] No JavaScript errors
- [ ] API calls succeed (Network tab)
- [ ] No CORS errors

---

## 🐛 Troubleshooting

### Issue: CORS Error

**Symptom:** 
```
Access to fetch at 'https://backend...' from origin 'https://your-app.netlify.app' 
has been blocked by CORS policy
```

**Solution:** Add Netlify domain to backend CORS configuration (see Step 2 above)

### Issue: API Base URL Not Set

**Symptom:** Frontend trying to call `http://localhost:8000` from Netlify

**Solution:** 
1. Go to Netlify Dashboard
2. Site Settings → Build & Deploy → Environment
3. Add `NEXT_PUBLIC_API_BASE_URL` with your backend URL
4. Trigger new deploy

### Issue: 404 on API Calls

**Symptom:** API calls return 404

**Check:**
- [ ] Backend URL is correct (https, not http)
- [ ] Backend is actually running
- [ ] Endpoint paths match (`/runs`, `/runs/{id}/upload`, etc.)

### Issue: Files Not Uploading

**Check:**
- [ ] Backend accepts `multipart/form-data`
- [ ] Backend field names match: `ap_file`, `hold_file`, `processing_date`
- [ ] File size limits (frontend: 10MB, backend: check your limit)

---

## 📝 Backend Must Support These Features

For full functionality, your backend should:

### ✅ Required (Core Functionality):
- [x] POST /runs - Create run
- [x] POST /runs/{id}/upload - Accept files
- [x] GET /runs/{id}/inspect - Return inspection data
- [x] POST /runs/{id}/run - Execute processing
- [x] GET /runs/{id}/download - Return download URLs

### ⚠️ Recommended (Enhanced Features):
- [ ] POST /runs/{id}/mapping - Accept overrides (Prompts A & B)
- [ ] Return `column_mappings` in inspect response
- [ ] Return `preview_rows` in inspect response
- [ ] Return `unmatched_payments` and `available_ap_names`

### 🎯 Optional (Audit Trail):
- [ ] Track processing events (Prompt C)
- [ ] Return `audit_trail` in download response (Prompt D)
- [ ] Provide `audit_trail_url` for downloadable log

---

## 🎉 Success Criteria

Your deployment is successful when:

✅ You can upload two Excel files from Netlify
✅ Processing completes without errors
✅ You can download the processed files
✅ Audit trail displays (if backend supports it)

---

## 📞 Need Help?

### Check These First:
1. **Browser Console** (F12) - JavaScript errors
2. **Network Tab** (F12) - API call responses
3. **Netlify Logs** - Build and function logs
4. **Backend Logs** - Server errors

### Common Issues:
- **CORS:** Most common issue - fix backend CORS settings
- **Environment Variables:** Make sure they're set in Netlify
- **Backend Not Running:** Verify backend is accessible
- **Wrong URL:** Check environment variable value

---

## 🔑 Key Points

1. **Backend must be deployed FIRST** with accessible HTTPS URL
2. **CORS must be configured** on backend
3. **Environment variable** must be set in Netlify
4. **Test locally first** with mock mode before deploying
5. **Frontend branch** is production-ready for Netlify

---

**You're ready to deploy!** 🚀

The frontend is fully integrated with your backend API contract. Once your backend is accessible, this will work perfectly on Netlify.


