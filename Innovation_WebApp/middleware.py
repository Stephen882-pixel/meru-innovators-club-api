import time
import logging

logger = logging.getLogger('request.logs')

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        # Get client info
        ip = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        path = request.path
        method = request.method
        user = request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
        
        # Process the request
        response = self.get_response(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log the request details
        logger.info(
            f"Request: {method} {path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.2f}s | "
            f"IP: {ip} | "
            f"User: {user} | "
            f"User-Agent: {user_agent}"
        )

        return response
        
      