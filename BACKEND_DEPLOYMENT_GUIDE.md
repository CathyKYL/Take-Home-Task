# Backend Deployment & Environment Variables Guide

## ✅ Backend Setup Verification

### Current Status Check:

#### 1. ✅ CORS Configuration
**Status:** Configured ✓

Your backend has CORS enabled in `app/main.py`:
```python
allow_origins=["*"]  # Allows all origins (including Netlify)
```

This means your Netlify frontend WILL be able to call the backend.

#### 2. ⚠️ Backend Deployment Status
**Action Required:** Check if backend is running

**To verify:**
```bash
# If running locally:
curl http://localhost:8000/health

# If deployed:
curl https://your-backend-url.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "finance-automation-backend",
  "version": "1.0.0"
}
```

#### 3. ⚠️ Backend URL
**Action Required:** Determine your backend URL

**Options:**
- **Local testing:** `http://localhost:8000`
- **Deployed (Railway):** `https://your-app.up.railway.app`
- **Deployed (Render):** `https://your-app.onrender.com`
- **Deployed (Heroku):** `https://your-app.herokuapp.com`

---

## 🔐 Environment Variables Setup

### ⚠️ CRITICAL: Never Commit API Keys to GitHub!

### Backend Environment Variables (Python)

Your backend needs these variables in a `.env` file:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key
```

### Frontend Environment Variables (Next.js)

Your frontend needs this variable (for Netlify):

```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.com
```

---

## 📝 Step-by-Step: Setting Up Environment Variables

### For Backend (Python - DO NOT COMMIT!)

#### Step 1: Create `.env` file locally

**In your project root:**

```bash
# Windows PowerShell
New-Item -Path ".env" -ItemType File

# Then edit the file and add:
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key
```

#### Step 2: Verify `.env` is in `.gitignore`

**Check `.gitignore` contains:**
```
.env
.env*.local
```

✅ This is already configured in your `.gitignore`!

#### Step 3: Get Your Supabase Credentials

1. Go to https://supabase.com
2. Log in to your project
3. Go to Settings → API
4. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** or **service_role** key → `SUPABASE_KEY`

#### Step 4: Test Backend Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start backend
python run.py
```

You should see:
```
✅ Environment variables configured
✅ All dependencies installed
✨ Starting server...
```

Then test: http://localhost:8000/health

---

### For Frontend (Next.js - For Netlify Deployment)

**⚠️ DO NOT create a `.env.local` file for Netlify!**

Instead, set environment variables IN Netlify:

#### Option 1: During Netlify Site Setup

When connecting GitHub repository:
1. Click "Show advanced"
2. Click "New variable"
3. Add:
   - **Key:** `NEXT_PUBLIC_API_BASE_URL`
   - **Value:** Your backend URL (e.g., `http://localhost:8000` or deployed URL)

#### Option 2: After Site is Created

1. Go to Netlify Dashboard
2. Select your site
3. Go to **Site settings** → **Build & deploy** → **Environment**
4. Click **"Edit variables"**
5. Click **"Add a variable"**
6. Add:
   - **Key:** `NEXT_PUBLIC_API_BASE_URL`
   - **Value:** Your backend URL

#### Option 3: Using Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Link to your site
netlify link

# Set environment variable
netlify env:set NEXT_PUBLIC_API_BASE_URL "https://your-backend-url.com"
```

---

## 🚀 Deployment Options for Backend

### Option 1: Railway (Recommended - Easy)

**Steps:**
1. Go to https://railway.app
2. Sign up/login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. It will auto-detect Python
6. Add environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
7. Deploy!
8. Copy your Railway URL (e.g., `https://your-app.up.railway.app`)

**Pros:**
- ✅ Free tier available
- ✅ Auto-deploys on git push
- ✅ Easy environment variable management
- ✅ Built-in HTTPS

### Option 2: Render (Free Tier Available)

**Steps:**
1. Go to https://render.com
2. Sign up/login
3. Click "New" → "Web Service"
4. Connect GitHub repository
5. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
7. Deploy!

**Pros:**
- ✅ Free tier (spins down after inactivity)
- ✅ Auto-deploys on git push
- ✅ Built-in HTTPS

### Option 3: Keep Running Locally

**For Testing Only:**

1. Start backend: `python run.py`
2. Use ngrok to expose it:
   ```bash
   # Install ngrok
   # Then run:
   ngrok http 8000
   ```
3. Use the ngrok URL in Netlify environment variable
4. **⚠️ Note:** ngrok URLs change on restart

---

## 🔒 Security Best Practices

### ❌ DO NOT:
- ❌ Commit `.env` files to GitHub
- ❌ Commit API keys in code
- ❌ Share `.env` files publicly
- ❌ Put secrets in frontend code (only `NEXT_PUBLIC_*` vars are exposed)

### ✅ DO:
- ✅ Use `.env.example` files (with fake values)
- ✅ Add `.env` to `.gitignore`
- ✅ Use environment variables in deployment platforms
- ✅ Use different keys for development and production
- ✅ Rotate keys if they're ever exposed

---

## 📋 Quick Checklist

### Backend Setup:
- [ ] Create `.env` file locally (NOT committed)
- [ ] Add `SUPABASE_URL` to `.env`
- [ ] Add `SUPABASE_KEY` to `.env`
- [ ] Verify `.env` is in `.gitignore`
- [ ] Run `python run.py` to test locally
- [ ] Backend responds at http://localhost:8000/health

### Backend Deployment:
- [ ] Choose deployment platform (Railway/Render/etc.)
- [ ] Deploy backend
- [ ] Add environment variables in platform
- [ ] Verify backend URL is accessible
- [ ] Test: `curl https://your-backend-url.com/health`

### Frontend Deployment:
- [ ] Push frontend branch to GitHub ✓ (Done!)
- [ ] Connect Netlify to GitHub repository
- [ ] Select `frontend` branch
- [ ] Add `NEXT_PUBLIC_API_BASE_URL` in Netlify
- [ ] Deploy!
- [ ] Test upload workflow

---

## 🧪 Testing Backend is Ready

### Run these tests:

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Create run
curl -X POST http://localhost:8000/runs

# 3. Check API docs
# Open in browser: http://localhost:8000/docs
```

All should return successful responses!

---

## ❓ FAQ

### Q: What's the difference between `.env` and `env.example`?

**`.env`** (DO NOT COMMIT):
- Contains REAL API keys
- Added to `.gitignore`
- Used locally and in deployment platforms

**`env.example`** (SAFE TO COMMIT):
- Contains FAKE/placeholder values
- Shows what variables are needed
- Helps other developers set up their own `.env`

### Q: Do I need to create a `.env` file for frontend?

**For local testing:** Yes, create `.env.local`:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

**For Netlify:** NO! Use Netlify's environment variables instead.

### Q: How do I get my Supabase keys?

1. Go to https://supabase.com
2. Select your project
3. Settings → API
4. Copy URL and Key

### Q: What if my backend URL changes?

**Railway/Render:** Your URL won't change unless you delete the project

**ngrok:** URL changes every restart - update Netlify env var each time

**Custom domain:** Set it up once, never changes

---

## 🆘 Troubleshooting

### Issue: "SUPABASE_URL environment variable is required"

**Solution:** Create `.env` file with Supabase credentials

### Issue: Backend won't start - port already in use

**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Issue: Frontend can't reach backend (CORS error)

**Check:**
1. Backend CORS allows your Netlify domain
2. Backend is actually running
3. Backend URL is correct in Netlify

### Issue: "ModuleNotFoundError" when running backend

**Solution:**
```bash
pip install -r requirements.txt
```

---

## ✅ Ready to Deploy?

### Your Current Status:

**Backend:**
- [x] Code is ready
- [x] CORS is configured
- [ ] Environment variables set up (you need to do this)
- [ ] Backend is deployed (or running locally)
- [ ] Backend URL is accessible

**Frontend:**
- [x] Code is ready
- [x] Pushed to GitHub (frontend branch)
- [ ] Netlify connected
- [ ] Environment variable set in Netlify
- [ ] Deployed and tested

**Next Steps:**
1. Set up your `.env` file for backend
2. Test backend locally
3. Deploy backend (Railway/Render)
4. Copy backend URL
5. Add URL to Netlify environment variable
6. Deploy frontend on Netlify
7. Test with real files!

---

**Need help?** Check the error messages and search above for the specific issue!


