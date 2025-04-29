from django.urls import path
from .views import CreateShortenedURLView, GetOriginalURLView, GetURLStatsView

urlpatterns = [
    path('create/', CreateShortenedURLView.as_view(), name='shorten_url'),
    path('<str:short_code>/', GetOriginalURLView.as_view(), name='redirect_url'),
    path('<str:short_code>/stats/', GetURLStatsView.as_view(), name='url_stats'),
]
