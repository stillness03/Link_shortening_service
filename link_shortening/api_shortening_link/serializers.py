from rest_framework import serializers
from .models import ShortenedLink


class ShortenedLinkApi(serializers.ModelSerializer):
    class Meta:
        model = ShortenedLink
        fields = ['original_url', 'short_code', 'created_at', 'expires_at']
        read_only_fields = ['created_at', 'expires_at']
