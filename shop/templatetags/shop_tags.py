from django import template
from shop.models import Product

register = template.Library()


@register.inclusion_tag("shop/components/latest_products.html")
def show_latest_products():
    products = Product.objects.order_by("-created_date")[:8]
    return {"products": products}