"""
URL configuration for URL shortener project
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include URL shortener URLs
    path('api/', include('src.url_shortener.interfaces.urls')),
]