from django.contrib import admin
from .models import ShortenedLink, Attending


@admin.register(ShortenedLink)
class ShortenedLinkAdmin(admin.ModelAdmin):
    list_display = ('original_url', 'short_code', 'created_at', 'expires_at')
    search_fields = ('original_url', 'short_code')
    list_filter = ('created_at', 'expires_at')


@admin.register(Attending)
class AttendingAdmin(admin.ModelAdmin):
    list_display = ('link', 'ip_address', 'user_agent', 'timestamp')
    search_fields = ('ip_address', 'user_agent')
    list_filter = ('timestamp', 'link')
