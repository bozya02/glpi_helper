# import Http Response from django
import urllib.parse

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, QueryDict, JsonResponse
from django.shortcuts import render, redirect
import requests
import api.views
import json
import io

from glpi_helper import service


# create a function
def items_view(request):
    # create a dictionary to pass
    # data to the template
    items = api.views.get_items(request)  # json.loads(requests.get('http://127.0.0.1:8000/api/items/').content)
    items = json.loads(items.content)
    # return response with template and context
    return render(request, 'base.html', items)


def home(request: WSGIRequest) -> HttpResponse:
    return render(request, 'home.html')


def scanner(request: WSGIRequest) -> JsonResponse | HttpResponse:
    item_type = request.GET.get('itemtype')
    item_id = request.GET.get('item_id')
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            qr_code = service.read(file.read())
            if qr_code:
                params = urllib.parse.parse_qs(urllib.parse.urlsplit(qr_code).query)
                print(params)
                item_type = params.get('itemtype', item_type)[0]
                item_id = params.get('item_id', item_id)[0]

    if is_ajax(request):
        print({'itemtype': item_type})
        return JsonResponse({'itemtype': item_type})
        #return redirect('/scanner/?itemtype={0}&item_id={1}'.format(item_type, item_id))

    if item_type is None or item_id is None:
        print(1)
        return render(request, 'scanner.html')
    else:
        return render(request, 'scanner.html', json.loads(api.views.get_item(request).content))


def is_ajax(request: WSGIRequest) -> bool:
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
