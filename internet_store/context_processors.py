from .cart import Cart
from .models import Category


def shop(request):
    cart = Cart(request)
    return {
        "menu_categories": Category.objects.filter(parent__isnull=True, in_menu=True),
        "cart_count": len(cart),
        "SHOP": {
            "name": "SHOP",
            "phone": "0 800 000 000",
            "email": "info@shop.example",
            "address": "м. Київ, вул. Прикладна, 1",
            "free_delivery_from": 1500,
        },
    }
