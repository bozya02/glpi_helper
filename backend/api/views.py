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
                            forcedisplay=forces['item'].keys())
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

    forcedisplay = (list(forces['item'].keys()) + list(forces['computer'].keys())) if itemtype == 'Computer' else \
        forces['item'].keys()
    try:
        item = glpi.search(itemtype=itemtype, criteria=criteria, range='0-999999',
                           forcedisplay=forcedisplay)[0]
    except Exception:
        return HttpResponseNotFound()
    user = get_contact_info(item[str(list(forces['item'].keys())[-1])])

    item.pop(list(forces['item'].keys())[-1])
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

    user = glpi.search(itemtype='user', criteria=criteria, range='0-999999', forcedisplay=forces['user'])[0]
    del user[list(user.keys())[0]]
    return user


def create_ticket(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    title = request.POST.get('title')
    description = request.POST.get('description')
    anonymous = request.POST.get('anonymous')

    print(request.POST)

    user_glpi = GLPI(url=url, apptoken=app_token, auth=user_token if anonymous else [username, password],
                     verify_certs=False)
    ticket_data = {
        'name': title,
        'content': description
    }
    print(user_glpi.add('ticket', ticket_data))
