from .cart import CartSession

def cart_processor(request):
    """
    Make cart available in all templates.
    Usage in templates: {{ cart.get_total_quantity }}
    """
    return {'cart': CartSession(request)}