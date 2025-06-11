from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShortenedLinkViewSet, main_page, redirect_original

router = DefaultRouter()
router.register(r'links', ShortenedLinkViewSet, basename='shortenedlink')

urlpatterns = [
    path('', main_page, name='main_page'),
    path('api/', include(router.urls)),
    path('<str:short_code>/', redirect_original, name='redirect_original')
]
