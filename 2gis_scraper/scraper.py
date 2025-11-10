"""
Core scraping engine for 2GIS
"""

import time
import random
import logging
import requests
from typing import List, Dict, Optional
from urllib.parse import quote

from parser import TwoGISParser
from cache_manager import CacheManager
import config

logger = logging.getLogger(__name__)


class TwoGISScraper:
    """Main scraper class for 2GIS business listings"""

    def __init__(
        self,
        cache_enabled: bool = True,
        delay: float = None,
        timeout: int = None,
        max_retries: int = None
    ):
        """
        Initialize 2GIS scraper

        Args:
            cache_enabled: Enable HTML response caching
            delay: Delay between requests in seconds (default from config)
            timeout: Request timeout in seconds (default from config)
            max_retries: Maximum retry attempts (default from config)
        """
        self.cache = CacheManager(
            cache_dir=config.DEFAULT_CACHE_DIR,
            enabled=cache_enabled
        )
        self.delay = delay if delay is not None else config.DEFAULT_DELAY
        self.timeout = timeout if timeout is not None else config.DEFAULT_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else config.MAX_RETRIES
        self.parser = TwoGISParser()
        self.session = self._create_session()

        logger.info(f"Scraper initialized (delay={self.delay}s, cache={cache_enabled})")

    def _create_session(self) -> requests.Session:
        """Create and configure requests session"""
        session = requests.Session()
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        return session

    def _get_user_agent(self) -> str:
        """Get random User-Agent from pool"""
        return random.choice(config.USER_AGENTS)

    def _get_tld(self, city: str) -> str:
        """
        Get TLD for city

        Args:
            city: City name (lowercase with underscores)

        Returns:
            TLD string (e.g., 'ru', 'ae', 'kz')
        """
        tld = config.CITY_TLD_MAP.get(city.lower())
        if not tld:
            logger.warning(f"Unknown city '{city}', defaulting to .ru")
            return 'ru'
        return tld

    def _build_url(self, city: str, query: str, page: int = 1) -> str:
        """
        Build 2GIS search URL

        Args:
            city: City name
            query: Search query
            page: Page number (1-indexed)

        Returns:
            Full URL for search
        """
        tld = self._get_tld(city)
        query_encoded = quote(query)
        city_encoded = quote(city.lower().replace('_', ' '))

        if page == 1:
            url = f'https://2gis.{tld}/{city_encoded}/search/{query_encoded}'
        else:
            url = f'https://2gis.{tld}/{city_encoded}/search/{query_encoded}/page/{page}'

        return url

    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML page with caching and retries

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if failed
        """
        # Check cache first
        cached_html = self.cache.get(url)
        if cached_html:
            return cached_html

        # Fetch from web
        for attempt in range(self.max_retries):
            try:
                headers = {'User-Agent': self._get_user_agent()}
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()

                # Explicitly set encoding to UTF-8 for Russian content
                response.encoding = 'utf-8'
                html = response.text

                # Cache the response
                self.cache.set(url, html)

                logger.info(f"Fetched: {url} ({len(html)} bytes)")
                return html

            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue

        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None

    def _rate_limit(self):
        """Apply rate limiting delay"""
        if self.delay > 0:
            # Add small random variation to avoid pattern detection
            jitter = random.uniform(-0.5, 0.5)
            sleep_time = max(0, self.delay + jitter)
            logger.debug(f"Sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

    def scrape_page(self, city: str, query: str, page: int = 1) -> List[Dict]:
        """
        Scrape single page of results

        Args:
            city: City name
            query: Search query
            page: Page number (1-indexed)

        Returns:
            List of business dictionaries
        """
        url = self._build_url(city, query, page)
        logger.info(f"Scraping page {page}: {query} in {city}")

        # Fetch HTML
        html = self._fetch_page(url)
        if not html:
            logger.error(f"Failed to fetch page {page}")
            return []

        # Extract initialState
        initial_state = self.parser.extract_initial_state(html)
        if not initial_state:
            logger.error(f"Failed to extract initialState from page {page}")
            return []

        # Extract businesses
        businesses = self.parser.extract_businesses(initial_state)
        logger.info(f"Extracted {len(businesses)} businesses from page {page}")

        return businesses

    def scrape(
        self,
        city: str,
        query: str,
        max_pages: Optional[int] = None,
        auto_detect_pages: bool = True
    ) -> List[Dict]:
        """
        Scrape multiple pages of results

        Args:
            city: City name
            query: Search query
            max_pages: Maximum number of pages to scrape (None for all)
            auto_detect_pages: Auto-detect total pages from first page

        Returns:
            List of all business dictionaries across pages
        """
        all_businesses = []
        total_pages = max_pages

        # Fetch first page
        logger.info(f"Starting scrape: '{query}' in {city}")
        page1_businesses = self.scrape_page(city, query, page=1)
        all_businesses.extend(page1_businesses)

        # Auto-detect total pages if requested
        if auto_detect_pages and not max_pages:
            url = self._build_url(city, query, page=1)
            html = self.cache.get(url)  # Should be cached from scrape_page
            if html:
                detected_pages = self.parser.detect_total_pages(html)
                if detected_pages:
                    total_pages = detected_pages
                    logger.info(f"Auto-detected {total_pages} total pages")

        # If no pages detected and no max_pages set, default to 1 page only
        if total_pages is None:
            logger.info("No pagination detected, scraping first page only")
            return all_businesses

        # Scrape remaining pages
        for page in range(2, total_pages + 1):
            self._rate_limit()  # Rate limiting between pages

            businesses = self.scrape_page(city, query, page)

            # Stop if no results found (reached end)
            if not businesses:
                logger.info(f"No results on page {page}, stopping")
                break

            all_businesses.extend(businesses)

        logger.info(f"Scraping complete: {len(all_businesses)} total businesses")
        return all_businesses

    def scrape_multiple_queries(
        self,
        city: str,
        queries: List[str],
        max_pages_per_query: Optional[int] = None
    ) -> Dict[str, List[Dict]]:
        """
        Scrape multiple queries for the same city

        Args:
            city: City name
            queries: List of search queries
            max_pages_per_query: Max pages per query

        Returns:
            Dictionary mapping query to list of businesses
        """
        results = {}

        for i, query in enumerate(queries):
            logger.info(f"Processing query {i + 1}/{len(queries)}: {query}")

            businesses = self.scrape(
                city=city,
                query=query,
                max_pages=max_pages_per_query
            )

            results[query] = businesses

            # Rate limit between queries
            if i < len(queries) - 1:
                self._rate_limit()

        return results

    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        return self.cache.get_stats()

    def clear_cache(self) -> int:
        """Clear cache and return number of files deleted"""
        return self.cache.clear()
