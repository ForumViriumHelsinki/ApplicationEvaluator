from django.http import JsonResponse


def health_check(request):
    """Simple health check endpoint for Kubernetes probes."""
    return JsonResponse({"status": "healthy"})
