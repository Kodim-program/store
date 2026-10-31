from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Order, OrderItem, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "order", "in_menu")
    list_editable = ("order", "in_menu")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("preview", "name", "category", "price", "old_price", "is_hit", "is_active")
    list_display_links = ("preview", "name")
    readonly_fields = ("preview",)

    @admin.display(description="Фото")
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:48px;border-radius:6px">', obj.image.url)
        return "—"

    list_filter = ("category", "is_hit", "is_active")
    list_editable = ("price", "old_price", "is_hit", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "price", "quantity")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "city", "total", "status", "created")
    list_filter = ("status", "created")
    list_editable = ("status",)
    search_fields = ("name", "phone", "email")
    inlines = [OrderItemInline]
