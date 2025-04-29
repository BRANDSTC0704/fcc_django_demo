# forms.py
from django import forms

class DateRangeForm(forms.Form):
    """Form for filtering dates for dashboard display.  

    Args:
        forms (django.forms.Form): Subclass from Django form. 
    """
    start_date = forms.DateField(
        label='Anfangsdatum', 
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d']
    )
    end_date = forms.DateField(
        label='Enddatum', 
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d']
    )