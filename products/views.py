from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from django.db import connection
from redis import Redis
from django.conf import settings
from config.celery import app as celery_app
from .models import Product
from .serializers import ProductSerializer
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug' 

    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    

    filterset_fields = ['category__name'] 
    search_fields = ['name', 'description']

    ordering_fields = ['price', 'created_at']
def health_check(request):
    services = {
        "database": "unhealthy",
        "celery_worker": "unhealthy",
        "redis": "unhealthy"
    }

    try:
        connection.ensure_connection()
        services["database"] = "healthy"
    except:
        pass
    try:
        r = Redis.from_url(settings.CELERY_BROKER_URL, socket_timeout=2)
        if r.ping():
            services["redis"] = "healthy"
    except:
        pass

    try:
        inspect = celery_app.control.inspect()
        active = inspect.active()
        if active and len(active) > 0:
            services["celery_worker"] = "healthy"
    except:
        pass

    overall_status = "ok" if all(s == "healthy" for s in services.values()) else "error"
    return JsonResponse(
        {"status": overall_status, "services": services}, 
        status=200 if overall_status == "ok" else 503
    )