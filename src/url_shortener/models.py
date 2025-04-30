from django.db import models
import random
import string
from django.utils import timezone
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from asgiref.sync import sync_to_async

class URL(models.Model):
    """
    Model to store URL mappings and statistics
    """
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=10, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    access_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['short_code']),
        ]

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"

    def update_stats(self):
        """Update access statistics"""
        self.last_accessed = timezone.now()
        self.access_count += 1
        self.save(update_fields=['last_accessed', 'access_count'])

    @staticmethod
    def generate_short_code(length=6):
        """Generate a random short code and check for collisions"""
        while True:
            short_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
            if not URL.objects.filter(short_code=short_code).exists():
                return short_code

    @staticmethod
    def validate_url(url):
        """Validate a URL"""
        validator = URLValidator()
        try:
            validator(url)
            return True
        except ValidationError:
            return False
