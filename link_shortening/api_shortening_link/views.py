from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.crypto import get_random_string

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

        return HttpResponseRedirect(link.original_url)

    except ShortenedLink.DoesNotExist:
        return HttpResponse("Посилання не знайдено", status=404)
