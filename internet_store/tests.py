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


class ProductImageTests(TestCase):
    def test_upload_is_converted_to_webp_in_static_images(self):
        from io import BytesIO
        from pathlib import Path

        from django.conf import settings
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image

        from .models import Category

        buf = BytesIO()
        Image.new("RGB", (2000, 1000), "red").save(buf, format="PNG")
        cat = Category.objects.create(name="Тест", slug="test-cat")
        p = Product.objects.create(
            category=cat, name="Фото", slug="photo-test", price=10,
            image=SimpleUploadedFile("big.png", buf.getvalue(), content_type="image/png"),
        )
        try:
            self.assertTrue(p.image.name.endswith(".webp"))
            path = Path(settings.PRODUCT_IMAGES_DIR) / p.image.name
            self.assertTrue(path.exists())
            with Image.open(path) as im:
                self.assertEqual(im.format, "WEBP")
                self.assertLessEqual(max(im.size), 1200)
            self.assertTrue(p.image.url.startswith("/static/images/"))
            self.assertContains(self.client.get(p.get_absolute_url()), p.image.url)
            self.assertEqual(self.client.get(p.image.url).status_code, 200)
        finally:
            p.delete()
        self.assertFalse(path.exists())
