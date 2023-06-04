import json

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
    return json.dumps([{'id': item['item']['2'], 'item_type': item['item_type']} for item in items])


@register.filter()
def to_json(item):
    return json.dumps(item)
