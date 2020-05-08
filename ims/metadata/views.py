from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect, JsonResponse
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
from django.core import serializers
import json
from django.shortcuts import redirect
from django.db import models
import metadata.models as app_models
from django.views.decorators.csrf import csrf_exempt
from crispy_forms.utils import render_crispy_form
from django import forms
from django.utils.html import escape

# Create your views here.


####INDEX############

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
    
#######################   
####JSON FIELDS########
def createJSON(request):
    json_type_pk = request.POST.get('json_type')
    json_object = JsonObj.objects.get(pk=json_type_pk).json_fields
    data = {}
    for keys in json_object:
        formVal = request.POST.get(keys)
        data[keys] = formVal
    json_data = json.dumps(data)
    return(json_data)
 
@csrf_exempt                
def addFields(request):
    if request.method == 'POST' and request.is_ajax():
        json_type_pk = request.POST.get('json_type_pk')
        field_values = JsonObj.objects.get(pk=json_type_pk).json_fields
        form = FieldsForm(initial={'field_values':field_values})
        form_html = render_crispy_form(form)
        return HttpResponse(form_html)
    else :
        return HttpResponse('<h1>Page was found</h1>')
 
#######################
####PROJECT############
    
 
class ShowProject(LoginRequiredMixin, View):
    template_name = 'showProject.html'
    
    def get(self,request):
        obj = Project.objects.all().order_by('-pk')
        context = {
            'object': obj,
        }
        
        return render(request, self.template_name, context)

class DetailProject(LoginRequiredMixin, View):
    template_name = 'detailProject.html'
    def get(self,request,prj_pk):
        prj = Project.objects.get(pk=prj_pk)
        exp = Experiment.objects.filter(project=prj_pk)
        context = {
            'project': prj,
            'experiment': exp,
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
    
    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs['prj_pk'])
    

######################
####Biosource#########

class AddBiosource(LoginRequiredMixin, CreateView):
    template_name = 'customForm.html'
    form_class = BiosourceForm
       
    def post(self, request, *args, **kwargs):
        existing_object = self.request.POST.get('choose_existing')
        if(existing_object):
            return HttpResponseRedirect(reverse('addBiosample', kwargs={'prj_pk':self.kwargs['prj_pk'], 'source_pk':existing_object}))
        else:
            return CreateView.post(self, request, *args, **kwargs)
    
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        form.instance.json_fields = createJSON(self.request)
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('addBiosample', kwargs={'prj_pk':self.kwargs['prj_pk'], 'source_pk':self.object.pk})
    
    
class DetailBiosource(LoginRequiredMixin, View):
    template_name = 'detailClass.html'
    def get(self,request,source_pk):
        bio = Biosource.objects.get(pk=source_pk)
        
        context = {
            'object': bio,
        }
        
        return render(request, self.template_name, context)

class EditBiosource(LoginRequiredMixin, UpdateView):
    model = Biosource
    template_name = 'editForm.html'
    form_class = BiosourceForm
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        form.instance.edited_at = timezone.now()
        form.instance.json_fields = createJSON(self.request)
        return super().form_valid(form)
    
    def get_object(self):
        return get_object_or_404(Biosource, pk=self.kwargs['obj_pk'])
    
    def get_success_url(self):
        return reverse('detailBiosource', kwargs={'source_pk': self.kwargs['obj_pk']})


class DeleteBiosource(LoginRequiredMixin, DeleteView):
    model = Biosource
    template_name = 'delete.html'
    prj_pk = None
    
    def get_object(self):
        bio = get_object_or_404(Biosource, pk=self.kwargs['obj_pk'])
        #print(bio.sample_source.all())
#         self.prj_pk = bio__sample__exp__pk
        return bio
    
    def get_success_url(self):
        #return reverse('detailProject', kwargs={'prj_pk': self.prj_pk})
        return reverse_lazy('showProject')


    
######################
####BIOSAMPLE##########
class AddBiosample(LoginRequiredMixin, CreateView):
    template_name = 'customForm.html'
    form_class = BiosampleForm
    
    def get_initial(self):
        initial = super(AddBiosample, self).get_initial()
        initial.update({'source_pk': self.kwargs['source_pk']})
        return initial
    

    def post(self, request, *args, **kwargs):
        existing_object = self.request.POST.get('choose_existing')
        if(existing_object):
            return HttpResponseRedirect(reverse('addExperiment', kwargs={'prj_pk':self.kwargs['prj_pk'],'sample_pk':existing_object}))
        else:
            return CreateView.post(self, request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        form.instance.json_fields = createJSON(self.request)
        form.instance.biosource = Biosource.objects.get(pk=self.kwargs['source_pk'])
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('addExperiment', kwargs={'prj_pk':self.kwargs['prj_pk'],'sample_pk':self.object.pk})

class DetailBiosample(LoginRequiredMixin, View):
    template_name = 'detailClass.html'
    def get(self,request,sample_pk):
        sample = Biosample.objects.get(pk=sample_pk)
        
        context = {
            'object': sample,
        }
        
        return render(request, self.template_name, context)

class EditBiosample(LoginRequiredMixin, UpdateView):
    model = Biosample
    template_name = 'editForm.html'
    form_class = BiosampleForm
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        form.instance.edited_at = timezone.now()
        form.instance.json_fields = createJSON(self.request)
        return super().form_valid(form)
    
    def get_object(self):
        return get_object_or_404(Biosample, pk=self.kwargs['obj_pk'])
    
    def get_success_url(self):
        return reverse('detailBiosample', kwargs={'sample_pk': self.kwargs['obj_pk']})


class DeleteBiosample(LoginRequiredMixin, DeleteView):
    model = Biosample
    template_name = 'delete.html'
    prj_pk = None
    
    def get_object(self):
        sample = get_object_or_404(Biosample, pk=self.kwargs['obj_pk'])
        self.prj_pk = sample.exp_biosample.all()[0].pk
        return sample
    
    def get_success_url(self):
        return reverse('detailProject', kwargs={'prj_pk': self.prj_pk})


    
######################

####EXPERIMENT########

class AddExperiment(LoginRequiredMixin, CreateView):
    template_name = 'customForm.html'
    form_class = ExperimentForm
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        form.instance.project=Project.objects.get(pk=self.kwargs['prj_pk'])
        form.instance.biosample = Biosample.objects.get(pk=self.kwargs['sample_pk'])
        form.instance.json_fields = createJSON(self.request)
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('detailProject', kwargs={'prj_pk':self.kwargs['prj_pk']})
    


class DetailExperiment(LoginRequiredMixin, View):
    template_name = 'detailExperiment.html'
    
    def get(self,request,exp_pk):
        exp = Experiment.objects.get(pk=exp_pk)
        context = {
            'experiment': exp
        }
        
        return render(request, self.template_name, context)

class EditExperiment(LoginRequiredMixin, UpdateView):
    model = Experiment
    template_name = 'editForm.html'
    form_class = ExperimentForm
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        form.instance.edited_at = timezone.now()
        form.instance.json_fields = createJSON(self.request)
        return super().form_valid(form)
    
    def get_object(self):
        return get_object_or_404(Experiment, pk=self.kwargs['exp_pk'])
    
    def get_success_url(self):
        return reverse('detailExperiment', kwargs={'exp_pk': self.kwargs['exp_pk']})
    

class DeleteExperiment(LoginRequiredMixin, DeleteView):
    model = Experiment
    template_name = 'delete.html'
    prj_pk = None
    
    def get_object(self):
        exp = get_object_or_404(Experiment, pk=self.kwargs['exp_pk'])
        self.prj_pk = exp.project.pk
        return exp
    
    def get_success_url(self):
        return reverse('detailProject', kwargs={'prj_pk': self.prj_pk})

########################

########################
class AddModification(LoginRequiredMixin, CreateView):
    template_name = 'customForm.html'
    form_class = ModificationForm
    

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            newObject = None
            try:
                newObject = form.save(commit= False)
                newObject.created_by = self.request.user
                newObject.edited_by = self.request.user
                newObject.save()
                
            except(forms.ValidationError):
                newObject = None
                
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(newObject._get_pk_val()), escape(newObject)))

        
        else:
            pageContext = {'form': form}
            return render(request,self.template_name,pageContext)
    
class AddTreatment(LoginRequiredMixin, CreateView):
    template_name = 'customForm.html'
    form_class = TreatmentForm
    
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            newObject = None
            try:
                newObject = form.save(commit= False)
                newObject.created_by = self.request.user
                newObject.edited_by = self.request.user
                newObject.save()
                
            except(forms.ValidationError):
                newObject = None
                
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(newObject._get_pk_val()), escape(newObject)))

        
        else:
            pageContext = {'form': form}
            return render(request,self.template_name,pageContext)











