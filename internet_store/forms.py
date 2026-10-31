from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["name", "phone", "email", "city", "address", "comment"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ім'я та прізвище", "autocomplete": "name"}),
            "phone": forms.TextInput(attrs={"placeholder": "+380...", "autocomplete": "tel", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email (необов'язково)", "autocomplete": "email"}),
            "city": forms.TextInput(attrs={"placeholder": "Місто"}),
            "address": forms.TextInput(attrs={"placeholder": "Відділення Нової пошти або адреса"}),
            "comment": forms.Textarea(attrs={"placeholder": "Коментар до замовлення", "rows": 3}),
        }
