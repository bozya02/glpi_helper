from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from glpi_api import GLPI
import json

url = 'http://10.3.2.103/apirest.php'
app_token = 'v3WMy8feotFXH9G6tTOWyu9UdyMsBNn0xWzEFSvk'
user_token = ['glpi', 'adminBozya02']
glpi = GLPI(url=url, apptoken=app_token, auth=user_token, verify_certs=False)


def get_items(request: WSGIRequest = None) -> JsonResponse:
    criteria = []
    itemtype = request.GET.get('itemtype')
    if not itemtype:
        itemtype = 'Computer'
    for param in request.GET:
        if param == 'itemtype':
            continue
        criteria.append({
            'field': param,
            'searchtype': 'contains',
            'value': request.GET.get(param)
        })

    items = glpi.search(itemtype=itemtype, criteria=criteria, range='0-999999', uid_cols=True, forcedisplay=[126])

    return JsonResponse({'items': items})


def get_locations(request: WSGIRequest = None) -> JsonResponse:
    locations = glpi.get_all_items(itemtype='Location', range='0-999999')
    locations = [{'id': item['id'], 'name': item['name']} for item in locations]
    return JsonResponse({'locations': locations})


def get_item(request: WSGIRequest):
    itemtype = request.GET.get('itemtype')
    item_id = request.GET.get('item_id')
    item = glpi.get_item(itemtype=itemtype, item_id=item_id)

    return JsonResponse({'item': item})


def refactor_names(items: list) -> list:
    for index, item in enumerate(items):
        keys = list(item.keys())
        for key in keys:
            new_key = key.split('.')[1].lower()
            item[new_key] = item[key]
            del item[key]

    return items
