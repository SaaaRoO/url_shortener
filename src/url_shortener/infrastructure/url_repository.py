
import random
import string
from url_shortener.models import URLShortener

class URLShortenerRepository:

    @staticmethod
    def create_shortened_url(original_url):
        shortened_url = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        url = URLShortener.objects.create(original_url=original_url, shortened_url=shortened_url)
        return url

    @staticmethod
    def get_url_by_shortened(shortened_url):
        try:
            return URLShortener.objects.get(shortened_url=shortened_url)
        except URLShortener.DoesNotExist:
            return None

    @staticmethod
    def increment_click_count(shortened_url):
        url = URLShortener.objects.get(shortened_url=shortened_url)
        url.click_count += 1
        url.save()
        return url
