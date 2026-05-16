from django import forms

from experts.models import ExpertProfile


class ExpertAvailabilityForm(forms.ModelForm):
    class Meta:
        model = ExpertProfile
        fields = ("availability",)
        widgets = {
            "availability": forms.RadioSelect(attrs={"class": "form-check-input"}),
        }
