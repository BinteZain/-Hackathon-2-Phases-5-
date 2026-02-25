# Backend Deployment Guide

## ✅ Frontend Deployed Successfully!

**Frontend URL:** https://frontend-in8o2lkvu-muhammad-afnan-doods-projects.vercel.app

The frontend is now live on Vercel, but it needs a backend to function properly.

---

## 🚀 Deploy Backend to Railway (Recommended - 5 minutes)

### Step 1: Go to Railway
Visit: https://railway.app

### Step 2: Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select: `BinteZain/-Hackathon_2_Phase_3-`

### Step 3: Configure Backend Service
1. Click on the `backend` service
2. Go to **"Settings"** tab
3. Set **Root Directory**: `backend`

### Step 4: Add Environment Variables
Click **"Variables"** tab and add:

```
DATABASE_URL=postgresql://neondb_owner:npg_YmT5PD3xAaJb@ep-weathered-butterfly-a76s9j-pooler.ap-southeast-2.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=eLlMDErNeheyQrPK7EbORWfOKjnB6HoT
PYTHON_VERSION=3.11
```

### Step 5: Deploy
Railway will automatically deploy. Wait for it to finish (~2-3 minutes).

### Step 6: Get Public URL
1. Click **"Settings"**
2. Scroll to **"Domains"**
3. Click **"Generate Domain"**
4. Copy the URL (e.g., `https://backend-production-xxxx.up.railway.app`)

---

## 🔄 Update Frontend Environment Variables

### Step 1: Go to Vercel Dashboard
Visit: https://vercel.com/muhammad-afnan-doods-projects/frontend

### Step 2: Add Environment Variables
1. Click **"Settings"** → **"Environment Variables"**
2. Add new variable:
   - **Key:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://backend-production-xxxx.up.railway.app/api/v1` (your Railway URL + /api/v1)
   - **Environment:** Production ✅
3. Click **"Save"**

### Step 3: Redeploy Frontend
1. Go to **"Deployments"**
2. Click **"Redeploy"** on the latest deployment
3. Wait for it to complete

---

## 🎯 Test Your App

After backend is deployed and frontend is updated:

1. Visit: https://frontend-in8o2lkvu-muhammad-afnan-doods-projects.vercel.app
2. You should be redirected to `/tasks`
3. Login with:
   - **Email:** admin@example.com
   - **Password:** admin123

---

## 📊 Current Status

| Component | Status | URL |
|-----------|--------|-----|
| **Frontend** | ✅ Deployed | https://frontend-in8o2lkvu-muhammad-afnan-doods-projects.vercel.app |
| **Backend** | ⏳ Pending | Deploy to Railway |

---

## 🆘 Need Help?

If you encounter issues:
1. Check Railway logs for backend errors
2. Verify environment variables are set correctly
3. Ensure CORS is configured in backend (should allow all origins for testing)
