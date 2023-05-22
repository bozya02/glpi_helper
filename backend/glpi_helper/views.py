# import Http Response from django
import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

import api.views
from forcedisplays import *
from glpi_helper import service
from .forms import ScannerForm


def home(request: WSGIRequest) -> HttpResponse:
    return render(request, 'home.html')


def scanner(request: WSGIRequest, itemtype: str = None, item_uuid: int = None) -> JsonResponse | HttpResponse:
    if request.method == 'POST':
        form = ScannerForm(request.POST, request.FILES)
        file = request.FILES.get('file')
        if file:
            qr_code = service.read(file.read())
            if qr_code:
                params = qr_code.split('/')[3:6]
                itemtype = params[1]
                item_uuid = params[2]
    else:
        form = ScannerForm()
        form.fields['file'].widget.attrs['onchange'] = 'this.form.submit();'

    context = {'form': form}
    if not (itemtype is None or item_uuid is None):
        content = json.loads(api.views.get_item(request, itemtype, item_uuid).content)['result']
        context['item'] = content['item']
        context['user'] = content['user']
        context['displays'] = displays

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
                item_uuid = params[2]
                items.append(json.loads(api.views.get_item(request, itemtype, item_uuid).content))
                request.session['items'] = items
    else:
        form = ScannerForm()
        form.fields['file'].widget.attrs['onchange'] = 'this.form.submit();'

    context = {'form': form, 'items': items}
    return render(request, 'scanner_table.html', context)
