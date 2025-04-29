import pytest
from django.urls import reverse
from rest_framework import status
from unittest import mock
import uuid
from datetime import timedelta
from django.utils import timezone

from src.url_shortener.models import URL
from src.url_shortener.events.tasks import update_url_stats, clean_expired_urls
from asgiref.sync import sync_to_async


@pytest.mark.asyncio
@pytest.mark.django_db
class TestURLShortener:
    """
    Test cases for URL shortener API and tasks
    """

    @pytest.fixture
    async def sample_url(self):
        """Create a sample URL for testing"""
        short_code = str(uuid.uuid4())[:8]
        url = URL(
            original_url="https://example.com",
            short_code=short_code,
            last_accessed=timezone.now(),
            is_active=True
        )
        await sync_to_async(url.save)()  # Ensuring async-safe save
        return url

    async def test_shorten_url(self, async_client):
        url = "https://www.example.com/very/long/url"

        response = await async_client.post(
            reverse('shorten_url'),  # Check your URL name here
            {'original_url': url},
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert 'original_url' in response.data
        assert 'shortened_url' in response.data
        assert response.data['original_url'] == url

        short_code = response.data['short_code']
        url_obj = await URL.objects.aget(short_code=short_code)
        assert url_obj.original_url == url

    async def test_invalid_url(self, async_client):
        response = await async_client.post(
            reverse('shorten_url'),
            {'original_url': 'invalid_url'},
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_redirect_url(self, async_client, sample_url):
        with mock.patch('src.url_shortener.events.tasks.update_url_stats.delay') as mock_task:
            response = await async_client.get(
                reverse('redirect_url', kwargs={'short_code': sample_url.short_code})
            )
            mock_task.assert_called_once_with(sample_url.short_code)
            assert response.status_code == status.HTTP_302_FOUND
            assert response.url == sample_url.original_url

    async def test_nonexistent_redirect(self, async_client):
        response = await async_client.get(
            reverse('redirect_url', kwargs={'short_code': 'nonexistent'})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_url_stats(self, async_client, sample_url):
        response = await async_client.get(
            reverse('url_stats', kwargs={'short_code': sample_url.short_code})
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['short_code'] == sample_url.short_code
        assert 'access_count' in response.data
        assert 'created_at' in response.data

    async def test_rate_limit_exceeded(self, async_client):
        url = "https://example.com"
        for _ in range(10):
            await async_client.post(reverse('shorten_url'), {'original_url': url}, format='json')

        response = await async_client.post(reverse('shorten_url'), {'original_url': url}, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    async def test_url_stats_cache(self, async_client, sample_url):
        first = await async_client.get(
            reverse('url_stats', kwargs={'short_code': sample_url.short_code})
        )
        assert first.status_code == 200

        sample_url.access_count += 100
        await sync_to_async(sample_url.save)()  # Ensure saving asynchronously

        cached = await async_client.get(
            reverse('url_stats', kwargs={'short_code': sample_url.short_code})
        )
        assert cached.data['access_count'] == first.data['access_count']


@pytest.mark.django_db
class TestCeleryTasks:
    """
    Test the Celery background tasks
    """

    def test_update_url_stats_success(self):
        url = URL.objects.create(
            original_url='https://test.com',
            short_code='test123',
            last_accessed=timezone.now() - timedelta(days=1),
            access_count=0
        )
        result = update_url_stats(url.short_code)
        url.refresh_from_db()
        assert result is True
        assert url.access_count == 1

    def test_update_url_stats_not_found(self):
        result = update_url_stats('nonexistent')
        assert result is False

    def test_clean_expired_urls(self):
        URL.objects.create(
            original_url='https://expired.com',
            short_code='expired1',
            last_accessed=timezone.now() - timedelta(days=31),
            is_active=True
        )
        URL.objects.create(
            original_url='https://fresh.com',
            short_code='fresh1',
            last_accessed=timezone.now(),
            is_active=True
        )

        count = clean_expired_urls(days=30)
        assert count == 1

        expired = URL.objects.get(short_code='expired1')
        assert expired.is_active is False
