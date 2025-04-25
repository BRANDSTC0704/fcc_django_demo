from django import forms
from django.forms import formset_factory
from .models import KuebelEintrag, KuebelSession

class KuebelSessionForm(forms.ModelForm):
    # name = forms.CharField(required=True)
    # comments = forms.CharField(required=False)
    
    class Meta:
        model = KuebelSession
        fields = ['name', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={
                'rows': 2,         # Smaller height
                'cols': 40,        # Optional width
                'class': 'form-control small-textarea',  # For CSS control
                'style': 'resize: vertical;'  # Optional: restrict resizing
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }

class KuebelEintragForm(forms.Form):

    class Meta:
        model = KuebelEintrag
        
    kuebel_art = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'infofield'}))
    sonstiges_h = forms.FloatField(required=False, initial=0, min_value=0,  widget=forms.NumberInput(attrs={'step': '0.5'}))
    reinigung_h = forms.FloatField(required=False, initial=0, min_value=0, widget=forms.NumberInput(attrs={'step': '0.5'}))
    waschen_h = forms.FloatField(required=False, initial=0, min_value=0, widget=forms.NumberInput(attrs={'step': '0.5'}))
    waschen_count = forms.IntegerField(required=False, initial=0, min_value=0)
    instandh_h = forms.FloatField(required=False, initial=0, min_value=0, widget=forms.NumberInput(attrs={'step': '0.5'}))
    instandh_count = forms.IntegerField(required=False, initial=0, min_value=0)
    zerlegen_h = forms.FloatField(required=False, initial=0, min_value=0, widget=forms.NumberInput(attrs={'step': '0.5'}))
    zerlegen_count = forms.IntegerField(required=False, initial=0, min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kuebel_art'].widget.attrs['readonly'] = True  # 👈 makes it read-only


KuebelEintragFormSet = formset_factory(KuebelEintragForm, extra=0)  # allow 0 rows by default

