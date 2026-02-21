from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from apps.products.models import ProductVariant, Inventory
from ..models import Cart, CartItem
from .serializers import CartSerializer ,UpdateCartItemSerializer
from rest_framework.generics import RetrieveAPIView
from django.db.models import Prefetch
from rest_framework.exceptions import NotFound


@extend_schema(
    summary="Add product variant to cart",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "variant_id": {"type": "integer"},
                "quantity": {"type": "integer", "minimum": 1},
            },
            "required": ["variant_id"],
        }
    },
    responses={200: CartSerializer},
)
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        variant_id = request.data.get("variant_id")
        quantity = int(request.data.get("quantity", 1))

        # 🔒 Lock ProductVariant row
        variant = get_object_or_404(
            ProductVariant.objects.select_for_update(),
            id=variant_id,
            is_active=True,
            product__is_active=True
        )

        # 🔒 Lock Inventory row separately
        inventory = Inventory.objects.select_for_update().get(
            variant=variant
        )

        if inventory.available_stock < quantity:
            return Response(
                {"detail": "Insufficient stock"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart, _ = Cart.objects.get_or_create(user=request.user)

        item, created = CartItem.objects.select_for_update().get_or_create(
            cart=cart,
            variant=variant,
            defaults={
                "quantity": quantity,
                "unit_price": variant.selling_price,
                "discount_percent": variant.discount_percent
            }
        )

        if not created:
            if inventory.available_stock < (item.quantity + quantity):
                return Response(
                    {"detail": "Insufficient stock"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            item.quantity += quantity
            item.save()

        cart.recalculate_totals()

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK
        )
    





@extend_schema(
    summary="Retrieve authenticated user's cart",
    description="Returns the active cart of the authenticated user including all cart items and totals.",
    responses={
        200: CartSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        404: OpenApiResponse(description="Cart not found."),
    },
    tags=["cart"],
)
class CartDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        try:
            return (
                Cart.objects
                .prefetch_related(
                    Prefetch(
                        "items",
                        queryset=CartItem.objects.select_related(
                            "variant__product",
                            "variant__inventory",
                        ).prefetch_related(
                            "variant__product__images"
                        )
                    )
                )
                .get(user=self.request.user)
            )
        except Cart.DoesNotExist:
            raise NotFound("Cart not found.")








@extend_schema(
    summary="Update cart item quantity",
    description=(
        "Updates the quantity of a cart item. "
        "If quantity is 0, the item will be removed from the cart. "
        "Validates stock availability before updating."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "quantity": {
                    "type": "integer",
                    "minimum": 0,
                    "example": 2
                }
            },
            "required": ["quantity"],
        }
    },
    responses={
        200: CartSerializer,
        400: OpenApiResponse(description="Invalid quantity or insufficient stock."),
        401: OpenApiResponse(description="Authentication required."),
        404: OpenApiResponse(description="Cart item not found."),
    },
    tags=["cart"],
)
class UpdateCartItemView(APIView):
    """
    Update quantity of a cart item.
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_quantity = serializer.validated_data["quantity"]

        # 🔒 Lock cart item
        cart = request.user.cart

        cart_item = get_object_or_404(
            CartItem.objects.select_for_update(),
            id=item_id,
            cart=cart
        )

        variant = cart_item.variant  # already loaded

        inventory = Inventory.objects.select_for_update().get(
            variant_id=variant.id
        )

        # 🗑 If quantity is 0 → remove item
        if new_quantity == 0:
            cart_item.delete()
            cart.recalculate_totals()
            return Response(
                CartSerializer(cart).data,
                status=status.HTTP_200_OK
            )

        # ❌ Check product & variant active
        if not variant.is_active or not variant.product.is_active:
            return Response(
                {"detail": "Product is no longer available."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 📦 Validate available stock
        if inventory.available_stock < new_quantity:
            return Response(
                {"detail": "Insufficient stock available."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔄 Update quantity
        cart_item.quantity = new_quantity

        # 🔥 Update snapshot price if needed
        cart_item.unit_price = variant.selling_price
        cart_item.discount_percent = variant.discount_percent

        cart_item.save()

        # 🧮 Recalculate totals
        cart.recalculate_totals()

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK
        )
    


@extend_schema(
    summary="Remove cart item",
    description="Removes a single item from the authenticated user's cart.",
    responses={
        200: CartSerializer,
        401: OpenApiResponse(description="Authentication required."),
        404: OpenApiResponse(description="Cart item not found."),
    },
    tags=["cart"],
)
class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, item_id):

        # Get user's cart safely
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # 🔒 Lock the cart item row
        cart_item = get_object_or_404(
            CartItem.objects.select_for_update(),
            id=item_id,
            cart=cart
        )

        # Delete the item
        cart_item.delete()

        # Recalculate totals
        cart.recalculate_totals()

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK
        )
    




@extend_schema(
    summary="Clear entire cart",
    description="Removes all items from the authenticated user's cart and resets totals.",
    responses={
        200: CartSerializer,
        401: OpenApiResponse(description="Authentication required."),
        404: OpenApiResponse(description="Cart not found."),
    },
    tags=["cart"],
)
class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request):

        try:
            cart = request.user.cart
        except Cart.DoesNotExist:
            return Response(
                {"detail": "Cart not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 🔒 Lock cart row
        cart = Cart.objects.select_for_update().get(pk=cart.pk)

        # Delete all items in one query
        cart.items.all().delete()

        # Reset totals
        cart.subtotal = 0
        cart.tax_amount = 0
        cart.shipping_amount = 0
        cart.total_amount = 0
        cart.save(update_fields=[
            "subtotal",
            "tax_amount",
            "shipping_amount",
            "total_amount",
            "updated_at"
        ])

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK
        )
    





@extend_schema(
    summary="Validate cart before checkout",
    description="Validates stock, product status, and pricing before checkout.",
    responses={
        200: CartSerializer,
        400: OpenApiResponse(description="Cart validation failed."),
        401: OpenApiResponse(description="Authentication required."),
    },
    tags=["cart"],
)
class ValidateCartView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        try:
            cart = request.user.cart
        except Cart.DoesNotExist:
            return Response(
                {"detail": "Cart not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not cart.items.exists():
            return Response(
                {"detail": "Cart is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        errors = []
        price_updated = False

        for item in cart.items.select_related("variant__product"):

            variant = item.variant

            # 🔒 Lock inventory row
            inventory = Inventory.objects.select_for_update().get(
                variant_id=variant.id
            )

            # ❌ Check active status
            if not variant.is_active or not variant.product.is_active:
                errors.append({
                    "item_id": item.id,
                    "error": "Product no longer available."
                })
                continue

            # ❌ Check stock
            if inventory.available_stock < item.quantity:
                errors.append({
                    "item_id": item.id,
                    "error": "Insufficient stock."
                })
                continue

            # 🔄 Check price change
            current_price = variant.selling_price

            if item.unit_price != current_price:
                item.unit_price = current_price
                item.discount_percent = variant.discount_percent
                item.save()
                price_updated = True

        if errors:
            return Response(
                {
                    "status": "failed",
                    "errors": errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Recalculate totals after possible price updates
        cart.recalculate_totals()

        return Response(
            {
                "status": "valid",
                "price_updated": price_updated,
                "cart": CartSerializer(cart).data
            },
            status=status.HTTP_200_OK
        )
    
from django.db.models import Sum

class CartCountView(APIView):
    """
    Returns total quantity of items in user's cart.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = getattr(request.user, "cart", None)

        if not cart:
            return Response({"count": 0})

        total_quantity = cart.items.aggregate(
            total=Sum("quantity")
        )["total"] or 0

        return Response({"count": total_quantity})