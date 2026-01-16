# Quick Troubleshooting Guide

## Current Issues

### 1. CORS Error
**Status:** Fix pushed to GitHub, waiting for Render deployment

**What's happening:**
- Backend CORS configuration updated to allow Vercel domain
- Render auto-deploys from GitHub but takes 2-3 minutes
- Until deployment completes, old code (without CORS fix) is still running

**Check deployment status:**
https://dashboard.render.com/web/srv-d5lb6femcj7s73b8fvq0/deploys

### 2. 502 Bad Gateway
**Possible causes:**
1. Render is currently deploying (service temporarily down)
2. Backend crashed during startup
3. Free tier cold start timeout

**How to verify:**
1. Go to Render dashboard
2. Check "Logs" tab for errors
3. Look for deployment status

### 3. Clinical Concepts Missing
**Root cause:** Backend request failing, so app uses mock data which doesn't include clinical_concepts

**Will be fixed when:** Backend CORS is deployed and responding

## Next Steps

**Option A: Wait for Render** (Recommended)
1. Wait 3-5 minutes for Render to finish deploying
2. Visit https://neurovoice-parkinsons-app-1.onrender.com/api/health
3. If you see JSON response, backend is up
4. Try recording again on Vercel site

**Option B: Check Render Manually**
1. Go to https://dashboard.render.com
2. Click on "neurovoice-parkinsons-app-1"
3. Look at "Logs" tab for errors
4. Check if deployment status shows "Live"

**Option C: Force Redeploy**
1. In Render dashboard, click "Manual Deploy" → "Deploy latest commit"
2. Wait for deployment to complete

## How to Tell It's Fixed

✅ Visit: https://neurovoice-parkinsons-app-1.onrender.com/api/health

**Should return:**
```json
{
  "status": "healthy",
  "advanced_models": true,
  "legacy_model": true
}
```

❌ If you get 502 or CORS error, backend isn't ready yet.
