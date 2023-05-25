# import Http Response from django
import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

import api.views
from forcedisplays import *
from glpi_helper import service
from .forms import *
from .service import generate_qr


def home(request: WSGIRequest) -> HttpResponse:
    return render(request, 'home.html')


def scanner(request: WSGIRequest, itemtype: str = None, item_guid: int = None) -> JsonResponse | HttpResponse:
    # api.views.create_ticket('test_ticket', 'test_ticket123', 123, '213213')
    ticket_form = TicketForm()
    ticket_form.fields['anonymous'].widget.attrs['onchange'] = 'switchVisible(event);'
    form = ScannerForm()
    form.fields['file'].widget.attrs['onchange'] = 'this.form.submit();'

    if request.method == 'POST':
        if 'file' in request.FILES:
            form = ScannerForm(request.POST, request.FILES)
            file = request.FILES.get('file')
            if file:
                qr_code = service.recognize_qr(file.read())
                if qr_code:
                    params = qr_code.split('/')[3:6]
                    itemtype = params[1]
                    item_guid = params[2]
                    return redirect('/scanner/{0}/{1}'.format(itemtype, item_guid))
        elif 'title' in request.POST:
            ticket_form = TicketForm()
            ticket_form.fields['anonymous'].widget.attrs['onchange'] = 'switchVisible(event);'
            api.views.create_ticket(request)

    context = {'form': form, 'ticket_form': ticket_form}
    if not (itemtype is None or item_guid is None):
        content = json.loads(api.views.get_item(request, itemtype, item_guid).content)['result']
        context['item'] = content['item']
        context['user'] = content['user']
        context['display'] = service.get_qr_display(itemtype.lower() == 'computer')
    return render(request, 'scanner.html', context)


def scanner_table(request):
    items = request.session.get('items', [])
    if request.method == 'POST':
        form = ScannerForm(request.POST, request.FILES)
        file = request.FILES.get('file')
        form.fields['file'].widget.attrs['onchange'] = 'this.form.submit();'
        if file:
            qr_code = service.recognize_qr(file.read())
            if qr_code:
                params = qr_code.split('/')[3:6]
                itemtype = params[1]
                item_guid = params[2]
                result = json.loads(api.views.get_item(request, itemtype, item_guid).content)['result']
                items.append(result)
                request.session['items'] = items
    else:
        form = ScannerForm()
        form.fields['file'].widget.attrs['onchange'] = 'this.form.submit();'

    context = {'form': form, 'items': items, 'display': service.get_table_display()}
    return render(request, 'scanner_table.html', context)


def search_table(request):
    items = []
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            itemtype = form.cleaned_data['itemtype']
            items = json.loads(api.views.get_items(request, itemtype).content)['items']

    else:
        itemtype = ITEM_TYPES[0]
        form = SearchForm()

    context = {'form': form, 'items': items, 'display': service.get_table_display(), 'itemtype': itemtype}
    return render(request, 'search_table.html', context)


def clear_table(request):
    if 'items' in request.session:
        del request.session['items']
    return redirect('scanner_table')


def download_table(request):
    items = request.POST.get('items')
    excel_file = service.generate_xlsx(items)
    response = HttpResponse(excel_file.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="table.xlsx"'

    return response


def download_qr(request):
    item_ids = request.POST.get('item_ids')
    item_id = request.POST.get('item_id')

    if item_ids:
        item_ids = json.loads(item_ids.replace("'", '"'))

    itemtype = request.POST.get('itemtype').replace("'", '"')

    buffer = generate_qr(item_ids if item_ids else [item_id], itemtype)

    if not item_ids:
        response = HttpResponse(content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="qr_code_{itemtype}_{item_id}.png"'
        response.write(buffer.getvalue())
    else:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="qr_codes.pdf"'
        response.write(buffer.getvalue())

    return response
