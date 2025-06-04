# lab/urls.py

from django.urls import path
from .views import lab_list, supervisor_view

urlpatterns = [
    path('', lab_list, name='lab_list'),
    path('supervisor/', supervisor_view, name='supervisor_view'),
]
