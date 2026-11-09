from decimal import Decimal

from django.core.management.base import BaseCommand

from internet_store.models import Category, Product

CATEGORIES = [
    # slug, name, emoji, order
    ("spalnya", "Спальня", "🛏️", 1),
    ("kukhnya", "Кухня", "🍽️", 2),
]

PRODUCTS = [
    # category, slug, name, emoji, price, old_price, is_hit
    ("spalnya", "podushka-comfort", "Подушка Comfort", "🛌", "439", None, True),
    ("spalnya", "kovdra-zyma", "Ковдра «Зима»", "🧸", "1290", "1790", True),
    ("spalnya", "kovdra-lito", "Ковдра «Літо»", "☁️", "790", "990", False),
    ("kukhnya", "nabir-garnkiv", "Набір каструль", "🍲", "2490", None, True),
]


class Command(BaseCommand):
    help = "Створює демо-категорії та товари (можна запускати повторно)."

    def handle(self, *args, **options):
        cats = {}
        for slug, name, emoji, order in CATEGORIES:
            cats[slug], _ = Category.objects.get_or_create(
                slug=slug, defaults={"name": name, "emoji": emoji, "order": order})
        for cat, slug, name, emoji, price, old, hit in PRODUCTS:
            Product.objects.get_or_create(slug=slug, defaults={
                "category": cats[cat], "name": name, "emoji": emoji,
                "price": Decimal(price), "old_price": Decimal(old) if old else None,
                "is_hit": hit, "description": f"{name} — демо-товар.",
            })
        self.stdout.write(self.style.SUCCESS("Готово"))
