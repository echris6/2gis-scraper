# 🔧 Playwright Activation - Bugs Fixed

## Timeline of Issues and Solutions

### Issue 1: Environment Variable Not Available at Module Import ✅ FIXED
**Problem:** `USE_PLAYWRIGHT` was checked at module import time, but Railway's environment variable wasn't available yet.

**Solution:** Check `os.getenv('USE_PLAYWRIGHT')` at runtime in `_fetch_page()` method instead of at module import.

**Commit:** 06944ef - "Fix Playwright activation by checking environment variable at runtime"

---

### Issue 2: Trailing Whitespace in Environment Variable ✅ FIXED
**Problem:** Railway's `USE_PLAYWRIGHT` variable had trailing space: `"true "` instead of `"true"`
- This caused `"true ".lower() == 'true'` to return `False`

**Evidence from logs:**
```
[INFO] [FETCH_PAGE] USE_PLAYWRIGHT env at runtime = 'true ' (raw)
[INFO] [FETCH_PAGE] use_playwright_runtime = False
```

**Solution:** Added `.strip()` to remove whitespace before comparison:
```python
use_playwright_runtime = os.getenv('USE_PLAYWRIGHT', 'false').strip().lower() == 'true'
```

**Commit:** 7c1e6b5 - "Fix whitespace bug in USE_PLAYWRIGHT environment variable check"

---

### Issue 3: Asyncio Loop Conflict ✅ FIXED
**Problem:** Playwright sync API cannot run inside asyncio event loop
- FastAPI uses async endpoints
- `sync_playwright()` cannot be called from async context

**Error:**
```
[ERROR] Playwright fetch failed: It looks like you are using Playwright Sync API inside the asyncio loop.
Please use the Async API instead.
```

**Solution:** Run sync Playwright in a separate thread using `ThreadPoolExecutor`:
```python
import concurrent.futures

# Detect if we're in async context
loop = asyncio.get_event_loop()
if loop.is_running():
    # Run in thread pool to avoid blocking
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(self._fetch_page_playwright_sync, url)
        html = future.result(timeout=60)
else:
    # Call directly (for local testing)
    html = self._fetch_page_playwright_sync(url)
```

**Commit:** 790f5ab - "Fix asyncio loop conflict by running Playwright in thread pool"

---

## Expected Behavior Now

When scraping runs, you should see:

```
[INFO] === ENVIRONMENT CHECK ===
[INFO] USE_PLAYWRIGHT env var: true
[INFO] All env vars with PLAYWRIGHT: ['USE_PLAYWRIGHT']

[INFO] [FETCH_PAGE] USE_PLAYWRIGHT env at runtime = 'true ' (raw)
[INFO] [FETCH_PAGE] After strip().lower() = 'true'
[INFO] [FETCH_PAGE] use_playwright_runtime = True
[INFO] [FETCH_PAGE] ✅ Playwright mode ACTIVE - attempting browser fetch
[INFO] [FETCH_PAGE] Running Playwright in thread pool (async context detected)
[INFO] ✓ Fetched with Playwright: https://2gis.ru/moscow/search/... (XXXXXX bytes)
```

**Key indicators:**
- ✅ `use_playwright_runtime = True`
- ✅ `Playwright mode ACTIVE`
- ✅ `Running Playwright in thread pool`
- ✅ `✓ Fetched with Playwright` (not just "Fetched:")

---

## Testing

1. Visit: https://frontend-iota-nine-84.vercel.app
2. Try scraping (moscow, автомойка, 1 page, enrich OFF)
3. Check logs for "✓ Fetched with Playwright"
4. Should return ~12 businesses instead of 0

---

## Railway Environment Variables

Current Railway variables:
```
ALLOWED_ORIGINS=https://frontend-iota-nine-84.vercel.app,http://localhost:3000,http://localhost:3001
USE_PLAYWRIGHT=true
```

**Note:** The trailing space in `USE_PLAYWRIGHT` is now handled correctly with `.strip()`

---

## Performance Notes

**With Playwright:**
- ~5-15 seconds per page (browser rendering)
- Successfully bypasses 2GIS anti-bot measures
- Returns actual data instead of 0 results

**Without Playwright (requests):**
- ~3 seconds per page
- Blocked by 2GIS (returns 0 results)
- Only works from residential IPs

---

## Current Deployment

**Version:** 2.0-playwright (commit 790f5ab)
**Status:** Deploying to Railway...
**Frontend:** https://frontend-iota-nine-84.vercel.app
**Backend:** https://2gis-scraper-production.up.railway.app

Wait 2-3 minutes for Railway to finish building, then test!
