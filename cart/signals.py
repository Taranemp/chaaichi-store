from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .cart import CartSession


@receiver(user_logged_in)
def sync_cart_on_login(sender, request, user, **kwargs):
    """
    Merge guest cart to database and sync to session after login.

    When a user logs in:
    1. Merge any guest cart items to their database cart
    2. Load database cart into session
    """
    cart = CartSession(request)

    if 'cart_items' in request.session:
        cart.merge_session_to_db(user)
        
    cart.sync_db_to_session(user)
