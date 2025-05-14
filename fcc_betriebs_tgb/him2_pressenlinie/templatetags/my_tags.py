from django import template

register = template.Library()


@register.simple_tag
def get_item(dict_obj, row_id, column_id):
    return dict_obj.get((row_id, column_id))
