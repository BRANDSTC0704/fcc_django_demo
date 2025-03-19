from django.core.exceptions import ValidationError


def validate_time(value):

    stunden = value.hour
    minuten = value.minute

    stundentest = stunden >= 0 & stunden < 25
    minutentest = minuten >= 0 & minuten < 61

    if not stundentest:
        msg_h = "Der Stundenwert ist ungültig! (zw. 0 und 24)"
        raise ValidationError(msg_h)
    elif not minutentest:
        msg_m = "Der Stundenwert ist ungültig! (zw. 0 und 60)"
        raise ValidationError(msg_m)
