from django import forms
from django.forms import formset_factory
# from .models import KuebelEintrag

class KuebelSessionForm(forms.Form):
    name = forms.CharField()
    comments = forms.CharField(widget=forms.Textarea, required=False)

class KuebelEintragForm(forms.Form):
    kuebel_art = forms.CharField()
    waschen_h = forms.FloatField()
    waschen_count = forms.IntegerField()
    instandh_h = forms.FloatField()
    instandh_count = forms.IntegerField()
    zerlegen_h = forms.FloatField()
    zerlegen_count = forms.IntegerField()

KuebelEintragFormSet = formset_factory(KuebelEintragForm)  # allow 3 rows by default
