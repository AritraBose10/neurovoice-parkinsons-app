# Deployment Guide for Render.com

## Prerequisites
- GitHub account
- Render.com account (free tier available)

## Step 1: Push Code to GitHub

1. Initialize git repository:
```bash
cd C:\Users\LENOVO\Desktop\voice
git init
git add .
git commit -m "Initial commit - Parkinson's voice analysis app"
```

2. Create a new repository on GitHub:
   - Go to https://github.com/new
   - Name: `neurovoice-parkinsons-detection`
   - Make it public or private
   - Don't initialize with README

3. Push to GitHub:
```bash
git remote add origin https://github.com/YOUR_USERNAME/neurovoice-parkinsons-detection.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy Backend to Render

1. Go to https://render.com and sign in
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `neurovoice-backend`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Instance Type**: `Free`

5. Add Environment Variables:
   - `PYTHON_VERSION`: `3.14.0`

6. Click "Create Web Service"
7. Wait for deployment (5-10 minutes)
8. Copy the backend URL (e.g., `https://neurovoice-backend.onrender.com`)

## Step 3: Update Frontend for Production

1. Update `app.js` - change API_URL:
```javascript
const API_URL = 'https://neurovoice-backend.onrender.com';
```

2. Commit and push changes:
```bash
git add app.js
git commit -m "Update API URL for production"
git push
```

## Step 4: Deploy Frontend to Render

1. In Render dashboard, click "New +" → "Static Site"
2. Connect the same GitHub repository
3. Configure:
   - **Name**: `neurovoice-app`
   - **Branch**: `main`
   - **Root Directory**: `.` (root)
   - **Build Command**: (leave empty)
   - **Publish Directory**: `.` (root)

4. Click "Create Static Site"
5. Wait for deployment (2-3 minutes)
6. Your app will be live at: `https://neurovoice-app.onrender.com`

## Step 5: Test the Deployment

1. Visit your frontend URL
2. Click "Upload Voice Sample"
3. Record 15 seconds
4. Click "View Voice Analytics"
5. Verify the detailed report appears

## Important Notes

⚠️ **Free Tier Limitations:**
- Backend may sleep after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds to wake up
- 750 hours/month free (enough for testing)

⚠️ **Medical Disclaimer:**
- Add prominent disclaimer on homepage
- This is for research/educational purposes only
- NOT for clinical diagnosis

## Alternative: Manual Deployment Steps

If you prefer, I can:
1. Create the GitHub repository for you (need your GitHub token)
2. Deploy directly using Render API
3. Provide you with the public URLs

Let me know if you need help with any step!
