from typing import Dict, Any, Optional, Tuple
from django.conf import settings
from src.url_shortener.infrastructure.url_repository import URLRepository
from src.url_shortener.models import URL

class URLService:
    """Service class for URL shortening business logic"""

    @staticmethod
    async def create_shortened_url(original_url: str) -> Dict[str, Any]:
        # Validate URL
        if not URL.validate_url(original_url):
            return {'error': 'Invalid URL provided'}

        # Create URL in database
        url = await URLRepository.create_url(original_url)

        if not url or isinstance(url, dict) and "error" in url:
            return {'error': 'Failed to create short URL'}

        # Construct the full shortened URL
        shortened_url = f"{settings.BASE_URL}/{url.short_code}"

        return {
            'original_url': url.original_url,
            'shortened_url': shortened_url,
            'short_code': url.short_code
        }

    @staticmethod
    async def get_original_url(short_code: str) -> Tuple[Optional[str], bool]:
        url = await URLRepository.get_by_short_code(short_code)

        if not url:
            return None, False

        # Update stats asynchronously
        await URLRepository.update_stats(short_code)

        return url.original_url, True

    @staticmethod
    async def get_url_stats(short_code: str) -> Optional[Dict[str, Any]]:
        stats = await URLRepository.get_stats(short_code)

        if not stats:
            return None

        return {
            'short_code': stats['short_code'],
            'original_url': stats['original_url'],
            'shortened_url': f"{settings.BASE_URL}/{stats['short_code']}",
            'created_at': stats['created_at'],
            'last_accessed': stats['last_accessed'],
            'access_count': stats['access_count'],
            'is_active': stats['is_active']
        }
