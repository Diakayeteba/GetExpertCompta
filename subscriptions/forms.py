from django import forms
from payments.models import PaymentTransaction
from subscriptions.models import Plan


class DemoSubscriptionForm(forms.Form):
    plan = forms.ModelChoiceField(
        queryset=Plan.objects.none(),
        label="Formule",
        widget=forms.Select(attrs={"class": "form-select form-select-lg"}),
    )
    provider = forms.ChoiceField(
        label="Moyen de paiement",
        choices=[
            (PaymentTransaction.Provider.ORANGE_MONEY, "Orange Money"),
            (PaymentTransaction.Provider.WAVE, "Wave"),
            (PaymentTransaction.Provider.MALITEL_MONEY, "Malitel Money"),
        ],
        widget=forms.Select(attrs={"class": "form-select form-select-lg"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["plan"].queryset = Plan.objects.filter(is_active=True).order_by("amount_cents")
