from django import forms
from .models import Employee, WorkCategory, WorkHours, ContainerCount, Protocollist

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'surname', 'work_start', 'work_end', 'break_time', 'absence']
        widgets = {
          'absence': forms.Textarea(attrs={'rows':3, 'cols':15}),
        }

    work_start = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    work_end = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))

class WorkCategoryForm(forms.ModelForm):
    class Meta:
        model = WorkCategory
        fields = ['cleaning', 'maintenance', 'interruption']

class WorkHoursForm(forms.ModelForm):
    class Meta:
        model = WorkHours
        fields = ['start_time', 'end_time']

    start_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    end_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))

class ContainerCountForm(forms.ModelForm):
    class Meta:
        model = ContainerCount
        fields = ['alu', 'holz', 'karton', 'magnetschrott', 'kanister']

class ProtocolForm(forms.ModelForm):
    class Meta:
        model = Protocollist
        fields = ['protocollist']
        widgets = {
          'protocollist': forms.Textarea(attrs={'rows':1, 'cols':50}),
        }
