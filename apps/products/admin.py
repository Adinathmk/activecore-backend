from django.contrib import admin
from .models import (
    Category,
    ProductType,
    Product,
    ProductFeature,
    ProductImage,
    ProductVariant,
    Inventory,
    ProductMetrics,
)

# -------------------------
# Category
# -------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


# -------------------------
# Product Type
# -------------------------
@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


# -------------------------
# Inlines
# -------------------------
class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    readonly_fields = ("selling_price",)


# -------------------------
# Product
# -------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "product_type",
        "is_active",
        "is_new_arrival",
        "is_top_selling",
        "created_at",
    )

    list_filter = (
        "category",
        "product_type",
        "is_active",
        "is_top_selling",
    )

    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)

    inlines = [
        ProductFeatureInline,
        ProductImageInline,
        ProductVariantInline,
    ]


# -------------------------
# Inventory (INLINE of Variant)
# -------------------------
class InventoryInline(admin.StackedInline):
    model = Inventory
    can_delete = False
    extra = 0
    readonly_fields = ("available_stock",)


# -------------------------
# Product Variant
# -------------------------
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "size",
        "sku",
        "price",
        "discount_percent",
        "selling_price",
        "is_active",
        "stock_display",
    )

    def stock_display(self, obj):
        return obj.inventory.stock if hasattr(obj, "inventory") else 0

    list_filter = ("is_active", "size")
    search_fields = ("sku",)
    inlines = [InventoryInline]


# -------------------------
# Product Metrics
# -------------------------

@admin.register(ProductMetrics)
class ProductMetricsAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "avg_rating",
        "rating_count",
    )
    readonly_fields = ("avg_rating", "rating_count")
