
from django.core.cache import cache
from django.http import JsonResponse
from time import time

class RateLimitMiddleware:
    """
    Limits the number of requests per IP using Django cache.
    Default: 100 requests per hour per IP.
    """

    RATE_LIMIT = 100  # max requests
    TIME_WINDOW = 60 * 60  # 1 hour (in seconds)

    def __init__(self, get_response):
        self.get_response = get_response
        

    def __call__(self, request):
        ip = self.get_client_ip(request)
        cache_key = f"rl:{ip}"
        request_info = cache.get(cache_key, {'count': 0, 'start_time': time()})

        elapsed = time() - request_info['start_time']
        if elapsed > self.TIME_WINDOW:
            # Reset window
            request_info = {'count': 1, 'start_time': time()}
        else:
            request_info['count'] += 1

        if request_info['count'] > self.RATE_LIMIT:
            return JsonResponse(
                {"error": "Rate limit exceeded. Try again later."},
                status=429
            )

        cache.set(cache_key, request_info, timeout=self.TIME_WINDOW)
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
