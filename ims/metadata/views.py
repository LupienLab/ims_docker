from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from metadata.forms import *
from django.views.generic.base import View
# Create your views here.

def index(request):
    return HttpResponse("Hi! Welcome lab user")

class AddProject(View): 
    template_name = 'customForm.html'
    form_class = ProjectForm
    
    def get(self,request):
        form = self.form_class()
        return render(request, self.template_name,{'form':form})
    
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('')
        else:
            return render(request, self.template_name,{'form':form})