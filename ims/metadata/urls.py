'''
Created on Feb. 26, 2020

@author: ankita
'''
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings

from metadata.views import *

urlpatterns = [
    url(r'^$', Index.as_view(), name='index'),
    url(r'^addProject/$', AddProject.as_view(), name='addProject'),
    url(r'^showProject/$', ShowProject.as_view(), name='showProject'),
    url(r'^detailProject/(?P<prj_pk>[0-9]+)/$', DetailProject.as_view(), name='detailProject'),
    url(r'^editProject/(?P<prj_pk>[0-9]+)/$', EditProject.as_view(), name='editProject'),
    url(r'^deleteProject/$', DeleteProject.as_view(), name='deleteProject'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
