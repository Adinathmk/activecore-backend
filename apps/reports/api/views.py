from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
import logging

logger = logging.getLogger(__name__)

from apps.accounts.models import User
from apps.products.models import Product
from apps.orders.models import Order, OrderItem, OrderStatus

class DashboardMetricsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Role.ADMIN:
            logger.warning(f"Unauthorized access attempt to dashboard metrics by user {request.user.id}")
            return Response({"detail": "You do not have permission to perform this action."}, status=403)

        logger.info(f"Dashboard metrics requested by user {request.user.id}")

     
        total_users = User.objects.filter(role=User.Role.CUSTOMER).count()
        total_products = Product.objects.filter(is_active=True).count()
        
      
        successful_orders = Order.objects.exclude(status__in=[OrderStatus.PENDING, OrderStatus.CANCELLED, OrderStatus.FAILED])
        total_sales = successful_orders.count()
        
        revenue_agg = successful_orders.aggregate(total_revenue=Sum('total_amount'))
        total_revenue = revenue_agg['total_revenue'] or 0

     
        revenue_by_category_raw = (
            OrderItem.objects
            .filter(order__in=successful_orders)
            .values('product_name')
        )
        
    
        category_revenue = {}
        type_sales = {}
        for item in OrderItem.objects.filter(order__in=successful_orders):
            try:
           
                real_product_id = item.product_id.int if hasattr(item.product_id, 'int') else item.product_id
                product = Product.objects.get(id=real_product_id)
                cat_name = product.category.name
                type_name = product.product_type.name
            except (Product.DoesNotExist, AttributeError, ValueError) as e:
                logger.error(f"Failed to find product info for OrderItem {item.id}: {e}")
                cat_name = "Unknown"
                type_name = "Unknown"
            
            # Use total_price from OrderItem for revenue
            item_total = float(item.total_price)
            if cat_name in category_revenue:
                category_revenue[cat_name] += item_total
            else:
                category_revenue[cat_name] = item_total

            # Use quantity from OrderItem for top selling types
            item_quantity = item.quantity
            if type_name in type_sales:
                type_sales[type_name] += item_quantity
            else:
                type_sales[type_name] = item_quantity
                
        # Format for charts: [{"name": "Category A", "value": 100}, ...]
        revenue_by_category = [{"name": key, "value": val} for key, val in category_revenue.items()]
        
    
        top_selling_types_list = [{"name": key, "quantity": val} for key, val in type_sales.items()]
        top_selling_types = sorted(top_selling_types_list, key=lambda x: x["quantity"], reverse=True)[:5]


        top_selling_raw = (
            OrderItem.objects
            .filter(order__in=successful_orders)
            .values('product_name')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')[:5]
        )
        top_selling_products = [{"name": item['product_name'], "quantity": item['total_quantity']} for item in top_selling_raw]


        status_distribution_raw = (
            Order.objects
            .values('status')
            .annotate(count=Count('id'))
        )
        order_status_distribution = [{"status": item['status'], "count": item['count']} for item in status_distribution_raw]

        data = {
            "total_users": total_users,
            "total_products": total_products,
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "revenue_by_category": revenue_by_category,
            "top_selling_products": top_selling_products,
            "top_selling_types": top_selling_types,
            "order_status_distribution": order_status_distribution,
        }

        return Response(data)
