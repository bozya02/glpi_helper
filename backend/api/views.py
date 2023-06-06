from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponseNotFound, HttpRequest
from glpi_api import GLPI
import json
from django.core import serializers
from api.models import *
from forcedisplays import *

import forcedisplays

url = 'http://10.3.2.103/apirest.php'
app_token = 'v3WMy8feotFXH9G6tTOWyu9UdyMsBNn0xWzEFSvk'
user_token = ['glpi', 'adminBozya02']
glpi = GLPI(url=url, apptoken=app_token, auth=user_token, verify_certs=False)


def get_items(request: WSGIRequest | HttpRequest = None, itemtype=None):
    criteria = []
    for param in request.GET:
        if param == 'itemtype':
            continue
        criteria.append({
            'field': param,
            'searchtype': 'contains',
            'value': request.GET.get(param)
        })

    forcedisplay = (list(forces['item'].keys()) + list(forces['computer'].keys())) if itemtype == 'Computer' else \
        forces['item'].keys()
    try:
        items = glpi.search(itemtype=itemtype, criteria=criteria, range='0-999999',
                            forcedisplay=forcedisplay)
    except Exception:
        return HttpResponseNotFound()

    result = []
    users = {}
    for item in items:
        username = item[str(list(forces['item'].keys())[-1])]
        if not username in users:
            users[username] = get_contact_info(username)
        result.append({'item': item, 'user': users[username], 'item_type': itemtype})
    return JsonResponse({'items': result})


def get_item(request: WSGIRequest | HttpRequest, itemtype, guid):
    if itemtype is None or guid is None:
        return HttpResponseNotFound()

    db_item = Item.get_item_id_by_guid(guid)
    item_id = db_item.item_id

    if item_id is None:
        return HttpResponseNotFound()

    criteria = [{
        'field': 'id',
        'searchtype': 'contains',
        'value': item_id
    }]

    forcedisplay = (list(forces['item'].keys()) + list(forces['computer'].keys())) if itemtype == 'Computer' else \
        forces['item'].keys()
    try:
        item = glpi.search(itemtype=itemtype, criteria=criteria, range='0-999999',
                           forcedisplay=forcedisplay)[0]
    except Exception:
        return HttpResponseNotFound()

    user = get_contact_info(item[str(list(forces['item'].keys())[-1])])
    item_movements = db_item.itemmovement_set.filter(is_returned=False)
    movement = item_movements.first().movement if item_movements else None

    return JsonResponse({'result': {
        'item': item,
        'user': user,
        'item_type': itemtype,
        'movement': movement.to_json() if movement else None
    }})


def get_items_by_movement(request, movement):
    items = []
    for item_movement in ItemMovement.objects.filter(movement=movement):
        item = (json.loads(get_item(request, item_movement.item.item_type, item_movement.item.guid).content)['result'])
        item['is_returned'] = item_movement.is_returned
        item['item_movement_id'] = item_movement.id
        items.append(item)
    return JsonResponse({'result': items})


def get_contact_info(username):
    criteria = [{
        'field': 'User.name',
        'searchtype': 'contains',
        'value': username
    }]
    try:
        user = glpi.search(itemtype='user', criteria=criteria, range='0-10', forcedisplay=forces['user'])[0]
    except:
        return ''

    return ' '.join(filter(None, list(user.values())[1:3]))


def get_users(request=None):
    users = glpi.search(itemtype='user', range='0-9999', forcedisplay=forces['user'])
    return JsonResponse({'result': [' '.join(filter(None, list(user.values())[1:3])) for user in users]})


def get_locations(request: WSGIRequest = None) -> JsonResponse:
    locations = glpi.get_all_items(itemtype='Location', range='0-999999')
    return JsonResponse({'result': [item['name'] for item in locations]})


def create_ticket(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    title = request.POST.get('title')
    description = request.POST.get('description')
    anonymous = request.POST.get('anonymous')

    user_glpi = GLPI(url=url, apptoken=app_token, auth=user_token if anonymous else [username, password],
                     verify_certs=False)
    ticket_data = {
        'name': title,
        'content': description
    }
    print(user_glpi.add('ticket', ticket_data))


def create_movement(request):
    user = request.POST.get('user')
    location = request.POST.get('location')
    date = request.POST.get('date')
    items = json.loads(request.POST.get('items'))

    movement = Movement.objects.create(username=user, location=location, move_date=date)

    for item in items:
        db_item = Item.check_or_create_item(item['id'], item['item_type'])
        ItemMovement.objects.create(movement=movement, item=db_item)

    return movement.id
