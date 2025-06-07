from django.db import models
from django.utils import timezone
from datetime import timedelta


def get_default():
    return timezone.now() + timedelta(minutes=3)


class ShortenedLink(models.Model):
    original_url = models.URLField()
    short_code = models.CharField(max_length=20, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_default)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return f'{self.original_url} -> {self.short_code}'


class Attending(models.Model):
    link = models.ForeignKey(
        'ShortenedLink', on_delete=models.CASCADE, related_name='visits')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.link.short_code} - {self.ip_address} @ {self.timestamp}"
