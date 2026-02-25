# Vercel Deployment Guide - Phase 3 Hackathon Todo App

## ✅ Quick Deploy (Recommended)

### Step 1: Connect to Vercel
1. Visit [vercel.com](https://vercel.com)
2. Sign in with your GitHub account
3. Click **"Add New Project"**

### Step 2: Import Repository
- Select **"Import Git Repository"**
- Find and select: `BinteZain/-Hackathon_2_Phase_3-`
- Click **"Import"**

### Step 3: Configure Project
Use these exact settings:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Next.js |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `.next` |
| **Install Command** | `npm install` |

### Step 4: Add Environment Variables
Click **"Environment Variables"** and add:

```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.herokuapp.com/api/v1
NEXT_PUBLIC_BETTER_AUTH_SECRET=eLlMDErNeheyQrPK7EbORWfOKjnB6HoT
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-openai-domain-key
```

> **Note:** Replace `your-backend-url` with your actual backend deployment URL (Railway, Render, or Heroku)

### Step 5: Deploy
- Click **"Deploy"**
- Wait for build to complete (~2-3 minutes)
- Click **"Visit Site"** when ready

## 🎯 Access Your App

After deployment:
- **Homepage:** `https://your-app.vercel.app` (auto-redirects to `/tasks`)
- **Tasks:** `https://your-app.vercel.app/tasks`
- **Login:** `https://your-app.vercel.app/login`
- **Chat:** `https://your-app.vercel.app/chat`

## 🔧 Backend Deployment (Required for Full Functionality)

The frontend needs a backend API. Deploy the backend separately:

### Option 1: Railway (Recommended)
1. Visit [railway.app](https://railway.app)
2. Create new project → "Deploy from GitHub repo"
3. Select: `muhammadafnandood/-Hackathon-2-Phases-3-`
4. Set root directory: `backend`
5. Add environment variables:
   ```
   DATABASE_URL=sqlite:///./todo.db
   BETTER_AUTH_SECRET=eLlMDErNeheyQrPK7EbORWfOKjnB6HoT
   OPENAI_API_KEY=your-openai-key
   ```
6. Deploy
7. Copy the public URL and update `NEXT_PUBLIC_API_URL` in Vercel

### Option 2: Render
1. Visit [render.com](https://render.com)
2. New Web Service → Connect repository
3. Root directory: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### Option 3: Heroku
```bash
cd backend
heroku create your-backend-name
heroku config:set DATABASE_URL=sqlite:///./todo.db
heroku config:set BETTER_AUTH_SECRET=eLlMDErNeheyQrPK7EbORWfOKjnB6HoT
git push heroku master
```

## 🔄 Update Deployment

To update your Vercel deployment after making changes:

```bash
cd E:\All Phases\Phase_3\hackathon-todo
git add .
git commit -m "Your changes"
git push origin master
```

Vercel will automatically redeploy!

## 🐛 Troubleshooting

### Build Fails
- Check that `frontend/package.json` exists
- Ensure `frontend/` directory is set as root in Vercel
- Review build logs in Vercel dashboard

### API Errors
- Verify backend is deployed and running
- Check `NEXT_PUBLIC_API_URL` is correct
- Ensure CORS is enabled in backend

### Authentication Issues
- Verify `NEXT_PUBLIC_BETTER_AUTH_SECRET` is set
- Check backend auth endpoints are working

## 📱 Test Users

Use these credentials to test:
- **Email:** admin@example.com | **Password:** admin123
- **Email:** user1@example.com | **Password:** user123
- **Email:** user2@example.com | **Password:** user123

## 🎉 Success!

Your Phase 3 Hackathon Todo App is now live on Vercel!

---

**Need Help?** Check Vercel's documentation: https://vercel.com/docs
