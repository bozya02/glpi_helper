from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('scanner/<str:itemtype>/<int:item_id>/', views.scanner, name='scanner_detail'),
    path('scanner/', views.scanner, name='scanner'),
    path('scanner-table/', views.scanner_table, name='scanner_table'),
]
