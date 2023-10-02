from django.views.generic.base import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.contrib.auth import logout as auth_logout
import requests
from metadata.keycloak_client import keycloak_openid
from metadata.keycloak_client import *

class CustomLogin(View):
    template_name = 'login.html'
    def get(self,request):
        return render(request, self.template_name)
    

def logout_view(request):
    if request.user.is_authenticated:
        logout_keycloak(request)
    auth_logout(request)
    return render(request, 'login.html')

def logout_view2(request):
    print("logout2 called")
    logout_keycloak(request)
    return render(request, 'login.html')