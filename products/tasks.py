import os
from celery import shared_task
from django.conf import settings
from PIL import Image

@shared_task(bind=True, max_retries=3)
def generate_thumbnail(self, product_id):
    from .models import Product 
    
    try:
        product = Product.objects.get(id=product_id)
        if not product.image:
            return "No image found"

        img = Image.open(product.image.path)
        img.thumbnail((300, 300), Image.Resampling.LANCZOS)

        thumb_name, thumb_ext = os.path.splitext(os.path.basename(product.image.name))
        thumb_filename = f"thumbnails/{thumb_name}_thumb{thumb_ext}"
        thumb_path = os.path.join(settings.MEDIA_ROOT, thumb_filename)

        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
        img.save(thumb_path)

        product.thumbnail = thumb_filename
        product.save()
        return f"Created thumbnail: {thumb_filename}"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)