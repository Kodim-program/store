from decimal import Decimal

from .models import Product

SESSION_KEY = "cart"
MAX_QTY = 99


class Cart:
    """Кошик у сесії: {product_id: quantity}."""

    def __init__(self, request):
        self.session = request.session
        self.data = self.session.setdefault(SESSION_KEY, {})

    def _save(self):
        self.session.modified = True

    def add(self, product, qty=1):
        key = str(product.pk)
        self.data[key] = min(self.data.get(key, 0) + qty, MAX_QTY)
        self._save()

    def set(self, product_id, qty):
        key = str(product_id)
        if qty <= 0:
            self.data.pop(key, None)
        elif key in self.data:
            self.data[key] = min(qty, MAX_QTY)
        self._save()

    def remove(self, product_id):
        self.data.pop(str(product_id), None)
        self._save()

    def clear(self):
        self.session.pop(SESSION_KEY, None)
        self.session.modified = True

    def __len__(self):
        return sum(self.data.values())

    def items(self):
        products = Product.objects.filter(pk__in=self.data.keys(), is_active=True)
        for p in products:
            qty = self.data[str(p.pk)]
            yield {"product": p, "quantity": qty, "subtotal": p.price * qty}

    @property
    def total(self):
        return sum((i["subtotal"] for i in self.items()), Decimal("0"))
