from celery import shared_task
import logging
from django.utils import timezone
from django.db import transaction
from src.url_shortener.models import URL

logger = logging.getLogger(__name__)


@shared_task
def update_url_stats(short_code):
    """
    Update URL access statistics in the background.
    """
    try:
        # Using transaction.atomic() to ensure atomicity in database operations
        with transaction.atomic():
            url = URL.objects.get(short_code=short_code)
            url.last_accessed = timezone.now()
            url.access_count += 1
            url.save(update_fields=['last_accessed', 'access_count'])
            logger.info(f"Updated stats for URL with short code: {short_code}")
            return True
    except URL.DoesNotExist:
        logger.error(f"Failed to update stats: URL with short code {short_code} not found")
        return False
    except Exception as e:
        logger.exception(f"Error updating URL stats: {str(e)}")
        return False

@shared_task
def clean_expired_urls(days=30):
    """
    Mark URLs that haven't been accessed for a specific number of days as inactive.
    """
    expiration_date = timezone.now() - timezone.timedelta(days=days)
    
    # Mark URLs as inactive if they haven't been accessed for the specified period
    expired_count = URL.objects.filter(
        last_accessed__lt=expiration_date,
        is_active=True
    ).update(is_active=False)
    
    logger.info(f"Marked {expired_count} URLs as inactive due to inactivity")
    return expired_count
