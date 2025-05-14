# him2_pressenlinie/templatetags/form_extras.py
from django import template

register = template.Library()

# in templatetags/form_extras.py
# @register.filter(name='get_field')
# def get_field(form, field_name):
#    """Returns the field from the form based on the dynamically generated field name."""
#    return form[field_name] if field_name in form else None


@register.filter(name="get_field")
def get_field(form, field_name):
    if field_name in form.fields:
        return form[field_name]
    return 0
