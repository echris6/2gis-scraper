"""
JSON extraction and business data parsing for 2GIS
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class TwoGISParser:
    """Extracts and parses business data from 2GIS HTML pages"""

    @staticmethod
    def extract_initial_state(html: str) -> Optional[Dict]:
        """
        Extract initialState JSON from 2GIS HTML page

        Args:
            html: Raw HTML content from 2GIS page

        Returns:
            Parsed JSON dictionary or None if extraction fails
        """
        try:
            # Pattern 1: var initialState = JSON.parse('...');
            pattern1 = r'var initialState = JSON\.parse\(\'(.+?)\'\);'
            match = re.search(pattern1, html, re.DOTALL)

            if match:
                # Decode escaped JSON string
                json_string = match.group(1)
                # Handle Unicode escape sequences (original working code)
                json_string = json_string.encode().decode('unicode_escape')
                # Parse JSON
                data = json.loads(json_string)
                logger.debug("Successfully extracted initialState using pattern 1")
                return data

            # Pattern 2: window.__INITIAL_STATE__ = {...}
            pattern2 = r'window\.__INITIAL_STATE__\s*=\s*({.+?});'
            match = re.search(pattern2, html, re.DOTALL)

            if match:
                json_string = match.group(1)
                data = json.loads(json_string)
                logger.debug("Successfully extracted initialState using pattern 2")
                return data

            logger.warning("Could not find initialState in HTML")
            return None

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting initialState: {e}")
            return None

    @staticmethod
    def extract_businesses(initial_state: Dict) -> List[Dict]:
        """
        Extract business listings from initialState JSON

        Args:
            initial_state: Parsed initialState dictionary

        Returns:
            List of business dictionaries with extracted data
        """
        businesses = []

        try:
            # Navigate to profiles: data.entity.profile
            profiles = initial_state.get('data', {}).get('entity', {}).get('profile', {})

            if not profiles:
                logger.warning("No business profiles found in initialState")
                return businesses

            logger.info(f"Found {len(profiles)} business profiles")

            for firm_id, profile in profiles.items():
                try:
                    business = TwoGISParser._parse_business_profile(firm_id, profile)
                    businesses.append(business)
                except Exception as e:
                    logger.warning(f"Error parsing business {firm_id}: {e}")
                    continue

            return businesses

        except Exception as e:
            logger.error(f"Error extracting businesses: {e}")
            return businesses

    @staticmethod
    def _parse_business_profile(firm_id: str, profile: Dict) -> Dict:
        """
        Parse individual business profile into structured data

        Args:
            firm_id: Business ID
            profile: Profile dictionary from initialState

        Returns:
            Structured business data dictionary
        """
        # Extract the actual data - profile has {data: {...}, meta: {...}}
        profile_data = profile.get('data', profile)

        # Fix double-encoded UTF-8 text
        def fix_encoding(text):
            if not text or not isinstance(text, str):
                return text
            try:
                # Text is UTF-8 bytes incorrectly decoded as latin-1, re-encode and decode properly
                return text.encode('latin-1').decode('utf-8')
            except (UnicodeDecodeError, UnicodeEncodeError, AttributeError):
                return text

        business = {
            'id': firm_id,
            'name': fix_encoding(profile_data.get('name', '')),
            'address': fix_encoding(TwoGISParser._extract_address(profile_data)),
            'coordinates': TwoGISParser._extract_coordinates(profile_data),
            'phone': TwoGISParser._extract_phone(profile_data),
            'website': TwoGISParser._extract_website(profile_data),
            'rating': TwoGISParser._extract_rating(profile_data),
            'review_count': TwoGISParser._extract_review_count(profile_data),
            'rubric': fix_encoding(TwoGISParser._extract_rubric(profile_data)),
            'schedule': TwoGISParser._extract_schedule(profile_data),
            'attributes': TwoGISParser._extract_attributes(profile_data),
        }

        return business

    @staticmethod
    def _extract_address(profile: Dict) -> str:
        """Extract formatted address"""
        # Try multiple address fields
        address = profile.get('address_name', '')
        if not address:
            address = profile.get('address', {}).get('name', '')
        if not address:
            # Build from components in adm_div
            adm_div = profile.get('adm_div', [])
            components = []
            for div in adm_div:
                if isinstance(div, dict):
                    name = div.get('name')
                    div_type = div.get('type')
                    # Skip country, include city and more specific
                    if name and div_type in ['city', 'district', 'division', 'district_area']:
                        components.append(name)

            # Also try address.components
            addr_obj = profile.get('address', {})
            if isinstance(addr_obj, dict):
                addr_components = addr_obj.get('components', [])
                for comp in addr_components:
                    if isinstance(comp, dict) and comp.get('type') != 'location':
                        comment = comp.get('comment')
                        if comment and comment not in components:
                            components.append(comment)

            address = ', '.join(components) if components else ''

        return address

    @staticmethod
    def _extract_coordinates(profile: Dict) -> Optional[Dict[str, float]]:
        """Extract latitude and longitude"""
        # Check point field first (most common in search results)
        point = profile.get('point', {})
        if isinstance(point, dict) and 'lat' in point and 'lon' in point:
            return {
                'lat': point.get('lat'),
                'lon': point.get('lon')
            }

        # Fallback to geometry field
        geometry = profile.get('geometry', {})
        if isinstance(geometry, dict):
            # Handle different geometry formats
            if 'centroid' in geometry:
                centroid = geometry['centroid']
                if isinstance(centroid, dict):
                    return {
                        'lat': centroid.get('lat'),
                        'lon': centroid.get('lon')
                    }
            elif 'lat' in geometry and 'lon' in geometry:
                return {
                    'lat': geometry.get('lat'),
                    'lon': geometry.get('lon')
                }

        return None

    @staticmethod
    def _extract_phone(profile: Dict) -> Optional[str]:
        """Extract primary phone number"""
        # Note: Phone data is often NOT available on search result pages
        # It's typically only available on the full business profile page

        # Check contacts array
        contacts = profile.get('contacts', [])
        if isinstance(contacts, list):
            for contact in contacts:
                if isinstance(contact, dict) and contact.get('type') == 'phone':
                    return contact.get('text', contact.get('value'))

        # Check direct phone field
        phone = profile.get('phone')
        if phone and isinstance(phone, str):
            return phone

        # Check org.contact_groups
        org = profile.get('org', {})
        if isinstance(org, dict):
            contact_groups = org.get('contact_groups', [])
            if isinstance(contact_groups, list):
                for group in contact_groups:
                    if isinstance(group, dict):
                        group_contacts = group.get('contacts', [])
                        if isinstance(group_contacts, list):
                            for contact in group_contacts:
                                if isinstance(contact, dict) and contact.get('type') == 'phone':
                                    return contact.get('text', contact.get('value'))

        return None

    @staticmethod
    def _extract_website(profile: Dict) -> Optional[str]:
        """Extract website URL"""
        # Note: Website data is often NOT available on search result pages
        # It's typically only available on the full business profile page

        # Blacklist of 2GIS partner/affiliate sites that aren't real business websites
        BLACKLISTED_DOMAINS = [
            'otello.ru',
            '2gis.ru',
            '2gis.ae',
            '2gis.kz',
            '2gis.kg',
            '2gis.cz',
            '2gis.cl',
            '2gis.it',
        ]

        def is_valid_website(url: str) -> bool:
            """Check if URL is a real business website (not 2GIS partner site)"""
            if not url:
                return False
            url_lower = url.lower()
            # Skip blacklisted domains
            for domain in BLACKLISTED_DOMAINS:
                if domain in url_lower:
                    return False
            return True

        # Check contacts array
        contacts = profile.get('contacts', [])
        if isinstance(contacts, list):
            for contact in contacts:
                if isinstance(contact, dict) and contact.get('type') in ['website', 'url']:
                    url = contact.get('text', contact.get('value'))
                    if is_valid_website(url):
                        return url

        # Check direct website field
        website = profile.get('website')
        if website and isinstance(website, str) and is_valid_website(website):
            return website

        # Check org.contact_groups
        org = profile.get('org', {})
        if isinstance(org, dict):
            contact_groups = org.get('contact_groups', [])
            if isinstance(contact_groups, list):
                for group in contact_groups:
                    if isinstance(group, dict):
                        group_contacts = group.get('contacts', [])
                        if isinstance(group_contacts, list):
                            for contact in group_contacts:
                                if isinstance(contact, dict) and contact.get('type') in ['website', 'url']:
                                    url = contact.get('text', contact.get('value'))
                                    if is_valid_website(url):
                                        return url

        # Check links array
        links = profile.get('links', [])
        if isinstance(links, list):
            for link in links:
                if isinstance(link, dict) and link.get('type') == 'website':
                    url = link.get('url')
                    if is_valid_website(url):
                        return url

        return None

    @staticmethod
    def _extract_rating(profile: Dict) -> Optional[float]:
        """Extract rating score"""
        reviews = profile.get('reviews', {})
        rating = reviews.get('general_rating')

        if rating is not None:
            try:
                return float(rating)
            except (ValueError, TypeError):
                return None

        return None

    @staticmethod
    def _extract_review_count(profile: Dict) -> Optional[int]:
        """Extract review count"""
        reviews = profile.get('reviews', {})
        count = reviews.get('general_review_count')

        if count is not None:
            try:
                return int(count)
            except (ValueError, TypeError):
                return None

        return None

    @staticmethod
    def _extract_rubric(profile: Dict) -> List[str]:
        """Extract business categories/rubrics"""
        rubrics = []

        # Note: field is 'rubrics' (plural) not 'rubric'
        rubric_data = profile.get('rubrics', [])
        for rubric in rubric_data:
            if isinstance(rubric, dict):
                name = rubric.get('name')
                if name:
                    rubrics.append(name)
            elif isinstance(rubric, str):
                rubrics.append(rubric)

        # Also check attribute_groups for rubric info
        if not rubrics:
            attr_groups = profile.get('attribute_groups', [])
            for group in attr_groups:
                if isinstance(group, dict) and group.get('is_primary'):
                    name = group.get('name')
                    if name:
                        rubrics.append(name)

        return rubrics

    @staticmethod
    def _extract_schedule(profile: Dict) -> Optional[Dict]:
        """Extract working hours schedule"""
        schedule = profile.get('schedule', {})

        if not schedule:
            return None

        # Check if 24/7
        is_24_7 = schedule.get('is_24_7', False)

        if is_24_7:
            return {'type': '24/7', 'hours': 'Open 24 hours'}

        # Extract working hours by day
        working_hours = {}
        comments = schedule.get('comment', '')

        # Try to get structured schedule
        if 'working_hours' in schedule:
            working_hours = schedule['working_hours']

        return {
            'type': 'regular',
            'hours': working_hours,
            'comments': comments,
            'is_24_7': is_24_7
        }

    @staticmethod
    def _extract_attributes(profile: Dict) -> List[Dict[str, Any]]:
        """Extract business attributes (WiFi, parking, delivery, etc.)"""
        attributes = []

        # Get attribute groups
        attribute_groups = profile.get('attribute_groups', [])

        for group in attribute_groups:
            group_name = group.get('name', 'General')
            items = group.get('attributes', [])

            for item in items:
                if isinstance(item, dict):
                    attributes.append({
                        'category': group_name,
                        'name': item.get('name', ''),
                        'value': item.get('tag', item.get('value', True))
                    })

        # Also check direct attributes field
        direct_attrs = profile.get('attributes', [])
        for attr in direct_attrs:
            if isinstance(attr, dict):
                attributes.append({
                    'category': 'General',
                    'name': attr.get('name', ''),
                    'value': attr.get('tag', attr.get('value', True))
                })

        return attributes

    @staticmethod
    def detect_total_pages(html: str) -> Optional[int]:
        """
        Detect total number of pages from pagination

        Args:
            html: Raw HTML content

        Returns:
            Total page count or None if not detected
        """
        try:
            # Look for pagination data in initialState
            initial_state = TwoGISParser.extract_initial_state(html)
            if not initial_state:
                return None

            # Check search context for total results
            context = initial_state.get('data', {}).get('context', {})
            total_items = context.get('total_items')
            items_per_page = context.get('items_per_page', 20)

            if total_items and items_per_page:
                total_pages = (total_items + items_per_page - 1) // items_per_page
                logger.info(f"Detected {total_pages} total pages ({total_items} items)")
                return total_pages

            # Fallback: parse pagination HTML
            pagination_pattern = r'/page/(\d+)'
            page_numbers = re.findall(pagination_pattern, html)

            if page_numbers:
                max_page = max(int(p) for p in page_numbers)
                logger.info(f"Detected {max_page} pages from pagination links")
                return max_page

            return None

        except Exception as e:
            logger.warning(f"Error detecting total pages: {e}")
            return None
