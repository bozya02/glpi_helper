# import Http Response from django
from django.shortcuts import render
import requests
import api.views
import json


# create a function
def items_view(request):
    # create a dictionary to pass
    # data to the template
    items = api.views.get_items(request)  # json.loads(requests.get('http://127.0.0.1:8000/api/items/').content)
    items = json.loads(items.content)
    # return response with template and context
    return render(request, 'base.html', items)


def home(request):
    return render(request, 'home.html')
