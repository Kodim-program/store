from django.db import models

# Create your models here.
from decimal import Decimal

from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField("Назва", max_length=120)
    slug = models.SlugField("Slug", unique=True)
    emoji = models.CharField("Емодзі", max_length=8, blank=True)
    parent = models.ForeignKey(
        "self", verbose_name="Батьківська категорія", null=True, blank=True,
        on_delete=models.CASCADE, related_name="children",
    )
    order = models.PositiveSmallIntegerField("Порядок", default=0)
    in_menu = models.BooleanField("Показувати в меню", default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalog_category", args=[self.slug])

    def with_children_ids(self):
        return [self.pk, *self.children.values_list("pk", flat=True)]


class Product(models.Model):
    category = models.ForeignKey(
        Category, verbose_name="Категорія", on_delete=models.PROTECT, related_name="products"
    )
    name = models.CharField("Назва", max_length=200)
    slug = models.SlugField("Slug", unique=True)
    image = models.ImageField("Фото", upload_to="products/", blank=True, null=True)
    emoji = models.CharField("Емодзі", max_length=8, blank=True, default="🛍️")
    color = models.CharField("Колір фону картки", max_length=7, default="#e4e6ee")
    description = models.TextField("Опис", blank=True)
    price = models.DecimalField("Ціна", max_digits=10, decimal_places=2)
    old_price = models.DecimalField("Стара ціна", max_digits=10, decimal_places=2, null=True, blank=True)
    reviews_count = models.PositiveIntegerField("Кількість відгуків", default=0)
    is_active = models.BooleanField("Активний", default=True)
    is_hit = models.BooleanField("Хіт продажу", default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created", "name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товари"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.slug])

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((1 - self.price / self.old_price) * 100)
        return 0


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Нове"
        CONFIRMED = "confirmed", "Підтверджене"
        SHIPPED = "shipped", "Відправлене"
        DONE = "done", "Виконане"
        CANCELED = "canceled", "Скасоване"

    name = models.CharField("Ім'я", max_length=120)
    phone = models.CharField("Телефон", max_length=32)
    email = models.EmailField("Email", blank=True)
    city = models.CharField("Місто", max_length=120)
    address = models.CharField("Адреса / відділення", max_length=255)
    comment = models.TextField("Коментар", blank=True)
    status = models.CharField("Статус", max_length=12, choices=Status.choices, default=Status.NEW)
    total = models.DecimalField("Сума", max_digits=12, decimal_places=2, default=Decimal("0"))
    created = models.DateTimeField("Створено", auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"

    def __str__(self):
        return f"Замовлення №{self.pk} — {self.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Позиція замовлення"
        verbose_name_plural = "Позиції замовлення"

    @property
    def subtotal(self):
        return self.price * self.quantity
