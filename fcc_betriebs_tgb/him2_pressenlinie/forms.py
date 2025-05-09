from django import forms
from django.forms import formset_factory
from .models import KuebelEintrag, KuebelSession

class KuebelSessionForm(forms.ModelForm):
    """Session Form including user name and comments; timestamp and user-name from login are saved in background. 

    Args:
        forms (django.forms.ModelForm): a modelform object. 
    """
    
    class Meta:
        model = KuebelSession
        fields = ['mitarbeiter', 'comments']
        # exclude = ['created_at']
        widgets = {
            'comments': forms.Textarea(attrs={
                'rows': 2,         # Smaller height
                'class': 'form-control small-textarea',  # For CSS control
                'style': 'resize: vertical;'  # Optional: restrict resizing
            }),
            'mitarbeiter': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }

class KuebelEintragForm(forms.Form):
    """Detailed 

    Args:
        forms (_type_): _description_
    """

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

