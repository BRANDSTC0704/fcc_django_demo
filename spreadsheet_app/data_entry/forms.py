from django import forms
from .models import Employee, WorkCategory, WorkHours, ContainerCount, Protocollist
from .validators import validate_time

valid_time_formats = ["%H:%M"]


class CommaFloatField(forms.DecimalField):
    def to_python(self, value):
        """Convert comma to dot before Django processes the field."""
        if value in self.empty_values:
            return None
        if isinstance(value, str):
            value = value.replace(",", ".").strip()
        return super().to_python(value)

    def prepare_value(self, value):
        """Ensure values are displayed with a comma in the form."""
        if isinstance(value, float):
            return str(value).replace(".", ",")
        return value


class EmployeeForm(forms.ModelForm):
    work_start = forms.TimeField(
        widget=forms.TimeInput(format="%H:%M", attrs={"type": "time", "step": "60"}),
        initial="06:00",
        localize=True,
        validators=[
            validate_time,
        ],
    )
    work_end = forms.TimeField(
        widget=forms.TimeInput(format="%H:%M", attrs={"type": "time", "step": "60"}),
        initial="14:30",
        localize=True,
        validators=[
            validate_time,
        ],
    )
    break_time = CommaFloatField(
        decimal_places=1,
        localize=True,
        initial="0.5",
        required=False,
        widget=forms.NumberInput(
            attrs={
                "style": "width: 50px; text-align: center;",
                "step": "0.1",  # Allows decimals like 4.5, 3.0, etc.
                "min": "0",
            }
        ),
    )
    attribut = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"style": "width:80px"})
    )

    class Meta:
        model = Employee
        fields = [
            "first_name",
            "surname",
            "attribut",
            "work_start",
            "work_end",
            "break_time",
            "absence",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "rows": 1,
                    "cols": 10,
                    "style": "width:80px",
                    "required": "required",
                }
            ),
            "surname": forms.TextInput(
                attrs={
                    "rows": 1,
                    "cols": 10,
                    "style": "width:80px",
                    "required": "required",
                }
            ),
            "absence": forms.TextInput(
                attrs={"rows": 1, "cols": 20, "style": "width:200px"}
            ),
        }
        localized_fields = ["break_time"]
        help_texts = {"break_time": "Sollte nun funktionieren mit deutschem Komma."}

    def __init__(self, *args, **kwargs):
        """Ensure break_time is displayed with a comma when editing."""
        super().__init__(*args, **kwargs)
        if "break_time" in self.initial and isinstance(
            self.initial["break_time"], (float, int)
        ):
            self.initial["break_time"] = str(self.initial["break_time"]).replace(
                ".", ","
            )


class WorkCategoryForm(forms.ModelForm):
    cleaning = CommaFloatField(
        decimal_places=1,
        localize=True,
        initial=0,
        widget=forms.NumberInput(
            attrs={
                "style": "width: 100px; text-align: center;",
                "step": "0.1",  # Allows decimals like 4.5, 3.0, etc.
                "min": "0",
            }
        ),
    )
    maintenance = CommaFloatField(
        decimal_places=1,
        localize=True,
        initial=0,
        widget=forms.NumberInput(
            attrs={
                "style": "width: 100px; text-align: center;",
                "step": "0.1",  # Allows decimals like 4.5, 3.0, etc.
                "min": "0",
            }
        ),
    )
    interruption = CommaFloatField(
        decimal_places=1,
        localize=True,
        initial=0,
        widget=forms.NumberInput(
            attrs={
                "style": "width: 100px; text-align: center;",
                "step": "0.1",  # Allows decimals like 4.5, 3.0, etc.
                "min": "0",
            }
        ),
    )

    class Meta:
        model = WorkCategory
        fields = ["cleaning", "maintenance", "interruption"]


class WorkHoursForm(forms.ModelForm):
    start_time = forms.TimeField(
        widget=forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
        initial="00:00",
        validators=[
            validate_time,
        ],
        error_messages={validate_time: "Keine gültige Zeit!"},
        input_formats=valid_time_formats,
        localize=True,
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
        initial="00:00",
        validators=[
            validate_time,
        ],
        localize=True,
    )

    class Meta:
        model = WorkHours
        fields = ["start_time", "end_time"]
        widgets = {
            "start_time": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
            "end_time": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
        }


class ContainerCountForm(forms.ModelForm):
    class Meta:
        model = ContainerCount
        fields = ["alu", "holz", "karton", "magnetschrott", "kanister"]
        widgets = {
            field: forms.NumberInput(
                attrs={
                    "min": "0",
                    "oninvalid": "this.setCustomValidity('Bitte eine Zahl >= 0 eingeben')",
                    "oninput": "this.setCustomValidity('')",
                }
            )
            for field in ["alu", "holz", "karton", "magnetschrott", "kanister"]
        }


class ProtocollistForm(forms.ModelForm):
    class Meta:
        model = Protocollist
        fields = ["protocollist"]
        widgets = {
            "protocollist": forms.TextInput(attrs={"style": "width:250px"}),
        }
