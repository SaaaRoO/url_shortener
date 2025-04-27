# tests/test_url_shortener.py
from rest_framework.test import APITestCase
from rest_framework import status

class URLShortenerTestCase(APITestCase):

    def test_shorten_url(self):
        response = self.client.post('/api/shorten', {'original_url': 'https://example.com'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('shortened_url', response.data)

    def test_get_original_url(self):
        shortened_url = 'abc123'  
        response = self.client.get(f'/api/{shortened_url}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('original_url', response.data)

    def test_get_url_stats(self):
        shortened_url = 'abc123'  
        response = self.client.get(f'/api/stats/{shortened_url}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('click_count', response.data)
