# 2GIS Business Scraper

Extract qualified business leads from 2GIS across Russia, UAE, Kazakhstan, and other supported regions.

## Why 2GIS Over Yandex Maps?

- **Easier to scrape**: Minimal anti-bot protection, no CAPTCHA on initial loads
- **Better data structure**: All business data embedded in initial HTML as JSON
- **More reliable**: Less aggressive blocking, simpler architecture
- **Rich data**: Phone, address, ratings, hours, attributes all available
- **Website detection**: Perfect for finding businesses WITHOUT websites (qualified leads)

## Features

✅ **Fast JSON Extraction**: Leverages embedded `initialState` JSON - no browser automation needed
✅ **Multi-Region Support**: Russia, UAE, Kazakhstan, Chile, Cyprus, Czech Republic, Italy
✅ **Lead Filtering**: Find businesses without websites for qualified lead generation
✅ **Smart Caching**: Avoid redundant requests with built-in HTML caching
✅ **Rate Limiting**: Respectful crawling with configurable delays
✅ **Flexible Export**: CSV and JSON output with customizable fields
✅ **Pagination Auto-Detection**: Automatically scrapes all available pages
✅ **Deduplication**: Removes duplicate businesses across queries

## Installation

```bash
# Navigate to scraper directory
cd 2gis_scraper

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```bash
# Scrape restaurants in Dubai (auto-detect all pages)
python main.py --city dubai --query "restaurant"

# Scrape 5 pages of cafes in Moscow
python main.py --city moscow --query "cafe" --pages 5

# Find auto detailing shops WITHOUT websites (qualified leads)
python main.py --city dubai --query "auto detailing" --no-website-only
```

### Advanced Usage

```bash
# Multiple queries with rating filter
python main.py --city almaty --queries "barbershop" "salon" "spa" \
  --min-rating 4.0 --pages 3

# Export qualified leads with phone numbers
python main.py --city moscow --query "car wash" \
  --no-website-only --require-phone --export-leads

# Custom output location and format
python main.py --city dubai --query "gym" \
  --format both --output dubai_gyms.csv --output-dir exports

# Fresh data (no cache)
python main.py --city spb --query "restaurant" \
  --no-cache --pages 2
```

## Command-Line Options

### Required Arguments

- `--city` - City name (moscow, dubai, almaty, etc.)
- `--query` or `--queries` - Search query/queries

### Scraping Options

- `--pages` - Max pages to scrape (default: auto-detect all)
- `--delay` - Delay between requests in seconds (default: 3)
- `--no-cache` - Disable caching
- `--clear-cache` - Clear cache before scraping

### Filtering Options

- `--no-website-only` - Only businesses WITHOUT websites (qualified leads)
- `--min-rating` - Minimum rating (e.g., 4.0)
- `--min-reviews` - Minimum review count
- `--require-phone` - Only businesses with phone numbers

### Output Options

- `--output` - Output filename (default: businesses.csv)
- `--format` - Output format: csv, json, both (default: csv)
- `--output-dir` - Output directory (default: output/)
- `--export-leads` - Also export qualified_leads.csv

### Logging

- `--log-level` - DEBUG, INFO, WARNING, ERROR (default: INFO)
- `--log-file` - Enable file logging

## Supported Cities

### Russia (.ru)
moscow, spb, petersburg, novosibirsk, ekaterinburg, kazan, nizhny_novgorod, chelyabinsk, samara, omsk, rostov, ufa, krasnoyarsk, voronezh, perm, volgograd

### UAE (.ae)
dubai, abu_dhabi, sharjah, ajman

### Kazakhstan (.kz)
almaty, astana, nur_sultan, shymkent, karaganda

### Other Regions
- Kyrgyzstan: bishkek, osh
- Chile: santiago
- Cyprus: nicosia, limassol
- Czech Republic: prague
- Italy: milan, rome

## Output Data Fields

### CSV Columns

| Field | Description |
|-------|-------------|
| id | Business ID |
| name | Business name |
| address | Full address |
| phone | Phone number |
| website | Website URL (if exists) |
| rating | Average rating (0-5) |
| review_count | Number of reviews |
| rubric | Business categories |
| latitude | Latitude coordinate |
| longitude | Longitude coordinate |
| hours | Working hours |
| attributes | Business features (WiFi, parking, etc.) |
| has_website | Yes/No flag |
| has_phone | Yes/No flag |

### JSON Structure

Full nested data including:
- Complete address breakdown
- Coordinates (lat/lon)
- Detailed schedule with day-by-day hours
- Full attribute list with categories
- Review statistics
- Business categories/rubrics

## Examples

### Example 1: Find Car Detailing Leads in Dubai

```bash
python main.py \
  --city dubai \
  --query "car detailing" \
  --no-website-only \
  --require-phone \
  --min-rating 3.5 \
  --output dubai_detailing_leads.csv
```

**Output**: CSV with car detailing businesses that:
- Don't have a website (qualified leads)
- Have a phone number (contactable)
- Have at least 3.5 rating (quality filter)

### Example 2: Multi-Query Restaurant Research

```bash
python main.py \
  --city moscow \
  --queries "italian restaurant" "sushi restaurant" "steakhouse" \
  --pages 5 \
  --format both \
  --export-leads \
  --output moscow_restaurants
```

**Output**:
- `moscow_restaurants.csv` - All restaurants
- `moscow_restaurants.json` - Full data with nested fields
- `moscow_restaurants_qualified_leads.csv` - Restaurants without websites

### Example 3: Quick Test Run

```bash
python main.py \
  --city dubai \
  --query "cafe" \
  --pages 1 \
  --log-level DEBUG
```

**Output**: Debug logs showing JSON extraction process + 1 page of results

## Architecture

```
2gis_scraper/
├── main.py              # CLI entry point
├── scraper.py           # Core scraping engine
├── parser.py            # JSON extraction & parsing
├── exporter.py          # Data export & filtering
├── cache_manager.py     # HTML caching system
├── config.py            # Configuration settings
├── requirements.txt     # Dependencies
├── cache/              # Cached HTML responses
│   └── search/
└── output/             # Exported data files
    ├── businesses.csv
    ├── businesses.json
    └── qualified_leads.csv
```

## How It Works

1. **URL Construction**: Builds 2GIS search URL for city/query/page
2. **HTTP Request**: Fetches HTML (checks cache first)
3. **JSON Extraction**: Extracts `initialState` JSON from HTML using regex
4. **Data Parsing**: Parses business profiles from JSON
5. **Pagination**: Auto-detects total pages, scrapes all results
6. **Filtering**: Applies lead qualification filters
7. **Deduplication**: Removes duplicate businesses
8. **Export**: Outputs to CSV/JSON with selected fields

## Performance

- **Speed**: ~2-3 seconds per page (with rate limiting)
- **Efficiency**: 10x faster than browser automation
- **Resource Usage**: Minimal (no browser overhead)
- **Reliability**: High (no CAPTCHA, minimal blocking)

## Best Practices

### Rate Limiting
- Default 3-second delay between requests is respectful
- Increase delay for high-volume scraping: `--delay 5`
- Use caching to avoid re-scraping same queries

### Large Scraping Jobs
- Start with 1-2 pages to test: `--pages 2`
- Enable caching for retries: cache is ON by default
- Use `--log-level DEBUG` to monitor progress
- Export qualified leads separately: `--export-leads`

### Finding Qualified Leads
- Use `--no-website-only` to filter businesses without websites
- Add `--require-phone` to ensure contactability
- Use `--min-rating 3.0` to filter low-quality businesses
- Combine filters for best leads

### Cache Management
- Cache speeds up development and testing
- Clear cache for fresh data: `--clear-cache`
- Disable for production runs: `--no-cache`
- Cache is stored in `cache/search/` directory

## Troubleshooting

### No results found
- Check city name spelling (use underscores: `saint_petersburg` not `saint petersburg`)
- Try broader query terms
- Use `--log-level DEBUG` to see extraction details

### JSON extraction failed
- 2GIS may have changed page structure (rare)
- Check if you're being rate-limited (try `--delay 5`)
- Disable cache and retry: `--no-cache`

### Slow scraping
- Reduce delay (not recommended): `--delay 2`
- Limit pages: `--pages 3`
- Use cache for repeated queries

## Configuration

Edit `config.py` to customize:

- **CITY_TLD_MAP**: Add new cities/regions
- **USER_AGENTS**: Rotate user agents for stealth
- **DEFAULT_DELAY**: Change default rate limiting
- **FILTER_***: Set default filters
- **DEFAULT_OUTPUT_DIR**: Change output location

## Comparison: 2GIS vs Yandex Maps

| Aspect | 2GIS | Yandex Maps |
|--------|------|-------------|
| Anti-Bot Protection | Minimal | Strict |
| CAPTCHA | Rarely | Frequently |
| Data Access | Embedded JSON | Complex API/JSON |
| Scraping Difficulty | Easy | Hard |
| Maintenance | Low | High |
| Recommended Tool | Requests | Selenium/Playwright |
| Speed | Fast | Slow |

## Legal & Ethical Considerations

- Respect robots.txt and terms of service
- Use reasonable rate limiting (3+ seconds)
- Don't overwhelm servers with requests
- Consider official API for commercial use
- Attribute data source if publishing

## Future Enhancements

Possible improvements:

- [ ] Proxy rotation for high-volume scraping
- [ ] Multi-threading for faster scraping
- [ ] Official API integration option
- [ ] More export formats (Excel, SQLite)
- [ ] Advanced attribute filtering
- [ ] Photo/review extraction
- [ ] Email extraction from websites
- [ ] Social media link extraction

## License

This tool is for educational and research purposes. Use responsibly.

## Support

For issues or questions:
1. Check logs with `--log-level DEBUG`
2. Review the examples above
3. Verify city name in `config.py`
4. Test with `--pages 1` first

---

**Happy Lead Hunting! 🎯**
