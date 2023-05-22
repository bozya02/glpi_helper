from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponseNotFound, HttpRequest
from glpi_api import GLPI
import json
from forcedisplays import *

import forcedisplays

url = 'http://10.3.2.103/apirest.php'
app_token = 'v3WMy8feotFXH9G6tTOWyu9UdyMsBNn0xWzEFSvk'
user_token = ['glpi', 'adminBozya02']
glpi = GLPI(url=url, apptoken=app_token, auth=user_token, verify_certs=False)


def get_items(request: WSGIRequest | HttpRequest = None):
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

    try:
        items = glpi.search(itemtype=itemtype, criteria=criteria, range='0-999999',
                            forcedisplay=displays['item'].keys())
    except Exception:
        return HttpResponseNotFound()

    return JsonResponse({'items': items})


def get_locations(request: WSGIRequest = None) -> JsonResponse:
    locations = glpi.get_all_items(itemtype='Location', range='0-999999')
    locations = [{'id': item['id'], 'name': item['name']} for item in locations]
    return JsonResponse({'locations': locations})


def get_item(request: WSGIRequest | HttpRequest, itemtype, item_uuid):
    if itemtype is None or item_uuid is None:
        return HttpResponseNotFound()

    criteria = [{
        'field': 'uuid',
        'searchtype': 'contains',
        'value': item_uuid
    }]

    forcedisplay = (list(displays['item'].keys()) + list(displays['computer'].keys())) if itemtype == 'Computer' else displays['item'].keys()
    try:
        item = glpi.search(itemtype=itemtype, criteria=criteria, range='0-999999',
                           forcedisplay=forcedisplay)[0]
    except Exception:
        return HttpResponseNotFound()
    user = get_contact_info(item[str(list(displays['item'].keys())[-1])])

    item.pop(list(displays['item'].keys())[-1])
    item.popitem()

    return JsonResponse({'result': {
        'item': item,
        'user': user
    }})


def get_contact_info(username):
    criteria = [{
        'field': 'User.name',
        'searchtype': 'contains',
        'value': username
    }]

    user = glpi.search(itemtype='user', criteria=criteria, range='0-999999', forcedisplay=displays['user'])[0]
    del user[list(user.keys())[0]]
    return user
