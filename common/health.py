from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django_redis import get_redis_connection
from config.celery import app as celery_app
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    status_code = 200
    services = {
        "database": "unhealthy",
        "celery_worker": "unhealthy",
        "redis": "unhealthy"
    }

    try:
        connection.ensure_connection()
        services["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        status_code = 503

    try:
        redis_conn = get_redis_connection("default")
        redis_conn.ping()
        services["redis"] = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        status_code = 503

    try:
        inspect = celery_app.control.inspect()
        active_workers = inspect.ping()
        if active_workers:
            services["celery_worker"] = "healthy"
        else:
            status_code = 503
    except Exception as e:
        logger.error(f"Celery health check failed: {e}")
        status_code = 503

    overall_status = "ok" if status_code == 200 else "error"

    return JsonResponse(
        {
            "status": overall_status,
            "services": services
        },
        status=status_code
    )