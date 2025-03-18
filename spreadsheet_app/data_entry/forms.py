from django import forms
from django.forms import modelformset_factory
from .models import Employee, WorkCategory, WorkHours, ContainerCount, Protocollist
from .validators import validate_time

valid_time_formats = ['%H:%M']


class CommaFloatField(forms.DecimalField):
    def to_python(self, value):
        """Convert comma to dot before Django processes the field."""
        if value in self.empty_values:
            return None
        if isinstance(value, str):
            value = value.replace(',', '.').strip()
        return super().to_python(value)
    
    def prepare_value(self, value):
        """Ensure values are displayed with a comma in the form."""
        if isinstance(value, float):
            return str(value).replace('.', ',')
        return value
    
class EmployeeForm(forms.ModelForm):
    work_start = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}), initial='08:00', localize=True, validators=[validate_time,])
    work_end = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}), initial='17:00', localize=True, validators=[validate_time,])
    break_time = CommaFloatField(decimal_places=1, localize=True, initial="0,5")

    class Meta:
        model = Employee
        fields = ['first_name', 'surname', 'work_start', 'work_end', 'break_time', 'absence']
        widgets = {
            'absence': forms.Textarea(attrs={'rows': 1, 'cols': 20}),
        }
        localized_fields = ['break_time']
        help_texts = {'break_time': 'Sollte nun funktionieren mit deutschem Komma.'}

    def __init__(self, *args, **kwargs):
        """Ensure break_time is displayed with a comma when editing."""
        super().__init__(*args, **kwargs)
        if 'break_time' in self.initial and isinstance(self.initial['break_time'], (float, int)):
            self.initial['break_time'] = str(self.initial['break_time']).replace('.', ',')


EmployeeFormset = modelformset_factory(Employee, form=EmployeeForm, extra=1, can_delete=True, 
                                       help_texts={'break_time': 'Sollte nun funktionieren mit deutschem Komma.'})
# EmployeeFormset_empty = modelformset_factory(queryset=Employee.objects.none(), extra=0, can_delete=True)

class WorkCategoryForm(forms.ModelForm):
    class Meta:
        model = WorkCategory
        fields = ['cleaning', 'maintenance', 'interruption']
        cleaning = forms.DecimalField(decimal_places=1, localize=True)
        maintenance = forms.DecimalField(decimal_places=1, localize=True)
        interruption = forms.DecimalField(decimal_places=1, localize=True)

class WorkHoursForm(forms.ModelForm):

    start_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}), initial='00:00', validators=[validate_time,], 
                                 error_messages={validate_time: 'Keine gültige Zeit!'}, input_formats=valid_time_formats)
    end_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}), initial='00:00', validators=[validate_time,])

    class Meta:
        model = WorkHours
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(format='%M:%S', attrs={'type': 'time'}),
            'end_time': forms.TimeInput(format='%M:%S', attrs={'type': 'time'}),
        }


class ContainerCountForm(forms.ModelForm):
    class Meta:
        model = ContainerCount
        fields = ['alu', 'holz', 'karton', 'magnetschrott', 'kanister']

class ProtocollistForm(forms.ModelForm):
    class Meta:
        model = Protocollist
        fields = ['protocollist']
        widgets = {
            'protocollist': forms.Textarea(attrs={
                'rows': '1', 
                'cols': '50',                
            }),
        }
