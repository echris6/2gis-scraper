# 🚀 Production Ready - Final Instructions

## ✅ Stable Production URLs

### Frontend (Vercel) - STABLE DOMAIN
**URL:** https://frontend-iota-nine-84.vercel.app
**Status:** ✅ Live with optimized assets
**Features:**
- ✅ Stable domain that won't change
- ✅ Background image optimized (4.9MB → 307KB)
- ✅ Environment configured for Railway backend
- ✅ Smooth loading transitions

### Backend (Railway)
**URL:** https://2gis-scraper-production.up.railway.app
**Status:** ✅ Live and running
**Features:**
- ✅ Playwright browser automation
- ✅ Contact enrichment
- ✅ Full 2GIS scraping

---

## ⚠️ FINAL STEP: Add CORS to Railway

Add this environment variable to Railway:

**Variable Name:** `ALLOWED_ORIGINS`

**Variable Value:**
```
https://frontend-iota-nine-84.vercel.app,http://localhost:3000,http://localhost:3001
```

### How to Add:
1. Go to https://railway.app/
2. Open your **2gis-scraper** project
3. Click **"Variables"** tab
4. Click **"New Variable"**
5. Paste the name and value above
6. Click **"Add"**
7. Railway restarts automatically in ~10 seconds

---

## ✅ After Adding CORS - You're Done!

Visit: **https://frontend-iota-nine-84.vercel.app**

### Test Quick Scraping:
1. City: **moscow**
2. Query: **автомойка**
3. Pages: **1**
4. Enrich: **OFF**
5. Click "Start Scraping"
6. Results in ~3 seconds ⚡

### Test Full Enrichment:
1. Pages: **2**
2. Enrich: **ON** ✅
3. Results in ~1-2 minutes (fetches phone/website for each business)
4. Download CSV to see all data

---

## 📤 Share with Your Friend

**Production URL:**
```
https://frontend-iota-nine-84.vercel.app
```

This URL is **stable** - it won't change with new deployments!

---

## 💰 Monthly Cost

- **Railway:** $5/month (Hobby plan)
- **Vercel:** Free
- **GitHub:** Free
- **Total:** $5/month

**For 100 businesses/day:**
- Daily scraping: ~10 minutes
- Monthly: ~5 hours
- Railway limit: 500 hours/month
- **Headroom:** 99% unused 🎉

---

## 📊 Performance

### Without Enrichment:
- **Speed:** ~3 seconds per page
- **Yield:** 12 businesses per page
- **Use case:** Quick lead discovery

### With Enrichment:
- **Speed:** ~5-10 seconds per business
- **Yield:** Phone + website data
- **Use case:** Qualified lead generation

---

## 🔧 Testing Backend Directly

```bash
# Health check
curl https://2gis-scraper-production.up.railway.app/

# Quick scrape test
curl -X POST https://2gis-scraper-production.up.railway.app/scrape \
  -H "Content-Type: application/json" \
  -d '{"city":"moscow","query":"автомойка","pages":1,"enrich_contacts":false}'
```

---

## 📝 Repository

**GitHub:** https://github.com/echris6/2gis-scraper

All code is committed and up to date!

---

## 🎯 Next Steps (Optional)

1. **Custom Domain:** Add your own domain in Vercel settings
2. **Authentication:** Add login to restrict access
3. **Rate Limiting:** Prevent abuse
4. **Analytics:** Track usage and performance
5. **Database:** Store scraping history

---

## ⚠️ Troubleshooting

### CORS Errors
**Symptom:** Frontend shows "Failed to load" or CORS errors
**Solution:** Verify `ALLOWED_ORIGINS` is added to Railway exactly as shown above

### No Results Returned
**Symptom:** Scraping returns 0 businesses
**Solution:** Check Railway logs for errors, try different city/query

### Slow Performance
**Symptom:** Enrichment takes too long
**Solution:** Normal! Enrichment visits each business page (5-10 sec each)

---

## ✅ Deployment Complete!

**Everything is ready to go once you add the CORS variable to Railway!**

**Production URL:** https://frontend-iota-nine-84.vercel.app

**Backend:** https://2gis-scraper-production.up.railway.app

**Cost:** $5/month

🎉 **Congratulations on deploying your 2GIS Lead Scraper!**
