from django.urls import path

from . import views

urlpatterns = [
    path('items/', views.get_items),
    path('locations/', views.get_locations),
    path('item', views.get_item)
]
