# Milo Deployment Guide

This guide will help you deploy Milo to production so you can create a Clerk production instance.

## 🚀 Quick Deployment Options

### Option 1: Vercel + Railway (Recommended)

#### Frontend (Vercel)
1. **Push to GitHub** (if not already done)
2. **Go to [vercel.com](https://vercel.com)**
3. **Import your repository**
4. **Configure build settings:**
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Root Directory: `milo-frontend`
5. **Add environment variables:**
   - `VITE_CLERK_PUBLISHABLE_KEY` (your test key for now)
   - `VITE_MILO_API_URL` (will be your Railway URL)
6. **Deploy!**

#### Backend (Railway)
1. **Go to [railway.app](https://railway.app)**
2. **Connect GitHub account**
3. **Create new project from GitHub**
4. **Select your repository**
5. **Add environment variables:**
   - `OPENAI_API_KEY` (your OpenAI key)
   - `FRONTEND_URL` (your Vercel URL)
6. **Deploy!**

### Option 2: Netlify + Render

#### Frontend (Netlify)
1. **Go to [netlify.com](https://netlify.com)**
2. **Import from Git**
3. **Configure build settings:**
   - Build command: `cd milo-frontend && npm run build`
   - Publish directory: `milo-frontend/dist`
4. **Add environment variables**
5. **Deploy!**

#### Backend (Render)
1. **Go to [render.com](https://render.com)**
2. **Create new Web Service**
3. **Connect GitHub repository**
4. **Configure:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. **Add environment variables**
6. **Deploy!**

## 🔧 Environment Variables

### Frontend (.env.production)
```env
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
VITE_MILO_API_URL=https://your-backend-url.com
```

### Backend
```env
OPENAI_API_KEY=your_openai_key
FRONTEND_URL=https://your-frontend-url.com
```

## 📋 Deployment Checklist

### Before Deployment:
- [ ] Code pushed to GitHub
- [ ] Environment variables ready
- [ ] Database file (yale.db) included
- [ ] All dependencies in requirements.txt

### After Frontend Deployment:
- [ ] Frontend URL working
- [ ] Environment variables set
- [ ] Build successful

### After Backend Deployment:
- [ ] Backend URL working
- [ ] API endpoints responding
- [ ] CORS configured correctly
- [ ] OpenAI API key working

### After Both Deployed:
- [ ] Frontend can communicate with backend
- [ ] Authentication flow working
- [ ] Ready for Clerk production setup

## 🎯 Next Steps After Deployment

1. **Get your production URLs:**
   - Frontend: `https://your-app.vercel.app`
   - Backend: `https://your-app.railway.app`

2. **Create Clerk Production Instance:**
   - Go to Clerk dashboard
   - Create production instance
   - Add your frontend domain
   - Get production keys

3. **Update Environment Variables:**
   - Update frontend with production Clerk key
   - Redeploy frontend

4. **Test Everything:**
   - Sign up flow
   - Onboarding process
   - Resume upload
   - Main application

## 🆘 Troubleshooting

### Common Issues:

1. **CORS Errors:**
   - Make sure `FRONTEND_URL` is set in backend
   - Check that frontend URL is in allowed origins

2. **Build Failures:**
   - Check Node.js version compatibility
   - Verify all dependencies are in package.json

3. **API Not Responding:**
   - Check environment variables
   - Verify OpenAI API key is valid
   - Check Railway/Render logs

4. **Authentication Issues:**
   - Verify Clerk keys are correct
   - Check domain configuration in Clerk

## 📞 Support

If you encounter issues:
1. Check the deployment platform logs
2. Verify environment variables
3. Test locally first
4. Check this guide for common solutions
