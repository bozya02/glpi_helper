from django import template

register = template.Library()

@register.filter
def get_item_value(item, key):
    return item.get(str(key), '')

@register.filter
def is_list(value):
    return isinstance(value, list)

@register.filter
def generate_ids(items):
    return [item['item']['2'] for item in items]