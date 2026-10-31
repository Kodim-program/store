from django.test import TestCase

# Create your tests here.
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Order, Product


class ShopFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_shop", verbosity=0)

    def test_pages_ok(self):
        p = Product.objects.first()
        for url in [reverse("index"), reverse("catalog"), reverse("catalog_category", args=["spalnya"]),
                    reverse("catalog") + "?sale=1&q=Ковдра&sort=-price", p.get_absolute_url(),
                    reverse("cart"), reverse("about"), reverse("delivery"), reverse("returns"), reverse("contacts")]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_cart_and_checkout(self):
        p = Product.objects.get(slug="podushka-comfort")
        self.client.post(reverse("cart_add", args=[p.pk]), {"quantity": 2})
        self.assertContains(self.client.get(reverse("cart")), "878")
        r = self.client.post(reverse("checkout"), {
            "name": "Іван", "phone": "+380501112233", "city": "Київ", "address": "НП №1"})
        order = Order.objects.get()
        self.assertRedirects(r, reverse("order_success", args=[order.pk]))
        self.assertEqual(order.total, 878)
        self.assertEqual(order.items.get().quantity, 2)
        self.assertContains(self.client.get(reverse("cart")), "порожній")

    def test_success_page_is_private(self):
        order = Order.objects.create(name="x", phone="1", city="c", address="a")
        r = self.client.get(reverse("order_success", args=[order.pk]))
        self.assertRedirects(r, reverse("index"))
