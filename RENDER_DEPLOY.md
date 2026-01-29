# Render Deployment Guide

This guide explains how to deploy the Finance Automation fullstack application (Next.js frontend + FastAPI backend) as a single Docker web service on Render.

## Architecture

- **Frontend**: Next.js static export served by Nginx
- **Backend**: FastAPI on uvicorn (port 8000, internal only)
- **Reverse Proxy**: Nginx routes `/api/*` to FastAPI, `/` to frontend
- **Single Container**: Both services run in one Docker container on Render

## Prerequisites

1. **GitHub Repository**: Your code must be pushed to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Supabase Project**: You need:
   - Supabase Project URL
   - Supabase Service Role Key (keep this secret!)

## Step 1: Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository:
   - Authorize Render to access your GitHub account
   - Select your repository (e.g., `CathyKYL/Take-Home-Task`)
4. Configure the service:
   - **Name**: `finance-automation` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main` or `frontend` (whichever has your code)
   - **Root Directory**: Leave empty (Dockerfile is at repo root)
   - **Environment**: **Docker**
   - **Instance Type**: Start with **Free** (for testing) or **Starter** ($7/mo for production)

## Step 2: Configure Environment Variables

In the Render dashboard, add these environment variables under **"Environment"**:

### Required Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `SUPABASE_URL` | `https://your-project-id.supabase.co` | Get from Supabase Project Settings → API |
| `SUPABASE_KEY` | `eyJhbGc...` (long key) | Get from Supabase Project Settings → API → service_role secret key |

### Optional Variables

| Variable | Default | Notes |
|----------|---------|-------|
| `PORT` | `10000` | Render automatically sets this - don't override |

⚠️ **IMPORTANT**: 
- Use **service_role** key (not anon key) for backend operations
- Never commit secrets to Git - set them only in Render dashboard
- The `SUPABASE_KEY` is **never exposed** to the browser (server-side only)

## Step 3: Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Build the Docker image (takes 5-10 minutes first time)
   - Start the container
   - Assign a public URL (e.g., `https://finance-automation.onrender.com`)

3. Monitor build logs in the Render dashboard
   - Look for: `=== Service Ready ===`
   - Check for any errors in red

## Step 4: Verify Deployment

Once deployed, test these URLs (replace with your Render URL):

### Health Check
```bash
curl https://your-app.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "finance-automation-backend",
  "version": "1.0.0"
}
```

### Frontend
Visit `https://your-app.onrender.com` in your browser
- Should load the Next.js UI
- Check browser console for errors

### API Endpoints
Test the full workflow:

1. **Create Run**:
   ```bash
   curl -X POST https://your-app.onrender.com/api/runs \
     -H "Content-Type: application/json"
   ```

2. **Get Run Status**:
   ```bash
   curl https://your-app.onrender.com/api/runs/{run_id}
   ```

## Troubleshooting

### Build Fails

**Check Dockerfile syntax**:
```bash
# Test locally first
docker build -t finance-automation .
docker run -e SUPABASE_URL=test -e SUPABASE_KEY=test -p 10000:10000 finance-automation
```

**Common issues**:
- Missing files in Dockerfile COPY commands
- Node or Python dependency conflicts
- Out of memory (upgrade Render instance)

### Container Starts but Crashes

**Check Render logs** for:
- `ERROR: SUPABASE_URL environment variable is required` → Set env vars in dashboard
- `ERROR: SUPABASE_KEY environment variable is required` → Set env vars in dashboard
- `nginx: [emerg]` → Nginx config error
- `ModuleNotFoundError` → Missing Python dependency in requirements.txt

### API Returns 502/504

- **502 Bad Gateway**: FastAPI backend not running or crashed
  - Check logs: `FastAPI started (PID: ...)`
  - Verify uvicorn is listening on `127.0.0.1:8000`

- **504 Gateway Timeout**: Request taking too long
  - Check nginx `proxy_read_timeout` in `deploy/nginx.conf`
  - Check backend processing logic

### Frontend Loads but API Fails

**CORS Error in Browser**:
- Should NOT happen (same-origin requests via `/api/*`)
- If it does, check that `lib/api.ts` uses relative paths

**404 on API Calls**:
- Verify backend routes start with `/api` prefix
- Check nginx config proxies `/api/` correctly

## Environment-Specific Configuration

### Development
For local development, run frontend and backend separately:

```bash
# Terminal 1: Backend
python run.py

# Terminal 2: Frontend (with proxy)
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` in `.env.local` for development.

### Production (Render)
- Frontend and backend served from same domain
- No CORS issues
- API calls use relative paths (`/api/*`)
- Environment variables set in Render dashboard

## Maintenance

### Updating the App

1. Push changes to GitHub (main or frontend branch)
2. Render automatically rebuilds and deploys
3. Monitor build logs for errors

### Scaling

- **Free Tier**: Spins down after 15 min inactivity (slow cold starts)
- **Starter ($7/mo)**: Always on, better performance
- **Standard+**: More CPU/RAM for heavy processing

### Database Backups

Your data is in Supabase (separate service):
- Configure automatic backups in Supabase dashboard
- Run migrations in `migrations/` folder if schema changes

## Security Checklist

- ✅ `SUPABASE_KEY` never in Git history
- ✅ Environment variables set only in Render dashboard
- ✅ HTTPS enforced (Render provides SSL automatically)
- ✅ Backend secrets never exposed to frontend
- ✅ Nginx security headers configured (X-Frame-Options, etc.)

## Support

- **Render Docs**: https://render.com/docs
- **Render Status**: https://status.render.com
- **Supabase Docs**: https://supabase.com/docs

---

## Quick Reference

| Resource | URL |
|----------|-----|
| Render Dashboard | https://dashboard.render.com |
| Build Logs | Render Dashboard → Your Service → Logs |
| Environment Variables | Render Dashboard → Your Service → Environment |
| Supabase Dashboard | https://app.supabase.com |
| Health Check | `https://your-app.onrender.com/api/health` |
| Frontend | `https://your-app.onrender.com` |
| API Base | `https://your-app.onrender.com/api` |

