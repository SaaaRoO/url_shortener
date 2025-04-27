# interfaces/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from url_shortener.application.url_service import URLShortenerService
from url_shortener.infrastructure.url_repository import URLShortenerRepository

class URLShortenerView(APIView):

    async def post(self, request):
        original_url = request.data.get('original_url')
        if not original_url:
            return Response({"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST)

        shortened_url = await URLShortenerService.shorten_url(original_url)
        return Response({"shortened_url": shortened_url}, status=status.HTTP_201_CREATED)

    async def get(self, request, shortened_url):
        original_url = await URLShortenerService.get_original_url(shortened_url)
        if original_url:
            await URLShortenerService.update_statistics(shortened_url)
            return Response({"original_url": original_url}, status=status.HTTP_200_OK)
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

class URLStatsView(APIView):

    async def get(self, request, shortened_url):
        url = await URLShortenerService.get_original_url(shortened_url)
        if url:
            # Assuming 'click_count' is a property you can track.
            click_count = URLShortenerRepository.get_url_by_shortened(shortened_url).click_count
            return Response({"click_count": click_count}, status=status.HTTP_200_OK)
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
