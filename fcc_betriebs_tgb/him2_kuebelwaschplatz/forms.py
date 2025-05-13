from django import forms
from django.forms import formset_factory
from .models import KuebelEintrag, KuebelSession
from him2_referenzdaten.models import Betankung, Mitarbeiter, Fahrzeug
from .validators import validate_time
from datetime import datetime, time, timedelta

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
    
    from datetime import time, timedelta

    def generate_time_choices(start="00:00", end="24:00", interval_minutes=15):
        start_h, start_m = map(int, start.split(":"))
        end_h, end_m = map(int, end.split(":"))
        current = time(start_h, start_m)
        end_time = time(end_h-1, end_m)

        choices = []
        while current <= end_time:
            label = current.strftime("%H:%M")
            choices.append((label, label))
            # advance time
            dt = timedelta(hours=current.hour, minutes=current.minute) + timedelta(minutes=interval_minutes)
            current = (dt.seconds // 3600, (dt.seconds % 3600) // 60)
            current = time(*current)

        return choices

    amount_fuel = forms.FloatField(required=False, initial=0, min_value=0, widget=forms.NumberInput(attrs={'step': '0.1'}))
    fahrzeug = forms.ModelChoiceField(
        queryset=Fahrzeug.objects.all(), 
        required=False
    )
    
    TIME_CHOICES = generate_time_choices()

    start_time = forms.ChoiceField(choices=TIME_CHOICES, label="Startzeit", initial='06:00', localize=True, validators=[validate_time], required=False)
    end_time = forms.ChoiceField(choices=TIME_CHOICES, label="Endzeit", initial='06:00', localize=True, validators=[validate_time], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fahrzeug'].queryset = Fahrzeug.objects.all()
        self.fields['amount_fuel'].empty_label = "getankte Menge"
        
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        # Debug: print the values of start and end to see what's being passed
        # print(f"start_time: {start}, end_time: {end}")

        # Only validate if both start_time and end_time are not empty
        if start and end:  
            # Convert string times to datetime objects
            start_time_obj = datetime.strptime(start, "%H:%M").time()
            end_time_obj = datetime.strptime(end, "%H:%M").time()

            if end_time_obj < start_time_obj:
                self.add_error("end_time", "Endzeit muss nach oder bei der Startzeit liegen.")

        elif start and not end:
            self.add_error("end_time", "Endzeit ist erforderlich, wenn Startzeit angegeben ist.")
        elif not start and end:
            self.add_error("start_time", "Startzeit ist erforderlich, wenn Endzeit angegeben ist.")

        print('CLEANED DATA: ', cleaned_data)
        return cleaned_data

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

