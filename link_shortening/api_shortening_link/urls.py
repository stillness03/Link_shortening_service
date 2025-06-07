from django.urls import path
from . import views


urlpatterns = [
    path('', views.home_page, name='home'),
    path('api/create/', views.created_shortenedLink, name='create_link'),
    path('<str:short_code>/', views.redirect_original, name='redirect'),
]
