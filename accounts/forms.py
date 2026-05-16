from allauth.account.forms import LoginForm as AllauthLoginForm
from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class LoginForm(AllauthLoginForm):
    """Connexion avec champs stylés Bootstrap."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, forms.CheckboxInput):
                w.attrs.setdefault("class", "form-check-input")
            else:
                w.attrs.setdefault("class", "form-control form-control-lg")
            if name == "password":
                field.help_text = ""


class RoleSignupForm(SignupForm):
    role = forms.ChoiceField(
        label=_("Type de compte"),
        choices=[
            (User.Role.BUSINESS, _("Entreprise")),
            (User.Role.EXPERT, _("Expert-comptable")),
        ],
        initial=User.Role.BUSINESS,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ctrl = "form-control form-control-lg"
        sel = "form-select form-select-lg"
        for name, field in self.fields.items():
            w = field.widget
            classes = sel if isinstance(w, forms.Select) else ctrl
            w.attrs.setdefault("class", classes)
            if name in ("password1", "password2"):
                field.help_text = ""
                w.attrs.setdefault("autocomplete", "new-password")
            if name == "email":
                w.attrs.setdefault("autocomplete", "email")
                w.attrs.setdefault("inputmode", "email")
