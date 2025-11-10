# 2GIS Scraper - Quick Start Guide

Get up and running in 5 minutes!

## Installation

```bash
cd 2gis_scraper
pip install -r requirements.txt
```

## Basic Usage

### 1. Simple Search (Auto-detect all pages)
```bash
python main.py --city dubai --query "restaurant"
```

**Output**: `output/businesses.csv` with all restaurants in Dubai

### 2. Limited Pages (Faster)
```bash
python main.py --city dubai --query "cafe" --pages 3
```

**Output**: First 3 pages (~36 businesses)

### 3. Export to JSON
```bash
python main.py --city moscow --query "barbershop" --format json
```

**Output**: `output/businesses.json`

### 4. Both Formats
```bash
python main.py --city dubai --query "gym" --format both
```

**Output**: Both CSV and JSON files

## Useful Commands

### Find High-Rated Businesses
```bash
python main.py --city dubai --query "restaurant" --min-rating 4.5
```

### Limit to Popular Places
```bash
python main.py --city moscow --query "cafe" --min-reviews 50
```

### Fresh Data (No Cache)
```bash
python main.py --city dubai --query "spa" --no-cache
```

### Clear Cache Before Running
```bash
python main.py --city dubai --query "restaurant" --clear-cache
```

## Supported Cities

### UAE
- dubai
- abu_dhabi
- sharjah

### Russia
- moscow
- spb (St. Petersburg)
- novosibirsk
- kazan

### Kazakhstan
- almaty
- astana

### Other
- bishkek (Kyrgyzstan)
- santiago (Chile)
- prague (Czech Republic)

[See config.py for full list]

## Output Data

Your CSV will include:

| Column | Description | Example |
|--------|-------------|---------|
| id | Business ID | 70000001089452553 |
| name | Business name | "Sakhalin Dubai" |
| address | Full address | "Dubai, Jumeirah 1" |
| latitude | GPS coordinate | 25.227487 |
| longitude | GPS coordinate | 55.257372 |
| rating | Average rating | 4.5 |
| review_count | Number of reviews | 123 |
| rubric | Category | "Cafe / Restaurants" |
| attributes | Features | "WiFi; Parking; Delivery" |
| hours | Working schedule | "Mon-Fri: 9:00-22:00" |

**NOTE**: Phone and website fields will be empty (see LIMITATIONS.md)

## Common Issues

### "No results found"
- Check city name spelling
- Use underscores: `saint_petersburg` not `saint petersburg`
- Try broader search terms

### Slow scraping
- Default delay is 3 seconds (safe)
- Reduce with `--delay 2` (not recommended)
- Use `--pages 5` to limit results

### Want to scrape many cities?
```bash
# Loop through cities
for city in dubai moscow almaty; do
  python main.py --city $city --query "restaurant" --output "${city}_restaurants.csv"
done
```

## Examples

### Example 1: Dubai Car Washes
```bash
python main.py \
  --city dubai \
  --query "car wash" \
  --pages 5 \
  --output dubai_car_washes.csv
```

### Example 2: Moscow Restaurants (High-Rated Only)
```bash
python main.py \
  --city moscow \
  --query "restaurant" \
  --min-rating 4.0 \
  --min-reviews 20 \
  --pages 10
```

### Example 3: Multi-Category Search
```bash
python main.py \
  --city dubai \
  --queries "cafe" "restaurant" "bar" \
  --pages 3 \
  --format both
```

## Next Steps

1. **Read LIMITATIONS.md** - Understand what data is available
2. **Check README.md** - Full documentation
3. **Modify config.py** - Customize settings
4. **View the code** - parser.py, scraper.py for details

## Getting Help

```bash
# Show all options
python main.py --help

# Enable debug logging
python main.py --city dubai --query "cafe" --log-level DEBUG
```

## Pro Tips

1. **Start small**: Test with `--pages 1` first
2. **Use cache**: Helps during development (automatic)
3. **Export JSON**: Easier to process programmatically
4. **Be respectful**: Don't hammer servers (keep default delay)
5. **Check logs**: `2gis_scraper.log` has detailed info

Happy scraping! 🎯
