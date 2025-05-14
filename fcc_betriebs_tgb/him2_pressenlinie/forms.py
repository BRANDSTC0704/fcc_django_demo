from django import forms
from django.forms import formset_factory
from .models import (
    ZeitAktivitaetTyp,
    StundenEingabeSession,
    StundenEingabeDetails,
    Aktivitaet,
    AbhProdTyp,
    Produktion,
    SchichtEingabeMitarbeiter,
)
from him2_referenzdaten.models import (
    PresseBallenTyp,
    Schicht,
    Fahrzeug,
    Mitarbeiter,
    Betankung,
)
import datetime
from django.forms import Select


class PresseZeitSessionForm(forms.ModelForm):
    """Static entries into activity table; Schicht (rows) and activities (additional columns) are built
    in views.pdf.

    Args:
        forms (forms.ModelForm): Django Form class.
    """

    # defaults current day
    created_date_mitarbeiter = forms.DateField(
        initial=datetime.date.today, widget=forms.SelectDateWidget()
    )

    class Meta:
        model = StundenEingabeSession
        fields = ["created_date_mitarbeiter", "comments"]
        labels = {"created_date_mitarbeiter": "Datum", "comments": "Anmerkung"}
        help_texts = {
            "created_date_mitarbeiter": ("vom Mitarbeiter erstelles Datum. "),
            "comments": ("Allgemeine Auffälligkeiten. "),
        }
        widgets = {
            "comments": forms.TextInput(attrs={"style": "width:250px"}),
        }


class PresseStundenEingabeForm(forms.Form):
    """Dynamically generated form for time entries based on available shifts and activity types."""

    def __init__(self, *args, **kwargs):

        schichten = kwargs.pop("schichten")
        zeittypen = kwargs.pop("zeittypen")
        super(PresseStundenEingabeForm, self).__init__(*args, **kwargs)

        # Dynamically add fields for each shift and activity type combination
        mitarbeiter_widget_style = {"style": "max-width:150px; margin: 2px 6px;"}

        for schicht in schichten:
            self.fields[f"schicht_mitarbeiter_1_{schicht.id}"] = forms.ModelChoiceField(
                queryset=Mitarbeiter.objects.all(),
                label=f"Schicht Mitarbeiter 1 ({schicht.name})",
                required=True,
                widget=Select(attrs=mitarbeiter_widget_style),
            )
            self.fields[f"schicht_mitarbeiter_2_{schicht.id}"] = forms.ModelChoiceField(
                queryset=Mitarbeiter.objects.all(),
                label=f"Schicht Mitarbeiter 2 ({schicht.name})",
                required=True,
                widget=Select(attrs=mitarbeiter_widget_style),
            )

            for zeittyp in zeittypen:
                # Add the shift worker fields

                # Add the duration field
                self.fields[f"entry_{schicht.id}_{zeittyp.id}"] = forms.FloatField(
                    label=f"Duration ({schicht.name} - {zeittyp})",
                    initial=0,
                    widget=forms.NumberInput(
                        attrs={"step": "0.25", "class": "form-control"}
                    ),
                    required=True,
                    min_value=0,
                )

        # print("Dynamic fields:", list(self.fields.keys()))

    def clean(self):
        cleaned_data = super().clean()
        for field in self.fields:
            if field.startswith("schicht_mitarbeiter_1_"):
                schicht_id = field.split("_")[-1]
                m1 = cleaned_data.get(f"schicht_mitarbeiter_1_{schicht_id}")
                m2 = cleaned_data.get(f"schicht_mitarbeiter_2_{schicht_id}")
                if m1 and m2 and m1 == m2:
                    self.add_error(f"schicht_mitarbeiter_2_{schicht_id}", "Die beiden Personen dürfen nicht gleich sein.")


    def save(self, session):
        """Save the form data to the StundeneingabeDetails model."""
        schichten = session.schichten.all()
        zeittypen = session.zeittypen.all()

        for schicht in schichten:
            schicht_mitarbeiter_1 = self.cleaned_data.get(
                f"schicht_mitarbeiter_1_{schicht.id}"
            )
            schicht_mitarbeiter_2 = self.cleaned_data.get(
                f"schicht_mitarbeiter_2_{schicht.id}"
            )

            # Check if both Mitarbeiter (workers) are selected
            if schicht_mitarbeiter_1 and schicht_mitarbeiter_2:

                if schicht_mitarbeiter_1 == schicht_mitarbeiter_2:
                    self.add_error(f"schicht_mitarbeiter_2_{schicht.id}", "Mitarbeiter dürfen nicht gleich sein.")
                
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
                    mitarbeiter_2=schicht_mitarbeiter_2,
                )
