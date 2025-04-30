from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from src.url_shortener.events.tasks import update_url_stats
from src.url_shortener.models import URL

class URLShortenerViewTests(APITestCase):
    
    @patch("src.url_shortener.interfaces.views.URLService.create_shortened_url")
    def test_create_shortened_url_success(self, mock_create):
        mock_create.return_value = {
            "short_code": "abc123",
            "original_url": "https://example.com"
        }

        response = self.client.post(
            reverse("shorten_url"),  
            {"original_url": "https://example.com"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("short_code", response.data)

    @patch("src.url_shortener.interfaces.views.URLService.create_shortened_url")
    def test_create_shortened_url_error(self, mock_create):
        mock_create.return_value = {"error": "Invalid URL format"}

        response = self.client.post(
            reverse("shorten_url"),
            {"original_url": "invalid-url"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_create_shortened_url_missing_field(self):
        response = self.client.post(
            reverse("shorten_url"),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    @patch("src.url_shortener.interfaces.views.URLService.get_original_url")
    def test_get_original_url_success(self, mock_get_original):
        mock_get_original.return_value = ("https://example.com", True)

        response = self.client.get(
            reverse("redirect_url", args=["abc123"])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["original_url"], "https://example.com")

    @patch("src.url_shortener.interfaces.views.URLService.get_original_url")
    def test_get_original_url_not_found(self, mock_get_original):
        mock_get_original.return_value = (None, False)

        response = self.client.get(
            reverse("redirect_url", args=["invalid"])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    @patch("src.url_shortener.interfaces.views.URLService.get_url_stats")
    def test_get_url_stats_success(self, mock_stats):
        mock_stats.return_value = {
            "original_url": "https://example.com",
            "created_at": "2025-04-29T12:00:00Z",
            "clicks": 42
        }

        response = self.client.get(
            reverse("url_stats", args=["abc123"])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["clicks"], 42)

    @patch("src.url_shortener.interfaces.views.URLService.get_url_stats")
    def test_get_url_stats_not_found(self, mock_stats):
        mock_stats.return_value = None

        response = self.client.get(
            reverse("url_stats", args=["invalid"])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)


    @pytest.mark.django_db
    def test_update_url_stats_task_updates_clicks(self):
        url = URL.objects.create(
            original_url='https://example.com',
            short_code='abc123',
           access_count=0
        )

        update_url_stats('abc123')

        url.refresh_from_db()
        assert url.access_count == 1