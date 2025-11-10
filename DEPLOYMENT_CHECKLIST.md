# Deployment Checklist

## Step 1: Backend (Railway) ✓ IN PROGRESS

- [x] Create GitHub repository
- [x] Push code to GitHub
- [x] Create Railway project from GitHub
- [x] Fix PORT environment variable issue
- [ ] Wait for build to complete (~5 minutes)
- [ ] Generate Railway domain
- [ ] Copy Railway URL
- [ ] Test backend endpoint

**Current Status:** Building... (Dockerfile CMD fixed, waiting for deployment)

---

## Step 2: Frontend (Vercel) - PENDING

Once Railway is deployed:

### 2.1 Get Railway URL
1. Go to Railway dashboard
2. Click Settings → Networking
3. Click "Generate Domain"
4. Copy URL (e.g., `https://2gis-scraper-production.up.railway.app`)

### 2.2 Deploy to Vercel

Run from your terminal:

```bash
cd "/Users/echris/Desktop/Yandex Scraper/frontend"
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? **Select your account**
- Link to existing project? **N**
- What's your project's name? **2gis-scraper-frontend** (or any name)
- In which directory is your code located? **./** (current directory)
- Want to override settings? **N**

### 2.3 Add Environment Variable to Vercel

After first deployment:

```bash
vercel env add NEXT_PUBLIC_API_URL
```

When prompted:
- Value: **[paste your Railway URL]**
- Environment: **Production, Preview, Development** (select all)

Then redeploy:

```bash
vercel --prod
```

---

## Step 3: Update CORS - PENDING

Once you have your Vercel URL:

### Option A: Via Railway Dashboard
1. Go to Railway project
2. Click "Variables" tab
3. Add variable:
   - Name: `ALLOWED_ORIGINS`
   - Value: `https://your-vercel-url.vercel.app,http://localhost:3000`

### Option B: Via Railway CLI (if linked)
```bash
railway variables set ALLOWED_ORIGINS="https://your-vercel-url.vercel.app,http://localhost:3000"
```

---

## Step 4: Test Full Stack - PENDING

### Test Backend
```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/
```

Expected response:
```json
{"status":"ok","message":"2GIS Scraper API"}
```

### Test Frontend
1. Visit your Vercel URL
2. Try scraping 1 page without enrichment (fast test)
3. Check browser console for [BACKEND] logs
4. Verify CSV download works

### Test with Enrichment
1. Enable "Enrich with phone/website"
2. Scrape 1-2 pages (will take 5-10 seconds per business)
3. Verify phone and website data appears
4. Download CSV and check columns

---

## Deployment URLs

**GitHub:** https://github.com/echris6/2gis-scraper
**Railway:** [URL will appear after deployment]
**Vercel:** [URL will appear after deployment]

---

## Cost Summary

**Monthly Costs:**
- GitHub: Free
- Railway: $5/month (Hobby plan)
- Vercel: Free (Hobby plan)

**Total: $5/month**

---

## Next Actions

**Right now:**
1. ⏳ Wait for Railway build to complete
2. 📝 Note the Railway URL when it appears
3. 🚀 Deploy frontend to Vercel
4. 🔧 Update CORS settings
5. ✅ Test the full application

**Let me know when Railway deployment shows "ACTIVE" status!**
