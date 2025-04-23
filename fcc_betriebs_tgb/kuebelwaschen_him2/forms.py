from django import forms
from django.forms import formset_factory
from .models import KuebelEintrag

class KuebelSessionForm(forms.Form):
    name = forms.CharField(required=True)
    comments = forms.CharField(required=False)

class KuebelEintragForm(forms.Form):

    class Meta:
        model = KuebelEintrag
        
    kuebel_art = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'infofield'}))
    sonstiges_h = forms.FloatField(required=False, initial=0, min_value=0,  widget=forms.NumberInput(attrs={'step': '0.1'}))
    reinigung_h = forms.FloatField(required=False, initial=0, min_value=0, widget=forms.NumberInput(attrs={'step': '0.1'}))
    waschen_h = forms.FloatField(required=False, initial=0, min_value=0, widget=forms.NumberInput(attrs={'step': '0.1'}))
    waschen_count = forms.IntegerField(required=False, initial=0, min_value=0)
    instandh_h = forms.FloatField(required=False, initial=0, min_value=0, widget=forms.NumberInput(attrs={'step': '0.1'}))
    instandh_count = forms.IntegerField(required=False, initial=0, min_value=0)
    zerlegen_h = forms.FloatField(required=False, initial=0, min_value=0, widget=forms.NumberInput(attrs={'step': '0.1'}))
    zerlegen_count = forms.IntegerField(required=False, initial=0, min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kuebel_art'].widget.attrs['readonly'] = True  # 👈 makes it read-only


KuebelEintragFormSet = formset_factory(KuebelEintragForm, extra=0)  # allow 0 rows by default

