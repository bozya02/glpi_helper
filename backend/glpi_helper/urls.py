from django.urls import path

from . import views

urlpatterns = [
    path('scanner/<str:itemtype>/<int:item_id>/', views.scanner, name='scanner_detail'),
    path('scanner/', views.scanner, name='scanner'),
    path('', views.home, name='home'),
]
