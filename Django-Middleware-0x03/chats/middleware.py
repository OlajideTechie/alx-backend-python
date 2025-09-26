import logging
from datetime import datetime, timedelta
from django.http import JsonResponse

from django.utils.deprecation import MiddlewareMixin

message_counts = {}

# Configure logger to write to a file
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('requests.log')
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class RequestLoggingMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        user_str = user.email if user and user.is_authenticated else 'Anonymous'
        logger.info(f"{datetime.now()} - User: {user_str} - Path: {request.path}")
        
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        # Deny access if current time is outside 18:00-21:00 (6PM-9PM)
        if current_hour < 18 or current_hour > 21:
            return JsonResponse({"detail": "Access allowed only between 6PM and 9PM."}, status=403)
        
        response = self.get_response(request)
        return response
    


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.rstrip('/')  # normalize path
        if path == '/api/messages' and request.method == 'POST':
            ip = self.get_client_ip(request)
            now = datetime.now()
            window_start = now - timedelta(minutes=1)

            # Clean up old timestamps
            timestamps = message_counts.get(ip, [])
            timestamps = [t for t in timestamps if t > window_start]

            # Debug: print current count
            print(f"[RateLimit] IP: {ip}, Count: {len(timestamps)}")

            if len(timestamps) >= 5:
                return JsonResponse(
                    {"detail": "Message rate limit exceeded (5 per minute)."},
                    status=429
                )

            # Record current message timestamp
            timestamps.append(now)
            message_counts[ip] = timestamps

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    
class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            if user.role not in ['admin', 'moderator']:
                return JsonResponse(
                    {"detail": "You do not have permission to access this resource."},
                    status=403
                )
        # If user is not authenticated, let other middleware handle it
        response = self.get_response(request)
        return response