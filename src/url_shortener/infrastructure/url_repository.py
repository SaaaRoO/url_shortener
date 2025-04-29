from typing import Optional, Dict, Any
from django.core.cache import cache
from asgiref.sync import sync_to_async
from src.url_shortener.models import URL
from django.db import transaction, DatabaseError

class URLRepository:
    """Repository for URL operations with caching and async support"""
    
    CACHE_TTL = 60 * 60 * 24  # 24 hours cache

    @staticmethod
    async def create_url(original_url: str) -> Optional[URL]:
        try:
            # Generate a unique short code synchronously
            while True:
                short_code = await URL.generate_short_code()  # Call synchronously, no await here
                exists = await sync_to_async(URL.objects.filter(short_code=short_code).exists)()
                if not exists:
                    break

            # Create and save the URL asynchronously with transaction
            url = await URLRepository._create_url_in_db(original_url, short_code)

            # Cache the mapping
            await URLRepository._set_cache(short_code, original_url)

            return url
        except DatabaseError as e:
            return {'error': f"Database error: {str(e)}"}

    @staticmethod
    async def get_by_short_code(short_code: str) -> Optional[URL]:
        # Check cache first
        cached_original_url = await URLRepository._get_cache(short_code)
        if cached_original_url:
            # Return a mock URL object with only original_url (since cache only stores string)
            return URL(original_url=cached_original_url, short_code=short_code)

        # Query the database if not in cache
        url = await URLRepository._get_url_by_short_code(short_code)

        if url:
            await URLRepository._set_cache(short_code, url.original_url)

        return url

    @staticmethod
    async def update_stats(short_code: str) -> None:
        await URLRepository._update_url_stats(short_code)

    @staticmethod
    async def get_stats(short_code: str) -> Optional[Dict[str, Any]]:
        return await URLRepository._get_url_stats(short_code)

    # ------------------------
    # Internal sync wrappers
    # ------------------------

    @staticmethod
    @sync_to_async
    def _create_url_in_db(original_url: str, short_code: str) -> URL:
        with transaction.atomic():
            return URL.objects.create(original_url=original_url, short_code=short_code)

    @staticmethod
    @sync_to_async
    def _get_url_by_short_code(short_code: str) -> Optional[URL]:
        return URL.objects.filter(short_code=short_code, is_active=True).first()

    @staticmethod
    @sync_to_async
    def _update_url_stats(short_code: str) -> None:
        try:
            url = URL.objects.get(short_code=short_code)
            url.update_stats()
        except URL.DoesNotExist:
            pass

    @staticmethod
    @sync_to_async
    def _get_url_stats(short_code: str) -> Optional[Dict[str, Any]]:
        try:
            url = URL.objects.get(short_code=short_code)
            return {
                'short_code': url.short_code,
                'original_url': url.original_url,
                'created_at': url.created_at,
                'last_accessed': url.last_accessed,
                'access_count': url.access_count,
                'is_active': url.is_active
            }
        except URL.DoesNotExist:
            return None

    @staticmethod
    async def _get_cache(short_code: str) -> Optional[str]:
        return await sync_to_async(cache.get)(f"url:{short_code}")

    @staticmethod
    async def _set_cache(short_code: str, original_url: str) -> None:
        await sync_to_async(cache.set)(f"url:{short_code}", original_url, URLRepository.CACHE_TTL)
