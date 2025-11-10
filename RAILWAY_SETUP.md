# Railway Setup Instructions

## Current Status
✓ Repository pushed to GitHub: https://github.com/echris6/2gis-scraper
🔄 Railway deployment initializing...

## Next Steps After Build Completes

### 1. Configure Environment Variables

Once the build finishes, go to the **Variables** tab in Railway and add:

```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

*(We'll update this with your Vercel URL later)*

### 2. Get Your Railway URL

After deployment completes:
1. Click on **Settings** tab
2. Scroll to **Networking** section
3. Click **Generate Domain**
4. Copy the URL (will be something like `https://2gis-scraper-production.up.railway.app`)

### 3. Test the Backend

Once you have the Railway URL, test it:

```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/
```

You should see:
```json
{"status":"ok","message":"2GIS Scraper API"}
```

### 4. Monitor Logs

- Click **View logs** to see deployment progress
- Check for any errors during Playwright installation
- The build should take 3-5 minutes (Playwright browser installation takes time)

## Troubleshooting

### Build Fails
- Check logs for specific error
- Most common: Out of memory (shouldn't happen with Hobby plan)
- Solution: Railway Hobby has 8GB RAM, plenty for Playwright

### Runtime Errors
- Check deployment logs
- Look for browser initialization errors
- Verify all dependencies installed correctly

## Expected Build Time
- **Initialization**: 5-10 seconds ✓
- **Build**: 3-5 minutes (Playwright chromium download is large)
- **Deploy**: 10-20 seconds
- **Total**: ~5 minutes

## What's Happening During Build

1. ✓ Taking snapshot of code
2. 🔄 Installing system dependencies (libgtk-3-0, libnss3, etc.)
3. 🔄 Installing Python packages
4. 🔄 Installing Playwright chromium (~150MB download)
5. 🔄 Starting uvicorn server

---

**Wait for build to complete, then we'll configure variables and get your Railway URL!**
