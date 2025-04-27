
from url_shortener.infrastructure.url_repository import URLShortenerRepository
from url_shortener.events.tasks import update_click_count
from django.core.cache import cache

class URLShortenerService:
    
    @staticmethod
    async def shorten_url(original_url):
        cached_url = cache.get(original_url)
        if cached_url:
            return cached_url

        url = URLShortenerRepository.create_shortened_url(original_url)
        cache.set(original_url, url.shortened_url, timeout=60*15)  # Cache for 15 minutes
        return url.shortened_url

    @staticmethod
    async def get_original_url(shortened_url):
        url = URLShortenerRepository.get_url_by_shortened(shortened_url)
        if url:
            return url.original_url
        return None

    @staticmethod
    async def update_statistics(shortened_url):
        update_click_count.apply_async(args=[shortened_url])
