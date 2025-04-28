import random
import string
from django.db import models

def generate_shortened_url(length=10):
    """
    Generates a random shortened URL consisting of letters and digits.
    Ensures uniqueness by checking the database for existing shortened URLs.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class URLShortener(models.Model):
    original_url = models.URLField()
    shortened_url = models.CharField(max_length=10, unique=True)
    click_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['original_url']),
            models.Index(fields=['shortened_url']),
        ]
    
    def save(self, *args, **kwargs):
        """
        Override the save method to generate a unique shortened URL.
        This will be used to ensure that the shortened URL is unique before saving the object.
        """
        if not self.shortened_url:
            self.shortened_url = generate_shortened_url()  # Generate a shortened URL
            # Ensure the shortened URL is unique
            while URLShortener.objects.filter(shortened_url=self.shortened_url).exists():
                self.shortened_url = generate_shortened_url()
        super(URLShortener, self).save(*args, **kwargs)

    def __str__(self):
        return self.original_url
