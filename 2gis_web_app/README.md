# 2GIS Business Scraper - Web Interface

Clean, minimal web interface for scraping 2GIS business listings across 50+ cities.

## Quick Start

### 1. Install Dependencies

```bash
cd 2gis_web_app
pip install -r requirements.txt
playwright install chromium  # Only needed if using enrichment
```

### 2. Run the Web App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Features

### Basic Scraping (Fast)
- Search businesses by category (e.g., "restaurant", "car wash", "gym")
- Select from 50+ cities across Russia, UAE, Kazakhstan, and more
- Scrape multiple pages (each page ~12 businesses)
- Get basic data: name, address, rating, reviews, category

**Time**: ~3 seconds per page

### Contact Enrichment (Slow but Accurate)
- Visit each business page individually
- Extract phone numbers and websites
- Find TRUE "qualified leads" (businesses without websites)
- Requires phone number filter

**Time**: ~8 seconds per business

### Advanced Filters
- Minimum rating (e.g., only 4.5+ stars)
- Minimum review count (e.g., only 10+ reviews)
- No website only (qualified leads for web development outreach)
- Require phone number (contactable businesses)

### Export Options
- Download as CSV
- Download as JSON
- Download qualified leads only (businesses without websites)

## Usage Examples

### Example 1: Quick Market Research
**Goal**: See what car washes exist in Dubai

**Settings**:
- City: Dubai
- Query: car wash
- Pages: 3
- Enrichment: OFF

**Result**: ~36 businesses in ~9 seconds with basic info

### Example 2: Find Qualified Leads
**Goal**: Find car washes without websites to offer web development services

**Settings**:
- City: Dubai
- Query: car wash
- Pages: 2
- Enrichment: ON ✓
- Advanced Filters:
  - No website only ✓
  - Require phone number ✓
  - Minimum rating: 4.0

**Result**: ~5-10 qualified leads in ~3-5 minutes with verified contact info

### Example 3: High-Quality Restaurants
**Goal**: Find top-rated restaurants with contact info

**Settings**:
- City: Moscow
- Query: restaurant
- Pages: 5
- Enrichment: ON ✓
- Advanced Filters:
  - Minimum rating: 4.5
  - Minimum reviews: 50

**Result**: ~20-30 high-quality restaurants with phone/website in ~5-8 minutes

## Understanding the Results

### Data Fields

| Field | Description | Always Available? |
|-------|-------------|-------------------|
| Name | Business name | ✓ Yes |
| Address | Full address | ✓ Yes |
| Rating | Star rating (0-5) | ✓ Yes |
| Review Count | Number of reviews | ✓ Yes |
| Rubric | Category/type | ✓ Yes |
| Latitude/Longitude | GPS coordinates | ✓ Yes |
| Phone | Phone number | Only with enrichment |
| Website | Website URL | Only with enrichment |

### Summary Statistics

The app shows:
- **Total Businesses**: All businesses found
- **With Phone**: Businesses that have phone numbers (enrichment only)
- **With Website**: Businesses that have websites (enrichment only)
- **Avg Rating**: Average rating across all businesses
- **Qualified Leads**: Businesses WITHOUT websites (potential web dev clients)

## Performance Tips

### Fast Testing
- Start with 1-2 pages
- Turn enrichment OFF
- No filters

**Time**: ~5-10 seconds

### Production Lead Generation
- Use 5-10 pages
- Turn enrichment ON
- Enable filters (no website, require phone, min rating)

**Time**: 5-15 minutes depending on results

### Known Limitations

1. **Enrichment is slow**: ~8 seconds per business
   - Solution: Use filters to reduce dataset first
   - Or scrape without enrichment, then enrich top results manually

2. **Headless browser detection**: 2GIS may detect automated browsers
   - Symptom: "0 with phone, 0 with website" despite enrichment
   - Solution: Documented in main scraper README
   - Quick fix: Edit main.py line 248 to use `headless=False`

3. **Rate limiting**: Too many requests may get blocked
   - Solution: Use delays (default 3 seconds is safe)
   - Or use residential proxies for production scale

## File Structure

```
2gis_web_app/
├── app.py                 # Streamlit web interface
├── scraper_wrapper.py     # Bridge between UI and scraper
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .streamlit/
    └── config.toml       # Streamlit configuration
```

## Troubleshooting

### "Module not found" errors
Install dependencies:
```bash
pip install -r requirements.txt
```

### Enrichment not working (0 with phone/website)
This is likely headless browser detection. See the main [ENRICHMENT_GUIDE.md](../2gis_scraper/ENRICHMENT_GUIDE.md) for solutions.

### App is slow
- Reduce number of pages
- Turn off enrichment for testing
- Use filters to reduce results

### No results found
- Try different search query
- Check if city is spelled correctly
- Some cities may have limited 2GIS coverage

## Advanced Configuration

### Custom Delays
Edit `scraper_wrapper.py` to change default delay:
```python
def scrape_with_progress(..., delay: float = 3.0):
    # Change to 5.0 for more conservative rate limiting
```

### Non-Headless Mode
If enrichment is being blocked, edit `scraper_wrapper.py` line 106:
```python
all_businesses = enrich_businesses(
    all_businesses,
    city=city,
    headless=False,  # Changed from True - opens visible browser
    delay=delay
)
```

### Add More Cities
Edit `../2gis_scraper/config.py` to add cities:
```python
CITY_TLD_MAP = {
    'your_city': 'country_tld',  # e.g., 'paris': 'fr'
    # ...
}
```

## Architecture

This web app is a thin wrapper around the core 2GIS scraper:

```
User Browser
    ↓
Streamlit UI (app.py)
    ↓
Scraper Wrapper (scraper_wrapper.py) - Progress tracking
    ↓
Core Scraper (../2gis_scraper/)
    ↓
2GIS Website
```

The wrapper:
- Provides real-time progress updates
- Handles async operations
- Formats data for display
- Manages exports

## Support

For issues with:
- **Web interface**: Check this README
- **Scraping functionality**: See [../2gis_scraper/README.md](../2gis_scraper/README.md)
- **Enrichment**: See [../2gis_scraper/ENRICHMENT_GUIDE.md](../2gis_scraper/ENRICHMENT_GUIDE.md)
- **Data quality**: See [../2gis_scraper/LIMITATIONS.md](../2gis_scraper/LIMITATIONS.md)

## Next Steps

1. **Test it**: Run with 1 page, no enrichment
2. **Find qualified leads**: Enable enrichment + "no website only" filter
3. **Export results**: Download CSV for outreach
4. **Scale up**: Increase pages once you verify it works

---

**Built with Streamlit** | Clean, minimal UI for 2GIS lead generation
