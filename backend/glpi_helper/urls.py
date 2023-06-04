from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('scanner/<str:itemtype>/<str:item_guid>/', views.scanner_view, name='scanner_detail'),
    path('scanner/', views.scanner_view, name='scanner'),
    path('scanner-table/', views.scanner_table_view, name='scanner_table'),
    path('search-table/', views.search_table_view, name='search_table'),
    path('clear-table/', views.clear_table, name='clear_table'),
    path('download_table/', views.download_table, name='download_table'),
    path('download_qr/', views.download_qr, name='download_qr'),
    path('update_selected_items/', views.update_selected_items, name='update_selected_items'),
    path('new_movement/', views.create_movement_view, name='new_movement'),
    path('movements/', views.movements_view, name='movements'),
    path('movements/<int:movement_id>', views.movement_view, name='movement'),
]
