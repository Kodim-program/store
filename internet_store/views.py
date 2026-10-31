from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CheckoutForm
from .models import Category, Order, OrderItem, Product

PAGE_SIZE = 12


def index(request):
    hits = Product.objects.filter(is_active=True, is_hit=True).select_related("category")
    sub_ids = hits.values_list("category_id", flat=True)
    tabs = Category.objects.filter(pk__in=sub_ids)
    tab = request.GET.get("tab")
    if tab:
        hits = hits.filter(category__slug=tab)
    return render(request, "index.html", {
        "hits": hits[:8],
        "tabs": tabs,
        "active_tab": tab,
        "tiles": Category.objects.filter(parent__isnull=True),
    })


def catalog(request, slug=None):
    products = Product.objects.filter(is_active=True).select_related("category")
    category = None
    title = "Усі товари"
    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = products.filter(category_id__in=category.with_children_ids())
        title = category.name
    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
        title = f"Пошук: {q}"
    if request.GET.get("sale"):
        products = products.filter(old_price__gt=F("price"))
        title = "SALE"
    sort = request.GET.get("sort", "")
    products = {
        "price": products.order_by("price"),
        "-price": products.order_by("-price"),
    }.get(sort, products)
    page = Paginator(products, PAGE_SIZE).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "catalog.html", {
        "category": category,
        "title": title,
        "page": page,
        "q": q,
        "sort": sort,
        "querystring": params.urlencode(),
        "subcategories": category.children.all() if category else Category.objects.filter(parent__isnull=True),
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    return render(request, "product_detail.html", {"product": product, "related": related})


def _back(request, fallback="cart"):
    nxt = request.POST.get("next", "")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return redirect(nxt)
    return redirect(fallback)


def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart.html", {"items": list(cart.items()), "total": cart.total})


@require_POST
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    try:
        qty = max(1, int(request.POST.get("quantity", 1)))
    except ValueError:
        qty = 1
    Cart(request).add(product, qty)
    messages.success(request, f"«{product.name}» додано до кошика")
    return _back(request)


@require_POST
def cart_update(request, pk):
    try:
        qty = int(request.POST.get("quantity", 1))
    except ValueError:
        qty = 1
    Cart(request).set(pk, qty)
    return redirect("cart")


@require_POST
def cart_remove(request, pk):
    Cart(request).remove(pk)
    return redirect("cart")


def checkout(request):
    cart = Cart(request)
    items = list(cart.items())
    if not items:
        messages.info(request, "Кошик порожній")
        return redirect("catalog")
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            order = form.save(commit=False)
            order.total = sum(i["subtotal"] for i in items)
            order.save()
            OrderItem.objects.bulk_create([
                OrderItem(order=order, product=i["product"], product_name=i["product"].name,
                          price=i["product"].price, quantity=i["quantity"])
                for i in items
            ])
        cart.clear()
        request.session["last_order"] = order.pk
        return redirect("order_success", pk=order.pk)
    return render(request, "checkout.html", {"form": form, "items": items, "total": cart.total})


def order_success(request, pk):
    # показуємо лише власне замовлення з поточної сесії
    if request.session.get("last_order") != pk:
        return redirect("index")
    order = get_object_or_404(Order, pk=pk)
    return render(request, "order_success.html", {"order": order})
