import json
from datetime import datetime, timezone

import django.utils.timezone
from django import template

register = template.Library()


@register.filter
def add_class(field, class_attr):
    return field.as_widget(attrs={'class': class_attr})


@register.filter
def get_item_value(item, key):
    return item.get(str(key), '')


@register.filter
def is_list(value):
    return isinstance(value, list)


@register.filter
def generate_ids(items):
    return json.dumps([{'id': item['item']['2'], 'item_type': item['item_type']} for item in items])


@register.filter
def to_json(item):
    return json.dumps(item)


@register.filter
def movement_items_to_json(items):
    return json.dumps([{
        'id': item['item_movement_id'],
        'is_returned': item['is_returned']
    } for item in items])


@register.filter
def is_movement_not_returned(movement):
    return movement.itemmovement_set.filter(
        is_returned=False).exists() and movement.move_date < django.utils.timezone.now().date()


@register.filter
def is_movement_returned(movement):
    return movement.move_date < django.utils.timezone.now().date() and not movement.itemmovement_set.filter(
        is_returned=False).exists()


@register.filter
def custom_date(date):
    value = datetime.strptime(date, '%d.%m.%Y')
    return format(value)


@register.filter
def custom_date_is_past_due(date):
    value = datetime.strptime(date, '%d.%m.%Y')
    return value <= datetime.today()
