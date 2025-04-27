from django.db import models

class URL(models.Model):
    original_url = models.URLField(max_length=2048)
    shortened_path = models.CharField(max_length=10, unique=True)
    clicks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.shortened_path} -> {self.original_url}"
