from celery import shared_task

from url_shortener.infrastructure.url_repository import URLShortenerRepository

@shared_task
def update_click_count(shortened_url):
    URLShortenerRepository.increment_click_count(shortened_url)
