'''
Created on Feb. 26, 2020

@author: ankita
'''
from django.urls import path
from django.conf.urls import url, include

from . import views
from metadata.views import *

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'adProject/$',views.test, name='addProject'),
]