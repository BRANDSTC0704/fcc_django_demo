from django import forms
from .models import Employee, WorkCategory, WorkHours, Count, Protocol

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'surname', 'work_start', 'work_end', 'break_time', 'absence']

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

class CountForm(forms.ModelForm):
    category = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),  # Display as text, read-only
        required=True
    )
    count = forms.IntegerField(min_value=0, required=True)

    class Meta:
        model = Count
        fields = ['category', 'count']

class ProtocolForm(forms.ModelForm):
    class Meta:
        model = Protocol
        fields = ['protocollist']
