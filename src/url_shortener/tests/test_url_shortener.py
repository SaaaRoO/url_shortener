import pytest
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch

from src.url_shortener.events.tasks import update_url_stats

pytestmark = pytest.mark.django_db

# Using DRF's APIClient for testing views
@pytest.fixture
def client():
    from rest_framework.test import APIClient
    return APIClient()

# Test for successful URL shortening
@patch("src.url_shortener.application.url_service.URLService.create_shortened_url")
def test_create_shortened_url_success(mock_create, client):
    mock_create.return_value = {
        "short_code": "abc123",
        "original_url": "https://example.com"
    }

    response = client.post(
        reverse("shorten_url"),
        {"original_url": "https://example.com"},
        format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert "short_code" in response.json()
    mock_create.assert_called_once_with("https://example.com")


# Test for invalid URL format
@patch("src.url_shortener.application.url_service.URLService.create_shortened_url")
def test_create_shortened_url_error(mock_create, client):
    mock_create.return_value = {"error": "Invalid URL format"}

    response = client.post(
        reverse("shorten_url"),
        {"original_url": "invalid-url"},
        format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.json()
    mock_create.assert_called_once_with("invalid-url")


# Test for missing 'original_url' field
def test_create_shortened_url_missing_field(client):
    response = client.post(
        reverse("shorten_url"),
        {},  # Missing the 'original_url' field
        format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.json()


# Test for getting original URL successfully
@pytest.mark.asyncio
async def test_get_original_url_success(mock_service, async_client):
    mock_service.return_value = ("https://example.com", True)
    response = await async_client.get(reverse("redirect_url", args=["abc123"]))
    assert response.status_code == 200
    assert response.data["original_url"] == "https://example.com"


# Test for not found URL during redirection
@pytest.mark.asyncio
async def test_get_original_url_not_found(mock_service, async_client):
    mock_service.return_value = (None, False)

    response = await async_client.get(reverse("redirect_url", args=["invalid"]))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "error" in response.json()


# Test for not found URL stats
@pytest.mark.asyncio
async def test_get_url_stats_not_found(mock_stats, async_client):
    mock_stats.return_value = None

    response = await async_client.get(reverse("url_stats", args=["invalid"]))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "error" in response.json()


# Test for Celery task call
@patch('src.url_shortener.events.tasks.update_url_stats.delay')
def test_update_url_stats(mock_delay, mocker):
    # Mocking the URLService to ensure that the URL is found
    mocker.patch('src.url_shortener.application.url_service.URLService.get_original_url', return_value=("https://example.com", True))

    short_code = 'abc123'
    
    # Call the task
    update_url_stats(short_code)
    
    # Assert that delay was called with the correct argument
    mock_delay.assert_called_once_with(short_code)
