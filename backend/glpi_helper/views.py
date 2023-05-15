# import Http Response from django
import urllib.parse

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, QueryDict, JsonResponse, HttpRequest
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


def scanner(request: WSGIRequest, itemtype: str = None, item_id: int = None) -> JsonResponse | HttpResponse:
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            qr_code = service.read(file.read())
            if qr_code:
                params = qr_code.split('/')[3:6]
                itemtype = params[1]
                item_id = params[2]

    if is_ajax(request):
        return JsonResponse(json.loads(api.views.get_item(request, itemtype, item_id).content))

    if itemtype is None or item_id is None:
        return render(request, 'scanner.html')
    else:
        return render(request, 'scanner.html', json.loads(api.views.get_item(request, itemtype, item_id).content))


def is_ajax(request: WSGIRequest) -> bool:
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
