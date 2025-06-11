from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.http import HttpResponseRedirect
from .models import ShortenedLink, Attending
from .serializers import ShortenedLinkApi

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


class ShortenedLinkViewSet(viewsets.ModelViewSet):
    queryset = ShortenedLink.objects.all()
    serializer_class = ShortenedLinkApi

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        short_code = get_random_string(6)
        while ShortenedLink.objects.filter(short_code=short_code).exists():
            short_code = get_random_string(6)

        link = serializer.save(short_code=short_code)

        short_url = request.build_absolute_uri(
            f"/api/links/redirect/{short_code}/")
        qr = qrcode.make(short_url)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)
        file_name = f"qr_{short_code}.png"
        link.qr_code.save(file_name, ContentFile(buffer.read()), save=True)

        output_serializer = self.get_serializer(link)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


# html
def main_page(request):
    if request.method == 'POST':
        original_url = request.POST.get('original_url')
        expires_at = request.POST.get('expires_at')

        if original_url:
            short_code = get_random_string(6)
            while ShortenedLink.objects.filter(short_code=short_code).exists():
                short_code = get_random_string(6)

            link_data = {
                'original_url': original_url,
                'short_code': short_code
            }
            if expires_at:
                link_data['expires_at'] = expires_at

            link = ShortenedLink.objects.create(**link_data)

            short_url = request.build_absolute_uri(f"/{short_code}")
            qr = qrcode.make(short_url)
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            buffer.seek(0)
            file_name = f"qr_{short_code}.png"
            link.qr_code.save(file_name, ContentFile(buffer.read()), save=True)

            return render(request, 'main.html', {
                'short_url': short_url,
                'qr_code_url': link.qr_code.url,
            })

    return render(request, 'main.html')


def redirect_original(request, short_code):
    try:
        link = ShortenedLink.objects.get(short_code=short_code)

        if link.expires_at and timezone.now() > link.expires_at:
            return render(request, 'main.html', {
                'error': 'Силка не дійсна (протермінована)'
            })

        ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        Attending.objects.create(
            link=link,
            ip_address=ip,
            user_agent=user_agent
        )

        return HttpResponseRedirect(link.original_url)

    except ShortenedLink.DoesNotExist:
        return render(request, 'main.html', {
            'error': 'Посилання не знайдено'
        })


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
