from django import forms
from django.forms import formset_factory


# forms.py
class BetankungRowForm(forms.Form):
    fahrzeug_id = forms.IntegerField(widget=forms.HiddenInput)
    fahrzeug_name = forms.CharField(
        disabled=True,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "wide-field",  # define in your CSS
                "style": "width: 200px;",  # or directly use inline style
            }
        ),
    )

    amount_fuel = forms.FloatField(min_value=0, required=False)

    laufzeit_hour = forms.ChoiceField(
        choices=[(f"{i:02d}", f"{i:02d}") for i in range(24)],
        label="Stunde",
        required=False,
    )
    laufzeit_minute = forms.ChoiceField(
        choices=[(f"{i:02d}", f"{i:02d}") for i in range(0, 60, 15)],
        label="Minute",
        required=False,
    )


BetankungFormSet = formset_factory(BetankungRowForm, extra=0)
