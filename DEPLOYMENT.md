# Deployment Guide

This guide walks you through deploying the 2GIS Lead Scraper to production using **Vercel** (frontend) and **Railway** (backend).

## Prerequisites

- [Vercel Account](https://vercel.com/signup) (free)
- [Railway Account](https://railway.app/) (Hobby plan: $5/month)
- [GitHub Account](https://github.com/) (for connecting repositories)

---

## Part 1: Deploy Backend to Railway

### 1. Push Code to GitHub

```bash
cd "/Users/echris/Desktop/Yandex Scraper"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/2gis-scraper.git
git push -u origin main
```

### 2. Create Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `2gis-scraper` repository
5. Railway will automatically detect the `Dockerfile` and start building

### 3. Configure Environment Variables

In Railway project settings, add these environment variables:

```
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

*Note: You'll get the Vercel URL after deploying the frontend. Update this variable then.*

### 4. Get Your Railway URL

Once deployed, Railway will provide a URL like:
```
https://your-app.up.railway.app
```

Copy this URL - you'll need it for the frontend configuration.

---

## Part 2: Deploy Frontend to Vercel

### 1. Prepare Frontend for Deployment

Create a `.env.local` file in the `frontend` directory:

```bash
cd frontend
cp .env.example .env.local
```

Edit `.env.local`:
```
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
```

Replace `your-app.up.railway.app` with your actual Railway URL.

### 2. Push Frontend to GitHub

If you want to keep frontend separate (optional):

```bash
cd frontend
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/2gis-scraper-frontend.git
git push -u origin main
```

Or use the same repository (monorepo approach) - Vercel can deploy from subdirectories.

### 3. Deploy to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Configure build settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend` (if using monorepo)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

5. Add environment variable:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-app.up.railway.app` (your Railway URL)

6. Click **"Deploy"**

### 4. Get Your Vercel URL

Vercel will provide a URL like:
```
https://your-app.vercel.app
```

### 5. Update Railway CORS Settings

Go back to Railway and update the `ALLOWED_ORIGINS` environment variable:

```
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

This allows your Vercel frontend to make requests to the Railway backend.

---

## Testing the Deployment

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Try scraping a few businesses
3. Check Railway logs for any errors:
   - Go to Railway dashboard
   - Click on your project
   - View **"Deployments"** → **"Logs"**

---

## Cost Estimate

- **Vercel**: Free (Hobby plan includes unlimited bandwidth)
- **Railway**: $5/month (Hobby plan)
  - Includes 500 hours of usage
  - For 100 businesses/day with enrichment (~10 min/scrape):
    - Daily usage: ~10 minutes
    - Monthly usage: ~5 hours
    - **Well within limits!**

---

## Local Development

To run locally after deployment setup:

### Backend:
```bash
cd "/Users/echris/Desktop/Yandex Scraper"
python3 -m uvicorn api.main:app --reload --port 8000
```

### Frontend:
```bash
cd frontend
npm run dev
```

Make sure your frontend `.env.local` points to `http://localhost:8000` for local development.

---

## Troubleshooting

### CORS Errors
- Make sure `ALLOWED_ORIGINS` in Railway includes your Vercel URL
- Check Railway logs for CORS-related errors

### Playwright Errors
- Railway Hobby plan includes enough memory (8GB) for Playwright
- Check Railway logs for browser initialization errors
- Dockerfile installs all required dependencies

### Environment Variables Not Working
- Vercel: Environment variables need to be prefixed with `NEXT_PUBLIC_` to be available in browser
- Railway: Restart deployment after changing environment variables

### Slow Scraping
- 100 businesses/day = ~10 minutes of scraping (with enrichment)
- Consider reducing enrichment timeout if needed
- Railway charges $0.000231/min beyond 500 hours

---

## Sharing with Your Friend

Simply share the Vercel URL:
```
https://your-app.vercel.app
```

They can use it directly without any setup!

---

## Security Notes

1. **Rate Limiting**: Consider adding rate limiting to prevent abuse
2. **Authentication**: Add login if you want to restrict access
3. **Data Privacy**: Scraped data includes business information - handle responsibly
4. **2GIS Terms**: Review 2GIS Terms of Service before commercial use

---

## Next Steps

Optional enhancements:

- Add user authentication (NextAuth.js)
- Add rate limiting (Redis + Railway)
- Add scraping history/database (PostgreSQL on Railway)
- Add email notifications when scraping completes
- Add webhook support for integration with other tools

---

**Deployment Complete!** 🚀

Your 2GIS Lead Scraper is now live and accessible worldwide.
