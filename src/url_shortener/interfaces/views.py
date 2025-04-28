from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from src.url_shortener.infrastructure.url_repository import URLShortenerRepository
from url_shortener.application.url_service import URLShortenerService
from asgiref.sync import sync_to_async


class URLShortenerView(APIView):
    # POST method for shortening URL
    async def post(self, request):
        original_url = request.data.get('original_url')
        if not original_url:
            return Response({"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Await the coroutine properly to get the shortened URL
        shortened_url = await URLShortenerService.shorten_url(original_url)

        # Return the response with the shortened URL
        return Response({"shortened_url": shortened_url}, status=status.HTTP_201_CREATED)

    # GET method to get the original URL
    async def get(self, request, shortened_url):
        original_url = await URLShortenerService.get_original_url(shortened_url)
        if original_url:
            # Updating stats (click count)
            await URLShortenerService.update_statistics(shortened_url)
            return Response({"original_url": original_url}, status=status.HTTP_200_OK)
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)


class URLStatsView(APIView):
    # GET method for fetching URL stats
    async def get(self, request, shortened_url):
        try:
            # Get original URL asynchronously
            original_url = await URLShortenerService.get_original_url(shortened_url)
            if original_url:
                # Ensure we use sync_to_async for the ORM call to retrieve click count
                url_instance = await sync_to_async(URLShortenerRepository.get_url_by_shortened)(shortened_url)
                if url_instance:
                    return Response({"click_count": url_instance.click_count}, status=status.HTTP_200_OK)
                return Response({"error": "Click count not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": "URL not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
