# import Http Response from django
import urllib.parse

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, QueryDict, JsonResponse, HttpRequest
from django.shortcuts import render, redirect
import requests
import api.views
import json
import io
from .forms import ScannerForm

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
        form = ScannerForm(request.POST, request.FILES)
        file = request.FILES.get('file')
        if file:
            qr_code = service.read(file.read())
            if qr_code:
                params = qr_code.split('/')[3:6]
                itemtype = params[1]
                item_id = params[2]
    else:
        form = ScannerForm()
        form.fields['file'].widget.attrs['onchange'] = 'this.form.submit();'

    context = {'form': form}
    if not (itemtype is None or item_id is None):
        context['item'] = json.loads(api.views.get_item(request, itemtype, item_id).content)['item']
    return render(request, 'scanner.html', context)


def scanner_table(request):
    items = request.session.get('items', [])
    if request.method == 'POST':
        form = ScannerForm(request.POST, request.FILES)
        file = request.FILES.get('file')
        if file:
            qr_code = service.read(file.read())
            if qr_code:
                params = qr_code.split('/')[3:6]
                itemtype = params[1]
                item_id = params[2]
                items.append(json.loads(api.views.get_item(request, itemtype, item_id).content))
                request.session['items'] = items
    else:
        form = ScannerForm()
        form.fields['file'].widget.attrs['onchange'] = 'this.form.submit();'

    context = {'form': form, 'items': items}
    return render(request, 'scanner_table.html', context)
