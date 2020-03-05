from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from metadata.forms import *
from metadata.models import *
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView, DeleteView,\
    UpdateView
from django.utils import timezone
from django.urls import reverse
from django.urls.base import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
# Create your views here.



class Index(LoginRequiredMixin, View):
    template_name = 'index.html'
    
    def get(self,request):
        obj= Project.objects.filter(status="Active").order_by('-pk')
        usr=self.request.user
        context = {
            'object': obj,
            'usr':usr,
        }
        
        return render(request, self.template_name, context)
    

####PROJECT########
    
 
class ShowProject(LoginRequiredMixin, View):
    template_name = 'showProject.html'
    
    def get(self,request):
        obj = Project.objects.all().order_by('-pk')
        context = {
            'object': obj,
        }
        
        return render(request, self.template_name, context)
    

class AddProject(LoginRequiredMixin, CreateView):
    template_name = 'customForm.html'
    form_class = ProjectForm
    success_url = reverse_lazy('showProject')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        return super().form_valid(form)
    
    
   
class DetailProject(LoginRequiredMixin, View):
    template_name = 'detailProject.html'
    def get(self,request,prj_pk):
        context = {}
        prj = Project.objects.get(pk=prj_pk)
        context['project']= prj
        return render(request, self.template_name, context)
    

class EditProject(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'customForm.html'
    form_class = ProjectForm
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        form.instance.edited_at = timezone.now()
        return super().form_valid(form)
    
    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs['prj_pk'])
    
    def get_success_url(self):
        return reverse('detailProject', kwargs={'prj_pk': self.kwargs['prj_pk']})


class DeleteProject(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'delete.html'
    success_url = reverse_lazy('showProject')
    

###################

####EXPERIMENT########


######################

