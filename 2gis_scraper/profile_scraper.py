"""
Profile page scraper for enriching business data with contact information
"""

import asyncio
import logging
import re
import json
import random
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page

from parser import TwoGISParser
import config

logger = logging.getLogger(__name__)


class ProfileEnricher:
    """Enriches business data by visiting individual profile pages"""

    def __init__(self, headless: bool = True, delay: float = None):
        """
        Initialize profile enricher

        Args:
            headless: Run browser in headless mode
            delay: Delay between requests (default from config)
        """
        self.headless = headless
        self.delay = delay if delay is not None else config.DEFAULT_DELAY
        self.parser = TwoGISParser()
        self.browser: Optional[Browser] = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def start(self):
        """Start browser"""
        playwright = await async_playwright().start()

        # Launch with anti-detection settings
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )

        logger.info("Browser started")

    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")

    def _build_profile_url(self, city: str, business_id: str, tld: str = None) -> str:
        """
        Build URL for business profile page

        Args:
            city: City name
            business_id: Business ID from search results
            tld: TLD override (auto-detected if not provided)

        Returns:
            Full URL to profile page
        """
        if not tld:
            tld = config.CITY_TLD_MAP.get(city.lower(), 'ru')

        # URL pattern: https://2gis.{tld}/{city}/firm/{business_id}
        city_encoded = city.lower().replace('_', ' ')
        return f'https://2gis.{tld}/{city_encoded}/firm/{business_id}'

    async def _fetch_profile_page(self, page: Page, url: str, max_retries: int = 2) -> Optional[str]:
        """
        Fetch individual profile page with retry logic

        Args:
            page: Playwright page instance
            url: Profile URL
            max_retries: Maximum number of retry attempts

        Returns:
            HTML content or None if failed
        """
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    # Exponential backoff: wait longer between retries
                    wait_time = 5 * (2 ** (attempt - 1))
                    logger.info(f"Retry {attempt}/{max_retries} for {url} after {wait_time}s...")
                    await asyncio.sleep(wait_time)

                logger.debug(f"Fetching profile: {url}")

                # Navigate to page with longer timeout (60 seconds)
                response = await page.goto(url, wait_until='load', timeout=60000)

                if not response or response.status != 200:
                    logger.warning(f"Failed to load profile: {url} (status: {response.status if response else 'None'})")
                    continue  # Retry

                # Wait for JavaScript to execute and render the initialState
                # The page uses client-side rendering, so we need to wait
                await page.wait_for_timeout(5000)  # Give it 5 seconds to render

                # Get HTML after JavaScript execution
                html = await page.content()
                logger.debug(f"Fetched profile: {url} ({len(html)} bytes)")

                return html

            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching {url} (attempt {attempt + 1}/{max_retries + 1})")
                if attempt == max_retries:
                    logger.error(f"Max retries reached for {url}")
                    return None
            except Exception as e:
                logger.error(f"Error fetching profile {url}: {e}")
                if attempt == max_retries:
                    return None

        return None

    def _extract_contact_info(self, html: str) -> Dict[str, Optional[str]]:
        """
        Extract contact information from profile page HTML

        Args:
            html: HTML content of profile page

        Returns:
            Dictionary with phone and website
        """
        from bs4 import BeautifulSoup

        contact_info = {
            'phone': None,
            'website': None
        }

        try:
            # Method 1: Try JSON extraction first
            initial_state = self.parser.extract_initial_state(html)

            if initial_state:
                logger.debug("Found initial state JSON in HTML")
                # Navigate to profile data
                profiles = initial_state.get('data', {}).get('entity', {}).get('profile', {})

                if not profiles:
                    # Try alternative path for profile pages
                    profile_data = initial_state.get('data', {}).get('profile', {})
                    if profile_data:
                        logger.debug("Using alternative profile path")
                        contact_info['phone'] = self.parser._extract_phone(profile_data)
                        contact_info['website'] = self.parser._extract_website(profile_data)
                        if contact_info['phone'] or contact_info['website']:
                            return contact_info

                # Get first (and usually only) profile
                if profiles:
                    profile_id = list(profiles.keys())[0]
                    profile = profiles[profile_id]
                    profile_data = profile.get('data', profile)

                    logger.debug(f"Extracting from profile {profile_id}")
                    contact_info['phone'] = self.parser._extract_phone(profile_data)
                    contact_info['website'] = self.parser._extract_website(profile_data)
                    if contact_info['phone'] or contact_info['website']:
                        return contact_info
            else:
                logger.debug("No initial state JSON found, will try HTML parsing")

            # Method 2: Parse rendered HTML directly (fallback)
            soup = BeautifulSoup(html, 'html.parser')

            # Find phone numbers in links or text
            phone_patterns = [
                r'\+?\d[\d\s\-\(\)]{7,}',  # Phone number pattern
            ]

            # Look for phone links
            phone_links = soup.find_all('a', href=re.compile(r'tel:'))
            if phone_links:
                phone = phone_links[0].get('href', '').replace('tel:', '').strip()
                if phone:
                    contact_info['phone'] = phone
                    logger.debug(f"Found phone via tel: link: {phone}")

            # Look for website links
            # Find links that are external (not 2gis.* or partner sites)
            SKIP_DOMAINS = ['2gis.', 'javascript:', '#', 'tel:', 'mailto:', 'otello.ru']

            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                # Skip internal 2gis links and partner sites
                if href and not any(x in href for x in SKIP_DOMAINS):
                    if href.startswith('http'):
                        contact_info['website'] = href
                        logger.debug(f"Found website link: {href}")
                        break

        except Exception as e:
            logger.error(f"Error extracting contact info: {e}")

        return contact_info

    async def enrich_business(
        self,
        business: Dict,
        city: str,
        tld: str = None
    ) -> Dict:
        """
        Enrich single business with contact information

        Args:
            business: Business dictionary from search results
            city: City name
            tld: TLD override

        Returns:
            Business dictionary with updated phone/website
        """
        business_id = business.get('id')

        if not business_id:
            logger.warning("Business has no ID, cannot enrich")
            return business

        # Build profile URL
        url = self._build_profile_url(city, business_id, tld)

        # Create new page for this request with proper headers
        page = await self.browser.new_page(
            user_agent=random.choice(config.USER_AGENTS) if hasattr(config, 'USER_AGENTS') else 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        # Set extra headers
        await page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })

        try:
            # Fetch profile page
            html = await self._fetch_profile_page(page, url)

            if not html:
                logger.warning(f"Failed to fetch profile for business {business_id}")
                return business

            # Extract contact info
            contact_info = self._extract_contact_info(html)

            # Update business dictionary
            business_name = business.get('name', business_id)

            if contact_info['phone']:
                business['phone'] = contact_info['phone']
                logger.info(f"✓ {business_name}: Found phone {contact_info['phone']}")
            else:
                logger.info(f"✗ {business_name}: No phone found")

            if contact_info['website']:
                business['website'] = contact_info['website']
                logger.info(f"✓ {business_name}: Found website {contact_info['website']}")
            else:
                logger.info(f"✗ {business_name}: No website found")

            # Rate limiting with random jitter (±25% to look more human)
            jitter = random.uniform(0.75, 1.25)
            await asyncio.sleep(self.delay * jitter)

        finally:
            await page.close()

        return business

    async def enrich_businesses(
        self,
        businesses: List[Dict],
        city: str,
        tld: str = None
    ) -> List[Dict]:
        """
        Enrich multiple businesses with contact information

        Args:
            businesses: List of business dictionaries
            city: City name
            tld: TLD override

        Returns:
            List of enriched businesses
        """
        logger.info(f"Starting enrichment for {len(businesses)} businesses...")

        enriched = []
        for i, business in enumerate(businesses):
            logger.info(f"[{i+1}/{len(businesses)}] Processing: {business.get('name', business.get('id'))}")

            enriched_business = await self.enrich_business(business, city, tld)
            enriched.append(enriched_business)

        # Count results
        with_phone = sum(1 for b in enriched if b.get('phone'))
        with_website = sum(1 for b in enriched if b.get('website'))
        without_website = sum(1 for b in enriched if not b.get('website'))

        logger.info(f"Enrichment complete: {with_phone} with phone, {with_website} with website, {without_website} without website")

        return enriched


async def enrich_businesses_async(
    businesses: List[Dict],
    city: str,
    headless: bool = True,
    delay: float = None
) -> List[Dict]:
    """
    Convenience function to enrich businesses

    Args:
        businesses: List of business dictionaries
        city: City name
        headless: Run browser in headless mode
        delay: Delay between requests

    Returns:
        List of enriched businesses
    """
    async with ProfileEnricher(headless=headless, delay=delay) as enricher:
        return await enricher.enrich_businesses(businesses, city)


def enrich_businesses(
    businesses: List[Dict],
    city: str,
    headless: bool = True,
    delay: float = None
) -> List[Dict]:
    """
    Synchronous wrapper for enriching businesses

    Args:
        businesses: List of business dictionaries
        city: City name
        headless: Run browser in headless mode
        delay: Delay between requests

    Returns:
        List of enriched businesses
    """
    return asyncio.run(enrich_businesses_async(businesses, city, headless, delay))
