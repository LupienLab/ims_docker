# lab/urls.py

from django.urls import path
from .views import lab_list


urlpatterns = [
    path('', lab_list, name='profile'),
]
