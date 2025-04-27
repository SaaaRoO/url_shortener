
from django.urls import path
from .views import URLShortenerView, URLStatsView

urlpatterns = [
    path('api/shorten', URLShortenerView.as_view(), name='shorten-url'),
    path('api/<str:shortened_url>', URLShortenerView.as_view(), name='get-original-url'),
    path('api/stats/<str:shortened_url>', URLStatsView.as_view(), name='url-stats'),
]
