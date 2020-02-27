from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from metadata.forms import *
from metadata.models import *
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
            return HttpResponseRedirect('/showProject')
        else:
            return render(request, self.template_name,{'form':form})
        

class ShowProject(View):
    template_name = 'showProject.html'
    
    def get(self,request):
        obj = Project.objects.all().order_by('-pk')
        context = {
            'object': obj,
        }
        
        return render(request, self.template_name, context)

class DetailProject(View):
    template_name = 'detailProject.html'
    def get(self,request,prj_pk):
        context = {}
        prj = Project.objects.get(pk=prj_pk)
        context['project']= prj
        return render(request, self.template_name, context)