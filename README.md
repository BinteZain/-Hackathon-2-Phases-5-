# Hackathon Phase 4 - Full Stack Application

A modern full-stack web application built with **Next.js 16** (Frontend) and **Python/Node.js** (Backend), designed for hackathon Phase 4.

## 🚀 Vercel Deployment (Recommended)

This project is **pre-configured for one-click deployment** to Vercel.

### Option 1: One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/muhammadafnandood/-Hackathon-2-Phases-4-)

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### Option 3: Automatic Deployments from GitHub

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository: `muhammadafnandood/-Hackathon-2-Phases-4-`
4. Configure environment variables (see below)
5. Click "Deploy"

**Vercel will automatically:**
- Detect Next.js framework
- Run `npm run build` in the `frontend` directory
- Deploy your application
- Provide a live URL (e.g., `your-project.vercel.app`)

### Environment Variables for Vercel

Add these in Vercel project settings → Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://your-backend.vercel.app/api` |
| `NEXT_PUBLIC_BETTER_AUTH_SECRET` | Authentication secret | `your-secret-key-min-32-chars` |

### Pre-Deployment Checklist

- ✅ Ensure `node_modules/` is in `.gitignore` (already configured)
- ✅ Ensure `.env` files are NOT committed (already configured)
- ✅ `vercel.json` is properly configured (already done)
- ✅ `frontend/package.json` has all dependencies (verified)
- ✅ Build script works locally: `cd frontend && npm run build`

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+ (for backend)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/muhammadafnandood/-Hackathon-2-Phases-4-.git
cd "4 phir se"
```

2. **Install Frontend Dependencies**
```bash
cd frontend
npm install
```

3. **Setup Environment Variables**
```bash
# Create .env.local in frontend directory
cp .env.example .env.local
```

## 📁 Project Structure

```
.
├── frontend/              # Next.js frontend application
│   ├── app/              # Next.js 13+ app directory
│   ├── components/       # React components
│   ├── public/           # Static assets
│   ├── styles/           # Global styles
│   └── package.json      # Frontend dependencies
├── backend/              # Python/Node.js backend
│   ├── main.py          # Main backend entry point
│   └── requirements.txt # Python dependencies
├── specs/               # Specification documents
├── history/             # Project history and records
├── vercel.json          # Vercel deployment configuration
└── README.md            # This file
```

## 🛠️ Development

### Frontend Development

```bash
cd frontend
npm run dev
```

The app will be available at `http://localhost:3000`

### Backend Development

```bash
# Python backend
python main.py

# Or using run script
python run_backend.py
```

## 🌐 Deployment

### Vercel Deployment (Frontend)

This project is pre-configured for Vercel deployment.

1. **Install Vercel CLI** (optional)
```bash
npm install -g vercel
```

2. **Deploy to Vercel**
```bash
# Using Vercel CLI
vercel

# Or connect your GitHub repository at vercel.com
# Vercel will automatically detect the configuration
```

3. **Environment Variables on Vercel**

Add the following environment variables in your Vercel project settings:

- `NEXT_PUBLIC_API_URL` - Your backend API URL
- `NEXT_PUBLIC_BETTER_AUTH_SECRET` - Authentication secret key

### Backend Deployment

Deploy the backend separately to your preferred platform (Heroku, Railway, Render, etc.)

## 🔧 Configuration

### Vercel Configuration

The `vercel.json` file contains:

- Build commands
- Output directory configuration
- Environment variables
- Rewrite rules for API calls
- Redirects

### Environment Variables

Create a `.env.local` file in the `frontend` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_BETTER_AUTH_SECRET=your-secret-key-here
```

## 📦 Features

- ✅ Modern Next.js 13+ frontend
- ✅ Responsive UI design
- ✅ API integration
- ✅ Authentication support
- ✅ TypeScript support
- ✅ Tailwind CSS styling
- ✅ Ready for Vercel deployment

## 🧪 Testing

```bash
# Frontend tests
cd frontend
npm test

# Linting
npm run lint
```

## 📝 Scripts

### Frontend Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |

## ⚠️ Important Notes

### ❌ NEVER Commit These Files

The following are **already excluded** in `.gitignore` - never commit them:

- **`node_modules/`** - Dependencies (500MB+, will cause deployment errors)
- **`.env*`** - Environment files with secrets
- **`.next/`** - Build artifacts
- **`.vercel/`** - Vercel configuration
- **`__pycache__/`** - Python cache files
- **`*.log`** - Log files
- **`.DS_Store`, `Thumbs.db`** - OS files

### ✅ Always Commit These Files

- **`package.json`** and **`package-lock.json`** - Dependencies
- **`vercel.json`** - Deployment configuration
- **`README.md`** - Documentation
- **Source code** - `.tsx`, `.ts`, `.js`, `.py` files
- **Configuration files** - `.gitignore`, `tsconfig.json`, etc.

### 🔒 Security Best Practices

- Never commit API keys, passwords, or secrets
- Use `.env.local` for local development
- Use Vercel Environment Variables for production
- Rotate secrets if accidentally committed

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

This project is part of Hackathon Phase 4.

## 🔗 Links

- **GitHub Repository**: https://github.com/muhammadafnandood/-Hackathon-2-Phases-4-
- **Vercel Documentation**: https://vercel.com/docs
- **Next.js Documentation**: https://nextjs.org/docs

## 🆘 Troubleshooting

### Build Errors on Vercel

1. Ensure all dependencies are in `package.json`
2. Check that `vercel.json` build commands are correct
3. Verify environment variables are set in Vercel dashboard

### Module Not Found

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### API Connection Issues

- Verify `NEXT_PUBLIC_API_URL` is correctly set
- Check CORS configuration on backend
- Ensure backend is running and accessible

---

**Built with ❤️ for Hackathon Phase 4**
