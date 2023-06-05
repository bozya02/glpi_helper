# import Http Response from django
import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

import api.views
from api.models import *
import config
from forcedisplays import *
from glpi_helper import service
from .forms import *
from .service import generate_qr


def home(request: WSGIRequest) -> HttpResponse:
    return render(request, 'home.html')


def scanner_view(request: WSGIRequest, itemtype: str = None, item_guid: int = None) -> JsonResponse | HttpResponse:
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

    context = {'form': form, 'ticket_form': ticket_form, 'anon': config.CAN_ANON}
    if not (itemtype is None or item_guid is None):
        content = json.loads(api.views.get_item(request, itemtype, item_guid).content)['result']
        context['item'] = content['item']
        context['user'] = content['user']
        context['movement'] = content['movement']
        context['display'] = service.get_qr_display(itemtype.lower() == 'computer')

    return render(request, 'scanner.html', context)


def scanner_list_view(request):
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
    return render(request, 'scanner_list.html', context)


def search_table_view(request):
    items = []
    selected_items = request.session.get('selected_items', [])
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            itemtype = form.cleaned_data['itemtype']
            items = json.loads(api.views.get_items(request, itemtype).content)['items']
            request.session['search_items'] = items
    else:
        itemtype = ITEM_TYPES[0]
        form = SearchForm()

    if not items:
        items = selected_items

    movement_form = MovementForm()

    context = {'form': form,
               'items': items,
               'display': service.get_table_display(),
               'itemtype': itemtype,
               'selected_items': selected_items,
               'movement_form': movement_form
               }

    return render(request, 'search_table.html', context)


def movements_view(request):
    movements = Movement.objects.all()
    return render(request, 'movements.html', context={'movements': movements})


def movement_view(request, movement_id):
    movement = get_object_or_404(Movement, pk=movement_id)
    items = json.loads(api.views.get_items_by_movement(request, movement).content)['result']

    print(items)
    return render(request, 'movement.html',
                  context={'movement': movement, 'items': items, 'display': service.get_table_display()})


def create_movement_view(request):
    movement_form = MovementForm(request.POST)
    if movement_form.is_valid():
        api.views.create_movement(request)
        request.session['selected_items'] = []

    return redirect('search_table')


def clear_table(request):
    if 'items' in request.session:
        del request.session['items']
    return redirect('scanner_table')


def download_table(request):
    session_item = request.GET.get('items')
    items = request.session.get(session_item, [])
    excel_file = service.generate_xlsx(items)
    response = HttpResponse(excel_file.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="table.xlsx"'

    return response


def download_qr(request):
    items = json.loads(request.POST.get('items'))
    buffer = generate_qr(items)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="qr_codes.pdf"'
    response.write(buffer.getvalue())

    return response


def update_selected_items(request):
    if request.method == 'POST':
        selected_items = request.session.get('selected_items', [])
        select_all = request.POST.get('select-all')
        item = request.POST.get('item')

        if item:
            item = json.loads(item)
            if item in selected_items:
                selected_items.remove(item)
            else:
                selected_items.append(item)
        else:
            if select_all:
                items = json.loads(request.POST.get('items'))
                selected_items = items
            else:
                selected_items = []

        request.session['selected_items'] = selected_items

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})
