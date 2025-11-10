# 🔍 Debug: Playwright Activation Investigation

## What We Added (v2.1-debug)

### 1. API Endpoint Debug Logging
**File:** `api/main.py:86-90`

Added direct environment variable checking in the `/scrape` endpoint:
```python
use_playwright_env = os.getenv('USE_PLAYWRIGHT', 'NOT SET')
logger.info(f"=== ENVIRONMENT CHECK ===")
logger.info(f"USE_PLAYWRIGHT env var: {use_playwright_env}")
logger.info(f"All env vars with PLAYWRIGHT: {[k for k in os.environ.keys() if 'PLAY' in k]}")
```

### 2. Module-Level Print Statements
**File:** `2gis_scraper/scraper.py:24-38`

Added `print()` statements (will appear in Railway stdout):
```python
print(f"[SCRAPER MODULE] USE_PLAYWRIGHT environment variable: {USE_PLAYWRIGHT_ENV}")
print(f"[SCRAPER MODULE] Playwright mode: {'ENABLED' if USE_PLAYWRIGHT else 'DISABLED'}")
```

---

## What to Look For

### Test the deployment:
1. Visit: https://frontend-iota-nine-84.vercel.app
2. Try scraping 1 page (moscow, автомойка)
3. Check the logs in the browser

### Expected Debug Output (if working):

```
[INFO] === ENVIRONMENT CHECK ===
[INFO] USE_PLAYWRIGHT env var: true
[INFO] All env vars with PLAYWRIGHT: ['USE_PLAYWRIGHT']
[INFO] Initializing scraper for moscow - автомойка
[INFO] USE_PLAYWRIGHT environment variable: true
[INFO] Playwright mode: ENABLED
[INFO] ✓ Playwright successfully imported
```

### If Still Not Working:

If you DON'T see these debug messages, it means one of:
1. **Railway hasn't finished rebuilding yet** - Wait 2-3 minutes
2. **Environment variable not available at startup** - Railway issue
3. **Module caching issue** - Railway needs manual restart

---

## How to Check Railway Deployment Status

Railway should auto-deploy when GitHub is updated. To verify:

1. Go to https://railway.app/
2. Open your **2gis-scraper** project
3. Click **"Deployments"** tab
4. Look for the latest deployment with commit message: "Add debug logging..."
5. Status should show **"Success"** or **"Active"**
6. Click on the deployment to see build logs

---

## Manual Railway Restart (If Needed)

If Railway built successfully but still not working:

1. Go to https://railway.app/
2. Open your **2gis-scraper** project
3. Click **"Settings"** tab
4. Scroll down to **"Danger Zone"**
5. Click **"Restart"**

This forces Railway to reload everything fresh.

---

## Verification Checklist

- [ ] Railway deployment shows "Success"
- [ ] `curl https://2gis-scraper-production.up.railway.app/` returns `{"version":"2.0-playwright"}`
- [ ] Scraping attempt shows `=== ENVIRONMENT CHECK ===` in logs
- [ ] Logs show `USE_PLAYWRIGHT env var: true`
- [ ] Logs show `Playwright mode: ENABLED`
- [ ] Scraping returns results (not 0 businesses)

---

## Current Status

**Deployed:** ✅ Code pushed to GitHub (commit 2365f5b)
**Railway:** ⏳ Should auto-deploy in 2-3 minutes
**Variables:** ✅ `USE_PLAYWRIGHT=true` set in Railway

**Next:** Try scraping and share the logs!

---

## If Playwright Still Doesn't Activate

If you still see:
- No `=== ENVIRONMENT CHECK ===` message
- No `[SCRAPER MODULE]` messages
- Still getting "Could not find initialState" error

Then we know Railway isn't loading the new code, and we need to:
1. Check Railway build logs for errors
2. Try manual restart
3. Verify GitHub webhook is working
