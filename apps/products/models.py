from django.db import models
from .mixins import SlugMixin
import uuid
from django.db.models import Q


class Category(SlugMixin):
    name = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

#--------------------------------------------------------------------


class ProductType(SlugMixin):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


#-----------------------------------------------------------------------

class Product(SlugMixin):
    name = models.CharField(max_length=255)
    description = models.TextField()

    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    product_type = models.ForeignKey(ProductType, on_delete=models.PROTECT)

    is_active = models.BooleanField(default=True)
    is_new_arrival = models.BooleanField(default=False)
    is_top_selling = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_top_selling"]),
            models.Index(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

#-----------------------------------------------------------------------

class ProductFeature(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="features",
        on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

#------------------------------------------------------------------------

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE
    )
    image_url = models.URLField()
    is_primary = models.BooleanField(default=False)
    is_secondary = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=models.Q(is_primary=True),
                name="one_primary_image_per_product",
            ),
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_secondary=True),
                name="one_secondary_image_per_product",
            ),
            models.CheckConstraint(
                condition=~(Q(is_primary=True) & Q(is_secondary=True)),
                name="image_not_both_primary_and_secondary",
            )

        ]


#--------------------------------------------------------------

from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

class ProductVariant(models.Model):

    SIZE_CHOICES = [
        ("XS", "Extra Small"),
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra Large"),
        ("XXL", "Extra Extra Large"),
    ]

    product = models.ForeignKey(
        Product,
        related_name="variants",
        on_delete=models.CASCADE
    )

    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    sku = models.CharField(max_length=50, unique=True,blank=True,null=True,)  #stock keeping unit

    price = models.DecimalField(    
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "size"],
                name="unique_variant_size_per_product"
            )
        ]

    @property
    def selling_price(self):
        if self.price is None or self.discount_percent is None:
            return Decimal("0.00")
        discount = (self.price * self.discount_percent) / Decimal("100")
        return self.price - discount

    def __str__(self):
        return f"{self.product.name} - {self.size}"
    
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)




#----------------------------------------------------------------


from django.db import models
from django.db.models import F, Q

class Inventory(models.Model):
    variant = models.OneToOneField(
        ProductVariant,
        related_name="inventory",
        on_delete=models.CASCADE
    )
    stock = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)   # for payment processong varients 

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(reserved__lte=F("stock")),
                name="reserved_lte_stock",
            )
        ]

    @property
    def available_stock(self):
        return self.stock - self.reserved



#-----------------------------------------------------------------------------------------

from django.db.models import Avg, Count

class ProductMetrics(models.Model):
    product = models.OneToOneField(
        Product,
        related_name="metrics",
        on_delete=models.CASCADE
    )
    avg_rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0
    )
    rating_count = models.PositiveIntegerField(default=0)

    def recalculate(self):
        data = self.product.ratings.aggregate(
            avg=Avg("rating"),
            count=Count("id")
        )

        self.avg_rating = round(data["avg"] or 0, 1)
        self.rating_count = data["count"]
        self.save(update_fields=["avg_rating", "rating_count"])


from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class ProductRating(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="ratings",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user")  



# Category
# ProductType
# Product
# ProductFeature
# ProductImage
# ProductVariant
# Inventory
# ProductMetrics
# ProductRating
