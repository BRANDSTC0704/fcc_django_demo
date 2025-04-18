from django import forms
from django.forms import formset_factory
from .models import KuebelEintrag

class KuebelSessionForm(forms.Form):
    name = forms.CharField(required=True)
    comments = forms.CharField()

class KuebelEintragForm(forms.Form):

    class Meta:
        model = KuebelEintrag
        
    kuebel_art = forms.CharField(required=True)
    waschen_h = forms.FloatField()
    waschen_count = forms.IntegerField()
    instandh_h = forms.FloatField()
    instandh_count = forms.IntegerField()
    zerlegen_h = forms.FloatField()
    zerlegen_count = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kuebel_art'].disabled = True  # 👈 makes it read-only


KuebelEintragFormSet = formset_factory(KuebelEintragForm, extra=0)  # allow 3 rows by default

