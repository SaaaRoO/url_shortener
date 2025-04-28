import pytest
from rest_framework import status
from django.test import Client
from url_shortener.models import URLShortener  

@pytest.mark.django_db
@pytest.mark.asyncio
class TestURLShortener:

    # Test for creating a shortened URL
    async def test_shorten_url(self, async_client):
        response = await async_client.post('/api/shorten/', {'original_url': 'https://example.com'})
        assert response.status_code == status.HTTP_201_CREATED
        assert 'shortened_url' in response.json()

    # Test for retrieving the original URL
    async def test_get_original_url(self, async_client):
        shortened_url = 'abc123'
        original_url = 'https://example.com'

        # Save the shortened URL in the database (for testing purposes)
        URLShortener.objects.create(shortened_url=shortened_url, original_url=original_url, click_count=0)

        response = await async_client.get(f'/api/{shortened_url}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get('original_url') == original_url

    # Test for retrieving URL stats (click count)
    async def test_get_url_stats(self, async_client):
        shortened_url = 'abc123'
        original_url = 'https://example.com'

        # Save the shortened URL with initial click count as 0
        URLShortener.objects.create(shortened_url=shortened_url, original_url=original_url, click_count=0)

        response = await async_client.get(f'/api/stats/{shortened_url}/')
        assert response.status_code == status.HTTP_200_OK
        assert 'click_count' in response.json()

    # Test when the shortened URL does not exist
    async def test_get_non_existent_url(self, async_client):
        shortened_url = 'nonexistent123'

        response = await async_client.get(f'/api/{shortened_url}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json().get('error') == 'Not found'

    # Test for invalid URL input in shortening
    async def test_invalid_shorten_url(self, async_client):
        response = await async_client.post('/api/shorten/', {'original_url': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json().get('error') == 'URL is required'
