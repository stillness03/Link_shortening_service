from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.crypto import get_random_string

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

from .models import Attending

from .serializers import ShortenedLinkApi
from .models import ShortenedLink


def home_page(request):
    return render(request, 'main.html')


@api_view(['POST'])
def created_shortenedLink(request):
    print("POST запит отримано:", request.data)

    original_url = request.data.get('original_url')
    expires_at = request.data.get('expires_at')
    if not original_url:
        print("Немає original_url")
        return Response({'error': 'Поле original_url обовʼязкове.'}, status=400)

    short_code = get_random_string(6)
    while ShortenedLink.objects.filter(short_code=short_code).exists():
        short_code = get_random_string(6)

    try:
        link = ShortenedLink.objects.create(
            original_url=original_url,
            short_code=short_code
        )

        short_url = request.build_absolute_uri(f"/{short_code}")
        qr = qrcode.make(short_url)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)
        file_name = f"qr_{short_code}.png"
        link.qr_code.save(file_name, ContentFile(buffer.read()), save=True)

    except Exception as e:
        print("Помилка при збереженні:", e)
        return Response({'error': str(e)}, status=500)

    print("Посилання створено:", link.short_code)
    serializer = ShortenedLinkApi(link)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def redirect_original(request, short_code):
    try:
        link = ShortenedLink.objects.get(short_code=short_code)

        if link.expires_at and timezone.now() > link.expires_at:
            return HttpResponse("Посилання неактивне", status=410)

        ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        Attending.objects.create(
            link=link,
            ip_address=ip,
            user_agent=user_agent
        )

        return HttpResponseRedirect(link.original_url)

    except ShortenedLink.DoesNotExist:
        return HttpResponse("Посилання не знайдено", status=404)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
