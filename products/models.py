import uuid
from django.db import models
from django.core.validators import MinValueValidator
from categories.models import Category
from .services import generate_unique_slug
from .tasks import generate_thumbnail

class Product(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, db_index=True, blank=True)

    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    stock = models.IntegerField(validators=[MinValueValidator(0)])

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    image = models.ImageField(upload_to="products/", null=True, blank=True)
    thumbnail = models.ImageField(upload_to="products/thumbnails/", null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]

    def __str__(self):
        return self.name
    
    from .services import generate_unique_slug

    def save(self, *args, **kwargs):
        is_new_image = False

        if self.pk:
            old = Product.objects.filter(pk=self.pk).first()
            if old and old.image != self.image:
                is_new_image = True
        else:
            if self.image:
                is_new_image = True

        if not self.slug:
            self.slug = generate_unique_slug(Product, self.name)

        super().save(*args, **kwargs)

        if is_new_image:
            generate_thumbnail.delay(self.id)