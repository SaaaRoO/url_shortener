
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    
    path('', include('src.url_shortener.interfaces.urls')),  
]
