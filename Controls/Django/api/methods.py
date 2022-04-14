from django.http import HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render


# decorator
def require_mobile_app(methods):
    def decorator(function):
        @require_http_methods(methods)
        def wrapper(request):
            if config.debug or request.META.get('HTTP_USER_AGENT') == 'ArchieMobile':
                return function(request)
            else:
                return HttpResponse(status = 444)
        return wrapper
    return decorator
