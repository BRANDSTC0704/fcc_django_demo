from django import forms
from django.forms import formset_factory
from .models import ZeitAktivitaetTyp, StundenEingabeSession, StundenEingabeDetails, Aktivitaet, AbhProdTyp, Produktion, SchichtEingabeMitarbeiter
from him2_referenzdaten.models import PresseBallenTyp, Schicht, Fahrzeug, Mitarbeiter, Betankung


class PresseZeitSessionForm(forms.ModelForm):
    """Static entries into activity table; Schicht (rows) and activities (additional columns) are built 
    in views.pdf. 

    Args:
        forms (forms.ModelForm): Django Form class. 
    """
    class Meta:
        model = StundenEingabeSession
        fields = ['created_date_mitarbeiter', 'comments']
        labels = {
            'created_date_mitarbeiter': 'Datum', 'comments': 'Anmerkung'
        }
        widgets = {
            'created_date_mitarbeiter': forms.SelectDateWidget(attrs={'label': 'Datum'}),  # date dropdown
            "comments": forms.TextInput(attrs={"style": "width:250px"}),
        }


class PresseStundenEingabeForm(forms.Form):
    """Dynamically generated form for time entries based on available shifts and activity types."""

    def __init__(self, *args, **kwargs):
        schichten = kwargs.pop('schichten')
        zeittypen = kwargs.pop('zeittypen')
        super(PresseStundenEingabeForm, self).__init__(*args, **kwargs)
        

        # Dynamically add fields for each shift and activity type combination
        for schicht in schichten:
            self.fields[f"schicht_mitarbeiter_1_{schicht.id}"] = forms.ModelChoiceField(
                    queryset=Mitarbeiter.objects.all(),
                    label=f"Schicht Mitarbeiter 1 ({schicht.name})",
                    required=True
                )
            self.fields[f"schicht_mitarbeiter_2_{schicht.id}"] = forms.ModelChoiceField(
                    queryset=Mitarbeiter.objects.all(),
                    label=f"Schicht Mitarbeiter 2 ({schicht.name})",
                    required=True
                )
           
            for zeittyp in zeittypen:
                # Add the shift worker fields
           
                # Add the duration field
                self.fields[f"entry_{schicht.id}_{zeittyp.id}"] = forms.FloatField(
                    label=f"Duration ({schicht.name} - {zeittyp})",
                    widget=forms.NumberInput(attrs={'step': '0.25', 'class': 'form-control'}),
                    required=True
                )
        
        print("Dynamic fields:", list(self.fields.keys()))

    def save(self, session):
        """Save the form data to the StundeneingabeDetails model."""
        schichten = session.schichten.all()
        zeittypen = session.zeittypen.all()
        
        for schicht in schichten:
            schicht_mitarbeiter_1 = self.cleaned_data.get(f"schicht_mitarbeiter_1_{schicht.id}")
            schicht_mitarbeiter_2 = self.cleaned_data.get(f"schicht_mitarbeiter_2_{schicht.id}")
            
            # Check if both Mitarbeiter (workers) are selected
            if schicht_mitarbeiter_1 and schicht_mitarbeiter_2:
                for zeittyp in zeittypen:
                    field_name = f"entry_{schicht.id}_{zeittyp.id}"
                    dauer = self.cleaned_data.get(field_name)

                    # Check if duration (dauer) is provided
                    if dauer is not None:
                        # Create the time entry detail record
                        StundenEingabeDetails.objects.create(
                            session=session,
                            schicht=schicht,
                            zeittyp=zeittyp,
                            dauer=dauer,
                        )

                # Create the worker entry record if both Mitarbeiter are valid
                SchichtEingabeMitarbeiter.objects.create(
                    session=session,
                    schicht=schicht,
                    mitarbeiter_1=schicht_mitarbeiter_1,
                    mitarbeiter_2=schicht_mitarbeiter_2
                )