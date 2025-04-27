
from rest_framework import serializers

class URLShortenerSerializer(serializers.Serializer):
    original_url = serializers.URLField()
