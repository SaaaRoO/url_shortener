from url_shortener.infrastructure.url_repository import URLShortenerRepository
from url_shortener.events.tasks import update_click_count
from django.core.cache import cache
from asgiref.sync import sync_to_async

class URLShortenerService:
    
    @staticmethod
    async def shorten_url(original_url):
        # Check if the shortened URL is cached
        cached_url = cache.get(original_url)
        if cached_url:
            return cached_url

        # Create a new shortened URL
        url = await URLShortenerRepository.create_shortened_url(original_url)
        # Cache the shortened URL for 15 minutes
        cache.set(original_url, url.shortened_url, timeout=60*15)  
        return url.shortened_url

    @staticmethod
    async def get_original_url(shortened_url):
        # Retrieve the original URL from the database
        url = await URLShortenerRepository.get_url_by_shortened(shortened_url)
        if url:
            return url.original_url
        return None

    @staticmethod
    async def update_statistics(shortened_url):
        # Trigger the Celery task to update click count
        await sync_to_async(update_click_count.apply_async)(args=[shortened_url])
