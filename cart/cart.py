from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from shop.models import Product
from .models import Cart, CartItem


class CartSession:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.user = request.user
        self._cart = None

    def _get_or_create_cart(self):
        if self._cart is not None:
            return self._cart

        if self.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.user)
        else:
            if not self.session.session_key:
                self.session.save()
            cart, _ = Cart.objects.get_or_create(session_key=self.session.session_key)

        self._cart = cart
        return cart

    def add(self, product_id, quantity=1):
        if quantity <= 0:

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return

        cart = self._get_or_create_cart()
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

    def remove(self, product_id):
        cart = self._get_or_create_cart()
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()

    def update_quantity(self, product_id, quantity):
        if quantity <= 0:
            self.remove(product_id)
            return
        cart = self._get_or_create_cart()
        CartItem.objects.filter(cart=cart, product_id=product_id).update(quantity=quantity)

    def clear(self):
        cart = self._get_or_create_cart()
        cart.items.all().delete()

    def get_items(self):
        cart = self._get_or_create_cart()
        return cart.items.select_related("product").all()

    def get_total_price(self):
        cart = self._get_or_create_cart()
        return cart.calculate_total_price()

    def get_total_quantity(self):
        cart = self._get_or_create_cart()
        return cart.get_total_quantity()

    def get_count(self):
        cart = self._get_or_create_cart()
        return cart.items.count()

    @transaction.atomic
    def merge_session_to_db(self, user):
        session_key = self.session.session_key
        if not session_key:
            return

        try:
            session_cart = Cart.objects.get(session_key=session_key)
        except Cart.DoesNotExist:
            return

        user_cart, _ = Cart.objects.get_or_create(user=user)

        for session_item in session_cart.items.select_related("product").all():
            cart_item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=session_item.product,
                defaults={"quantity": session_item.quantity},
            )
            if not created:
                cart_item.quantity += session_item.quantity
                cart_item.save()

        session_cart.items.all().delete()
        session_cart.delete()

        self._cart = user_cart

    def sync_db_to_session(self, user):
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            self.session["cart_items"] = []
            self.session.modified = True
            return

        items_data = []
        for item in cart.items.select_related("product").all():
            items_data.append(
                {
                    "product_id": item.product.id,
                    "title": item.product.title,
                    "slug": item.product.slug,
                    "image": item.product.image.url if item.product.image else None,
                    "price": float(item.product.get_price()),
                    "quantity": item.quantity,
                    "subtotal": float(item.subtotal()),
                }
            )

        self.session["cart_items"] = items_data
        self.session["cart_total_quantity"] = cart.get_total_quantity()
        self.session["cart_total_price"] = float(cart.calculate_total_price())
        self.session.modified = True

    def is_empty(self):
        cart = self._get_or_create_cart()
        return cart.is_empty()
