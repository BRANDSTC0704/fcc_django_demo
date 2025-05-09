from django import forms
from django.forms import formset_factory
from .models import KuebelEintrag, KuebelSession
from him2_referenzdaten.models import Betankung, Mitarbeiter, Fahrzeug

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
                'cols': 40,        # Optional width
                'class': 'form-control small-textarea',  # For CSS control
                'style': 'resize: vertical;'  # Optional: restrict resizing
            }),
            'mitarbeiter': forms.Select(attrs={'class': 'form-control'}) 
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mitarbeiter'].queryset = Mitarbeiter.objects.all()
        self.fields['mitarbeiter'].empty_label = "Mitarbeiter auswählen"

class BetankungForm(forms.ModelForm):
    """Form including Fahrzeug-Info und Betankung. 
    
    fahrzeug = models.ForeignKey(Mitarbeiter, verbose_name='Fahrzeug', blank=False, null=False, on_delete=models.PROTECT)
    daten_eingabe_von = models.CharField(max_length=40) # die jeweilige App - muss beim Anlegen hard kodiert werden
    created_at = models.DateField(auto_now_add=True, editable=False, null=False, blank=False)
    amount_fuel = models.FloatField(default=0, validators=[MinValueValidator(0)])

    Args:
        forms (django.forms.ModelForm): a modelform object. 
    """
    
    class Meta:
        model = Betankung
        fields = ['fahrzeug', 'amount_fuel']
        # exclude = ['created_at']
        widgets = {
            'fahrzeug': forms.Select(attrs={'class': 'form-control'}) 
        }
    
    amount_fuel = forms.FloatField(required=False, initial=0, min_value=0, widget=forms.NumberInput(attrs={'step': '0.1'}))
    fahrzeug = forms.ModelChoiceField(
        queryset=Fahrzeug.objects.all(), 
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fahrzeug'].queryset = Fahrzeug.objects.all()
        self.fields['amount_fuel'].empty_label = "getankte Menge"


class KuebelEintragForm(forms.Form):
    """Detaillierte Aktivitätsaufzeichnung Kübelwaschplatz.  

    Args:
        forms (Form): Subclass von Form. 
    """

    class Meta:
        model = KuebelEintrag
        
    kuebel_art = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'infofield'}))
    # sonstiges_h = forms.FloatField(required=False, initial=0, min_value=0,  widget=forms.NumberInput(attrs={'step': '0.25'}))
    # Rückmeldung Franz: kann weg 
    reinigung_h = forms.FloatField(required=False, initial=0, min_value=0, widget=forms.NumberInput(attrs={'step': '0.25'}))
    waschen_h = forms.FloatField(required=False, initial=0, min_value=0, widget=forms.NumberInput(attrs={'step': '0.25'}))
    waschen_count = forms.IntegerField(required=False, initial=0, min_value=0)
    instandh_h = forms.FloatField(required=False, initial=0, min_value=0, widget=forms.NumberInput(attrs={'step': '0.25'}))
    instandh_count = forms.IntegerField(required=False, initial=0, min_value=0)
    zerlegen_h = forms.FloatField(required=False, initial=0, min_value=0, widget=forms.NumberInput(attrs={'step': '0.25'}))
    zerlegen_count = forms.IntegerField(required=False, initial=0, min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kuebel_art'].widget.attrs['readonly'] = True  # 👈 makes it read-only


KuebelEintragFormSet = formset_factory(KuebelEintragForm, extra=0)  # allow 0 rows by default

