import random
import string
from url_shortener.models import URLShortener
from asgiref.sync import sync_to_async

class URLShortenerRepository:

    @staticmethod
    @sync_to_async
    def create_shortened_url(original_url):
        shortened_url = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        url = URLShortener.objects.create(original_url=original_url, shortened_url=shortened_url)
        return url

    @staticmethod
    @sync_to_async
    def get_url_by_shortened(shortened_url):
        try:
            return URLShortener.objects.get(shortened_url=shortened_url)
        except URLShortener.DoesNotExist:
            return None

    @staticmethod
    @sync_to_async
    def increment_click_count(shortened_url):
        try:
            url = URLShortener.objects.get(shortened_url=shortened_url)
            url.click_count += 1
            url.save()
            return url
        except URLShortener.DoesNotExist:
            return None
