from rest_framework import serializers
from src.url_shortener.models import URL


class URLShortenSerializer(serializers.Serializer):
    """
    Serializer for shortening URLs
    """
    original_url = serializers.URLField(max_length=2048, required=True)
    
    def validate_original_url(self, value):
        """Validate the URL"""
        if not URL.validate_url(value):
            raise serializers.ValidationError("Invalid URL format")
        return value


class URLRedirectSerializer(serializers.Serializer):
    """
    Serializer for URL redirect response
    """
    original_url = serializers.URLField()


class URLStatsSerializer(serializers.Serializer):
    """
    Serializer for URL statistics
    """
    short_code = serializers.CharField(max_length=10)
    original_url = serializers.URLField()
    shortened_url = serializers.URLField() 
    created_at = serializers.DateTimeField()
    last_accessed = serializers.DateTimeField(allow_null=True)
    access_count = serializers.IntegerField()
    is_active = serializers.BooleanField()


class ErrorSerializer(serializers.Serializer):
    """
    Serializer for error responses
    """
    error = serializers.CharField()