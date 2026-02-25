# Deploy to Vercel - Quick Start

## ✅ All Code Uploaded to GitHub!

Your complete Phase 3 work is now at:
**https://github.com/BinteZain/-Hackathon_2_Phase_3-**

✅ **node_modules excluded** (not uploaded)
✅ **Auto-redirect configured** (homepage → /tasks)

---

## Option 1: Vercel Dashboard (Easiest) ⭐

### Click to Deploy:
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/BinteZain/-Hackathon_2_Phase_3-)

1. Click the button above
2. Import: `BinteZain/-Hackathon_2_Phase_3-`
3. Set Root Directory: `frontend`
4. Add environment variables (see below)
5. Deploy!

### Environment Variables Needed:
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com/api/v1
NEXT_PUBLIC_BETTER_AUTH_SECRET=eLlMDErNeheyQrPK7EbORWfOKjnB6HoT
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-openai-key
```

---

## Option 2: Vercel CLI (Advanced)

### Install Vercel CLI
```bash
npm install -g vercel
```

### Deploy
```bash
cd E:\All Phases\Phase_3\hackathon-todo\frontend
vercel login
vercel --prod
```

### Set Environment Variables
```bash
vercel env add NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_BETTER_AUTH_SECRET production
vercel env add NEXT_PUBLIC_OPENAI_DOMAIN_KEY production
```

Then redeploy:
```bash
vercel --prod
```

---

## 🎯 Your App URLs

After deployment:
- **Main App:** https://your-project.vercel.app/tasks
- **Homepage:** https://your-project.vercel.app (redirects to /tasks)
- **Login:** https://your-project.vercel.app/login
- **Chat:** https://your-project.vercel.app/chat

---

## 📝 Test Credentials

- **Email:** admin@example.com | **Password:** admin123
- **Email:** user1@example.com | **Password:** user123

---

## 🔗 Links

- **GitHub:** https://github.com/muhammadafnandood/-Hackathon-2-Phases-3-
- **Vercel Dashboard:** https://vercel.com/dashboard
- **DEPLOYMENT.md:** See full guide in repository
