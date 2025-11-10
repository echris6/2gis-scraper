"""
Configuration settings for 2GIS scraper
"""

# City to TLD mapping for 2GIS regions
CITY_TLD_MAP = {
    # Russia
    'moscow': 'ru',
    'spb': 'ru',
    'petersburg': 'ru',
    'saint_petersburg': 'ru',
    'novosibirsk': 'ru',
    'ekaterinburg': 'ru',
    'kazan': 'ru',
    'nizhny_novgorod': 'ru',
    'chelyabinsk': 'ru',
    'samara': 'ru',
    'omsk': 'ru',
    'rostov': 'ru',
    'ufa': 'ru',
    'krasnoyarsk': 'ru',
    'voronezh': 'ru',
    'perm': 'ru',
    'volgograd': 'ru',

    # UAE
    'dubai': 'ae',
    'abu_dhabi': 'ae',
    'sharjah': 'ae',
    'ajman': 'ae',

    # Kazakhstan
    'almaty': 'kz',
    'astana': 'kz',
    'nur_sultan': 'kz',
    'shymkent': 'kz',
    'karaganda': 'kz',

    # Kyrgyzstan
    'bishkek': 'kg',
    'osh': 'kg',

    # Chile
    'santiago': 'cl',

    # Cyprus
    'nicosia': 'com.cy',
    'limassol': 'com.cy',

    # Czech Republic
    'prague': 'cz',

    # Italy
    'milan': 'it',
    'rome': 'it',
}

# User-Agent rotation pool
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

# Scraping settings
DEFAULT_DELAY = 8  # Seconds between requests (increased to avoid rate limiting)
DEFAULT_TIMEOUT = 60  # Request timeout in seconds (increased for reliability)
MAX_RETRIES = 3  # Maximum retry attempts for failed requests
CACHE_ENABLED = True  # Enable HTML response caching

# Output settings
DEFAULT_OUTPUT_DIR = 'output'
DEFAULT_CACHE_DIR = 'cache/search'

# Data extraction settings
EXTRACT_PHOTOS = False  # Set to True to extract photo URLs
EXTRACT_REVIEWS = False  # Set to True to extract individual reviews
EXTRACT_ATTRIBUTES = True  # Extract business attributes (WiFi, parking, etc.)
EXTRACT_SCHEDULE = True  # Extract working hours

# Lead filtering settings
FILTER_NO_WEBSITE = False  # Only return businesses without websites
FILTER_MIN_RATING = None  # Minimum rating (e.g., 4.0) or None
FILTER_MIN_REVIEWS = None  # Minimum review count or None
FILTER_REQUIRE_PHONE = False  # Only return businesses with phone numbers

# Logging settings
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_FILE = '2gis_scraper.log'
