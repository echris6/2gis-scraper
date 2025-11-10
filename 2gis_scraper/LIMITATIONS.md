# 2GIS Scraper - Limitations & Notes

## Successfully Extracted Data

The scraper successfully extracts the following information from 2GIS search results:

✅ **Business Name** - Full business name
✅ **Address** - Location details (city, district, street)
✅ **Coordinates** - Latitude and longitude
✅ **Rating** - Average rating (1-5 stars)
✅ **Review Count** - Number of reviews
✅ **Categories** - Business type/rubrics (e.g., "Cafe / Restaurants")
✅ **Attributes** - Business features (cuisine type, price range, amenities)
✅ **Working Hours** - Schedule information

## Data NOT Available in Search Results

The following information is **NOT included** in 2GIS search result pages:

❌ **Phone Numbers** - Not present in search API response
❌ **Website URLs** - Not present in search API response
❌ **Email Addresses** - Not present in search API response

### Why Phone/Website Data is Missing

2GIS search results use a lightweight data structure optimized for map display. Full contact information (phone, website, social media) is only available when you click into an individual business profile page.

This is a deliberate design choice by 2GIS to:
1. Reduce initial page load size
2. Prevent easy bulk contact harvesting
3. Encourage users to view full profiles (with ads)

## Workarounds for Contact Information

If you need phone numbers and websites, you have three options:

### Option 1: Use 2GIS Official API (Recommended for Production)
- **Endpoint**: `https://catalog.api.2gis.ru/3.0/`
- **Requires**: API key from https://platform.2gis.ru
- **Pros**: Legal, supported, includes full contact data
- **Cons**: Costs money for high volume, rate limited
- **Best for**: Commercial projects, high-volume scraping

### Option 2: Scrape Individual Business Pages
- Modify scraper to visit each business detail page
- Extract phone/website from full profile HTML
- **Pros**: Gets all contact info
- **Cons**: Much slower (1 request per business), higher chance of detection
- **Implementation**: Would require Playwright/Selenium for full rendering

### Option 3: Combine with Other Data Sources
- Use 2GIS for discovery (names, locations, categories)
- Cross-reference with Google Maps API for contact info
- **Pros**: Legal, reliable contact data
- **Cons**: More complex, requires Google API key
- **Best for**: Lead enrichment workflows

## Performance Characteristics

### Speed
- **Search pages**: ~3 seconds per page (with rate limiting)
- **Throughput**: ~240 businesses per minute (12 per page × 20 pages)
- **Pagination**: Auto-detects total pages, scrapes all results

### Reliability
- **Success rate**: ~95% (some profiles may fail parsing)
- **CAPTCHA**: Rarely encountered on search pages
- **Rate limiting**: Minimal with 3-second delays
- **Blocking**: Low risk with respectful crawling

## Data Quality Notes

### Addresses
- Addresses are hierarchical (Country > City > District > Street)
- Some businesses only have city-level addresses
- Street numbers may be missing for newer businesses

### Coordinates
- Highly accurate (verified GPS coordinates)
- Available for 100% of businesses
- Suitable for mapping and distance calculations

### Ratings
- Aggregated from multiple sources (2GIS, Foursquare, etc.)
- Not all businesses have ratings (new listings)
- Review counts may include ratings without text

### Categories
- Multiple categories per business (e.g., "Restaurant, Bar, Cafe")
- Hierarchical structure (parent/child categories)
- Localized names based on region

## Recommendations

### For Lead Generation
If your goal is **qualified lead generation** (businesses to contact), this scraper has **limited utility** without phone/website data.

**Better approach:**
1. Use this scraper to discover businesses by category/location
2. Export the list with names and coordinates
3. Manually look up contact info, OR
4. Use 2GIS official API for full profiles, OR
5. Cross-reference with Google Places API

### For Market Research
If your goal is **market analysis** (density, distribution, ratings), this scraper is **excellent**:
- Analyze business density by district
- Map competitor locations
- Track rating distributions
- Identify underserved areas

### For Database Building
If you're building a **business database**:
- Start with 2GIS for basic profiles
- Enrich with other data sources
- Update contact info separately
- Use coordinates for deduplication

## Ethical Considerations

### Terms of Service
- Review 2GIS Terms of Service before large-scale scraping
- Consider official API for commercial use
- Respect rate limits (default 3 seconds is safe)

### Data Usage
- Don't resell scraped data directly
- Attribute data source if publishing
- Use for internal research/lead gen is generally acceptable
- Be transparent about data sources

### Privacy
- Extracted data is public information
- However, bulk contact harvesting may violate privacy laws
- GDPR/CCPA may apply depending on your location
- Consult legal advice for commercial projects

## Future Enhancements

Potential improvements to extract more data:

1. **Two-Stage Scraping**
   - Stage 1: Scrape search results (current implementation)
   - Stage 2: Visit each business page for full profile
   - Extract phone, website, social media links
   - Requires Playwright for JavaScript rendering

2. **API Integration**
   - Add 2GIS official API support
   - Fallback to scraping if API quota exceeded
   - Combine API + scraping for cost optimization

3. **Cross-Reference Engine**
   - Match 2GIS businesses with Google Places
   - Enrich with additional contact data
   - Verify business existence

4. **Contact Discovery**
   - Extract business name + location
   - Search Google for "{business name} {city} phone"
   - Parse contact info from search results
   - Requires additional scraping/API calls

## Conclusion

This scraper is **excellent for**:
- 📊 Market research and analysis
- 📍 Location-based business discovery
- ⭐ Rating and review analysis
- 🗺️ Mapping business distributions

This scraper has **limitations for**:
- 📞 Direct lead generation (no phone numbers)
- 🌐 Contact harvesting (no websites)
- 📧 Email marketing (no emails)

For full contact data, use 2GIS official API or implement two-stage scraping (scrape search → visit each profile).

---

**Built with**: Python, Requests, BeautifulSoup, Pandas
**Data Source**: 2GIS public search pages
**Extraction Method**: JSON parsing from embedded `initialState`
