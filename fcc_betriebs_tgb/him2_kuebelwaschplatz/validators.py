from django.core.exceptions import ValidationError


def validate_time(value):
    if not value:  # Allow empty values when field is optional
        return

    try:
        stunden, minuten = map(int, str(value).split(":"))
    except (ValueError, AttributeError):
        raise ValidationError("Ungültiges Zeitformat! (Erwartet: HH:MM)")

    if not (0 <= stunden < 24):
        raise ValidationError("Der Stundenwert ist ungültig! (Zwischen 0 und 23)")

    if not (0 <= minuten < 60):
        raise ValidationError("Der Minutenwert ist ungültig! (Zwischen 0 und 59)")
