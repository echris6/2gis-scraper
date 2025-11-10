"""
Wrapper module for integrating 2GIS scraper with Streamlit web interface
Provides progress tracking and simplified API for the web app
"""

import sys
import logging
from pathlib import Path
from typing import Generator, Dict, List, Optional

# Add parent 2gis_scraper directory to path
scraper_dir = Path(__file__).parent.parent / '2gis_scraper'
sys.path.insert(0, str(scraper_dir))

# Import scraper modules
from scraper import TwoGISScraper
from exporter import DataExporter
from profile_scraper import enrich_businesses
import config

# Configure logging to show in terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def get_city_list() -> List[str]:
    """
    Get list of available cities for scraping

    Returns:
        Sorted list of city names
    """
    cities = sorted(config.CITY_TLD_MAP.keys())
    return cities


def scrape_with_progress(
    city: str,
    query: str,
    max_pages: int = 5,
    enrich_contacts: bool = False,
    min_rating: Optional[float] = None,
    min_reviews: Optional[int] = None,
    no_website_only: bool = False,
    require_phone: bool = False,
    delay: float = 3.0
) -> Generator[Dict, None, None]:
    """
    Scrape 2GIS with real-time progress updates

    Yields progress dictionaries with:
        - progress: float 0.0-1.0
        - status: str description
        - count: int total businesses found
        - current_page: int current page number
        - total_pages: int total pages to scrape
        - qualified_count: int businesses without websites (if filtering)
        - businesses: List[Dict] final results (only in last yield)

    Args:
        city: City to scrape
        query: Search query
        max_pages: Maximum pages to scrape
        enrich_contacts: Visit profile pages for phone/website
        min_rating: Minimum rating filter
        min_reviews: Minimum review count filter
        no_website_only: Only businesses without websites
        require_phone: Only businesses with phone numbers
        delay: Delay between requests in seconds
    """

    # Initialize
    yield {
        'progress': 0.0,
        'status': f'Initializing scraper for {city}...',
        'count': 0,
        'current_page': 0,
        'total_pages': max_pages
    }

    # Stage 1: Scrape search results
    try:
        scraper = TwoGISScraper(delay=delay)
        exporter = DataExporter()

        all_businesses = []

        # Scrape pages with progress tracking
        for page in range(1, max_pages + 1):
            yield {
                'progress': (page - 1) / max_pages * 0.5,  # First 50% for search
                'status': f'Scraping page {page}/{max_pages}...',
                'count': len(all_businesses),
                'current_page': page,
                'total_pages': max_pages
            }

            # Scrape single page
            page_businesses = scraper.scrape_page(city, query, page)

            if not page_businesses:
                # No more results
                yield {
                    'progress': 0.5,
                    'status': f'No more results found on page {page}',
                    'count': len(all_businesses),
                    'current_page': page,
                    'total_pages': page
                }
                break

            all_businesses.extend(page_businesses)

            yield {
                'progress': page / max_pages * 0.5,
                'status': f'Found {len(page_businesses)} businesses on page {page}',
                'count': len(all_businesses),
                'current_page': page,
                'total_pages': max_pages
            }

        # Stage 2: Enrich with contact info if requested
        if enrich_contacts and all_businesses:
            yield {
                'progress': 0.5,
                'status': f'Starting contact enrichment for {len(all_businesses)} businesses...',
                'count': len(all_businesses)
            }

            # Enrich businesses (this is slow ~8 sec per business)
            # We'll track progress by monitoring the enrichment
            total_to_enrich = len(all_businesses)

            # Use the synchronous wrapper which handles async internally
            all_businesses = enrich_businesses(
                all_businesses,
                city=city,
                headless=True,
                delay=delay
            )

            # Count results
            with_phone = sum(1 for b in all_businesses if b.get('phone'))
            with_website = sum(1 for b in all_businesses if b.get('website'))

            yield {
                'progress': 0.9,
                'status': f'Enrichment complete: {with_phone} with phone, {with_website} with website',
                'count': len(all_businesses)
            }

        # Stage 3: Apply filters
        if any([min_rating, min_reviews, no_website_only, require_phone]):
            yield {
                'progress': 0.95,
                'status': 'Applying filters...',
                'count': len(all_businesses)
            }

            filtered = exporter.filter_businesses(
                all_businesses,
                min_rating=min_rating,
                min_reviews=min_reviews,
                no_website_only=no_website_only,
                require_phone=require_phone
            )

            yield {
                'progress': 0.98,
                'status': f'Filters applied: {len(filtered)}/{len(all_businesses)} businesses match criteria',
                'count': len(filtered),
                'qualified_count': len(filtered) if no_website_only else sum(1 for b in filtered if not b.get('website'))
            }

            all_businesses = filtered

        # Count qualified leads (businesses without websites)
        qualified_count = sum(1 for b in all_businesses if not b.get('website'))

        # Final results
        yield {
            'progress': 1.0,
            'status': f'Complete! Found {len(all_businesses)} businesses',
            'count': len(all_businesses),
            'qualified_count': qualified_count,
            'businesses': all_businesses
        }

    except Exception as e:
        yield {
            'progress': 0.0,
            'status': f'Error: {str(e)}',
            'count': 0,
            'error': str(e)
        }
        raise


# For testing
if __name__ == '__main__':
    print("Available cities:", get_city_list()[:10], "...")

    print("\nTesting scraper with progress tracking:")
    for update in scrape_with_progress(
        city='dubai',
        query='restaurant',
        max_pages=1,
        enrich_contacts=False
    ):
        print(f"[{update['progress']*100:.0f}%] {update['status']}")
        if 'businesses' in update:
            print(f"Final results: {len(update['businesses'])} businesses")
