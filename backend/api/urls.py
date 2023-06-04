from django.urls import path

from . import views

urlpatterns = [
    path('items/', views.get_items),
    path('locations/', views.get_locations),
    path('item/<str:itemtype>/<int:item_id>/', views.get_item),
    path('users/', views.get_users)
]
