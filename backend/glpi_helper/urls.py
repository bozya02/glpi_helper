from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('scanner/<str:itemtype>/<str:item_uuid>/', views.scanner, name='scanner_detail'),
    path('scanner/', views.scanner, name='scanner'),
    path('scanner-table/', views.scanner_table, name='scanner_table'),
    path('clear-table/', views.clear_table, name='clear_table'),
    path('download_table/', views.download_table, name='download_table')
]
