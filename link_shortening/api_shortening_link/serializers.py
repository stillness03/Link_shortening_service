from rest_framework import serializers
from .models import ShortenedLink


class ShortenedLinkApi(serializers.ModelSerializer):
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = ShortenedLink
        fields = ['original_url', 'short_code',
                  'created_at', 'expires_at', 'qr_code_url']
        read_only_fields = ['created_at', 'expires_at', 'short_code']

    def get_qr_code_url(self, obj):
        if obj.qr_code:
            return obj.qr_code.url
        return None
