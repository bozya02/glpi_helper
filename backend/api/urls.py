from django.urls import path

from . import views

urlpatterns = [
    path('items/', views.get_items),
    path('locations/', views.get_locations),
]
