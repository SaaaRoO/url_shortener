from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from asgiref.sync import async_to_sync
from src.url_shortener.application.url_service import URLService


class CreateShortenedURLView(APIView):
    def post(self, request, *args, **kwargs):
        original_url = request.data.get("original_url", "").strip()
        
        if not original_url:
            raise ValidationError({"error": "URL is required"})
        
        # Use async_to_sync to call the async method
        response = async_to_sync(URLService.create_shortened_url)(original_url)
        
        # Check if the response has an error
        if "error" in response:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(response, status=status.HTTP_201_CREATED)

class GetOriginalURLView(APIView):
    def get(self, request, short_code, *args, **kwargs):
        original_url, success = async_to_sync(URLService.get_original_url)(short_code)

        if not success:
            return Response({"error": "URL not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"original_url": original_url}, status=status.HTTP_200_OK)


class GetURLStatsView(APIView):
    def get(self, request, short_code, *args, **kwargs):
        stats = async_to_sync(URLService.get_url_stats)(short_code)

        if not stats:
            return Response({"error": "URL stats not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(stats, status=status.HTTP_200_OK)