from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("catalog/", views.catalog, name="catalog"),
    path("catalog/<slug:slug>/", views.catalog, name="catalog_category"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),

    path("cart/", views.cart_detail, name="cart"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:pk>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("order/<int:pk>/success/", views.order_success, name="order_success"),

    path("about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    path("delivery/", TemplateView.as_view(template_name="pages/delivery.html"), name="delivery"),
    path("returns/", TemplateView.as_view(template_name="pages/returns.html"), name="returns"),
    path("contacts/", TemplateView.as_view(template_name="pages/contacts.html"), name="contacts"),
]
