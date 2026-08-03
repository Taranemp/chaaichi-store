from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404

from shop.models import Product
from .cart import CartSession



def _cart_json_response(cart_session, success=True, message=None):

    summary = cart_session.get_price_summary()

    data = {
        "success": success,

        "total_quantity": cart_session.get_total_quantity(),

        "original_total": float(
            summary["original_total"]
        ),

        "discount_total": float(
            summary["discount_total"]
        ),

        "total_price": float(
            summary["final_total"]
        ),

        "cart_count": cart_session.get_count(),
    }


    if message:
        data["message"] = message


    return JsonResponse(data)



# =========================
# Add To Cart
# =========================

class AddToCartView(View):

    def post(self, request, *args, **kwargs):

        product_id = request.POST.get(
            "product_id"
        )

        quantity = int(
            request.POST.get(
                "quantity",
                1
            )
        )


        if not product_id:

            return JsonResponse(
                {
                    "success": False,
                    "message": "product_id is required"
                },
                status=400
            )


        try:

            get_object_or_404(
                Product,
                id=product_id
            )

        except Http404:

            return JsonResponse(
                {
                    "success": False,
                    "message": "Product not found"
                },
                status=404
            )


        cart = CartSession(request)

        cart.add(
            product_id,
            quantity
        )


        return _cart_json_response(
            cart,
            message="Product added to cart"
        )



# =========================
# Remove Cart
# =========================

class RemoveFromCartView(View):

    def post(self, request, *args, **kwargs):

        product_id = request.POST.get(
            "product_id"
        )


        if not product_id:

            return JsonResponse(
                {
                    "success": False,
                    "message": "product_id is required"
                },
                status=400
            )


        cart = CartSession(request)

        cart.remove(
            product_id
        )


        return _cart_json_response(
            cart,
            message="Product removed from cart"
        )



# =========================
# Update Cart
# =========================

class UpdateCartView(View):

    def post(self, request, *args, **kwargs):

        product_id = request.POST.get(
            "product_id"
        )


        quantity = int(
            request.POST.get(
                "quantity",
                1
            )
        )


        if not product_id:

            return JsonResponse(
                {
                    "success": False,
                    "message": "product_id is required"
                },
                status=400
            )


        cart = CartSession(request)


        if quantity <= 0:

            cart.remove(
                product_id
            )

        else:

            cart.update_quantity(
                product_id,
                quantity
            )


        return _cart_json_response(
            cart,
            message="Cart updated"
        )



# =========================
# Clear Cart
# =========================

class ClearCartView(View):

    def post(self, request, *args, **kwargs):

        cart = CartSession(request)

        cart.clear()


        return _cart_json_response(
            cart,
            message="Cart cleared"
        )



# =========================
# Cart Summary
# =========================

class CartSummaryView(TemplateView):

    template_name = "cart/cart-summary.html"


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        cart = CartSession(
            self.request
        )


        summary = cart.get_price_summary()


        context["cart_items"] = (
            cart.get_items()
        )


        context["total_quantity"] = (
            cart.get_total_quantity()
        )


        context["original_total"] = (
            summary["original_total"]
        )


        context["discount_total"] = (
            summary["discount_total"]
        )


        context["total_price"] = (
            summary["final_total"]
        )


        context["cart_count"] = (
            cart.get_count()
        )


        return context