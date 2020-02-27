'''
Created on Feb. 26, 2020

@author: ankita
'''
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings

from . import views
from metadata.views import *

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^addProject/$', AddProject.as_view(), name='addProject'),
    url(r'^showProject/$', ShowProject.as_view(), name='showProject'),
    url(r'^detailProject/(?P<prj_pk>[0-9]+)/$', DetailProject.as_view(), name='detailProject'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
