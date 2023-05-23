# import Http Response from django
import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

import api.views
from forcedisplays import *
from glpi_helper import service
from .forms import *


def home(request: WSGIRequest) -> HttpResponse:
    return render(request, 'home.html')


def scanner(request: WSGIRequest, itemtype: str = None, item_uuid: int = None) -> JsonResponse | HttpResponse:
    # api.views.create_ticket('test_ticket', 'test_ticket123', 123, '213213')
    ticket_form = TicketForm()
    ticket_form.fields['anonymous'].widget.attrs['onchange'] = 'switchVisible(event);'

    if request.method == 'POST':
        if 'file' in request.FILES:
            form = ScannerForm(request.POST, request.FILES)
            file = request.FILES.get('file')
            if file:
                qr_code = service.recognize_qr(file.read())
                if qr_code:
                    params = qr_code.split('/')[3:6]
                    itemtype = params[1]
                    item_uuid = params[2]
                    return redirect('{0}/{1}'.format(itemtype, item_uuid))
        elif 'title' in request.POST:
            ticket_form = TicketForm()
            ticket_form.fields['anonymous'].widget.attrs['onchange'] = 'switchVisible(event);'
            api.views.create_ticket(request)
            form = ScannerForm()
            form.fields['file'].widget.attrs['onchange'] = 'this.form.submit();'
    else:
        form = ScannerForm()
        form.fields['file'].widget.attrs['onchange'] = 'this.form.submit();'

    context = {'form': form, 'ticket_form': ticket_form}
    if not (itemtype is None or item_uuid is None):
        content = json.loads(api.views.get_item(request, itemtype, item_uuid).content)['result']
        context['item'] = content['item']
        context['user'] = " ".join(filter(None, content['user'].values()))
        context['display'] = service.get_qr_display(itemtype.lower()=='computer')
    return render(request, 'scanner.html', context)


def scanner_table(request):
    items = request.session.get('items', [])
    if request.method == 'POST':
        form = ScannerForm(request.POST, request.FILES)
        file = request.FILES.get('file')
        if file:
            qr_code = service.recognize_qr(file.read())
            if qr_code:
                params = qr_code.split('/')[3:6]
                itemtype = params[1]
                item_uuid = params[2]
                result = json.loads(api.views.get_item(request, itemtype, item_uuid).content)['result']
                items.append({'item': result['item'], 'user': " ".join(filter(None, list(result['user'].values())))})
                request.session['items'] = items
    else:
        form = ScannerForm()
        form.fields['file'].widget.attrs['onchange'] = 'this.form.submit();'

    context = {'form': form, 'items': items, 'display': service.get_table_display()}
    return render(request, 'scanner_table.html', context)

def clear_table(request):
    if 'items' in request.session:
        del request.session['items']
    return redirect('scanner_table')

def download_table(request):
    items = request.session.get('items', [])

    excel_file = service.generate_xlsx(items)
    response = HttpResponse(excel_file.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="table.xlsx"'

    return response
