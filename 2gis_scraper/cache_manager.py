"""
Cache management for 2GIS scraper to avoid redundant requests
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages HTML response caching for the scraper"""

    def __init__(self, cache_dir: str = 'cache/search', enabled: bool = True):
        """
        Initialize cache manager

        Args:
            cache_dir: Directory to store cached files
            enabled: Whether caching is enabled
        """
        self.cache_dir = Path(cache_dir)
        self.enabled = enabled

        if self.enabled:
            # Create cache directory if it doesn't exist
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cache manager initialized: {self.cache_dir}")

    def _generate_cache_key(self, url: str) -> str:
        """
        Generate cache file key from URL

        Args:
            url: Request URL

        Returns:
            MD5 hash of URL as cache key
        """
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def _get_cache_path(self, url: str) -> Path:
        """
        Get cache file path for URL

        Args:
            url: Request URL

        Returns:
            Path to cache file
        """
        cache_key = self._generate_cache_key(url)
        return self.cache_dir / f"{cache_key}.html"

    def get(self, url: str) -> Optional[str]:
        """
        Retrieve cached HTML for URL

        Args:
            url: Request URL

        Returns:
            Cached HTML content or None if not found/disabled
        """
        if not self.enabled:
            return None

        cache_path = self._get_cache_path(url)

        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    html = f.read()
                logger.debug(f"Cache HIT: {url}")
                return html
            except Exception as e:
                logger.warning(f"Error reading cache for {url}: {e}")
                return None
        else:
            logger.debug(f"Cache MISS: {url}")
            return None

    def set(self, url: str, html: str) -> bool:
        """
        Store HTML in cache

        Args:
            url: Request URL
            html: HTML content to cache

        Returns:
            True if cached successfully, False otherwise
        """
        if not self.enabled:
            return False

        cache_path = self._get_cache_path(url)

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.debug(f"Cached: {url}")
            return True
        except Exception as e:
            logger.warning(f"Error caching {url}: {e}")
            return False

    def clear(self) -> int:
        """
        Clear all cached files

        Returns:
            Number of files deleted
        """
        if not self.enabled or not self.cache_dir.exists():
            return 0

        deleted = 0
        try:
            for cache_file in self.cache_dir.glob('*.html'):
                cache_file.unlink()
                deleted += 1
            logger.info(f"Cleared {deleted} cached files")
            return deleted
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return deleted

    def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        if not self.enabled or not self.cache_dir.exists():
            return {
                'enabled': False,
                'total_files': 0,
                'total_size_mb': 0
            }

        cached_files = list(self.cache_dir.glob('*.html'))
        total_size = sum(f.stat().st_size for f in cached_files)

        return {
            'enabled': True,
            'total_files': len(cached_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir)
        }
