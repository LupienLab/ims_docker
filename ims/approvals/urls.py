# urls.py
from django.urls import path
from .views import create_approval_request, approval_list, approve_request, disapprove_request

urlpatterns = [
  path('create/', create_approval_request, name='create_approval_request'),
  path('', approval_list, name='approval_list'),
  path('approve/<int:pk>/', approve_request, name='approve_request'),
  path('disapprove/<int:pk>/', disapprove_request, name='disapprove_request'),
]
