from django.shortcuts import render, get_object_or_404, redirect
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
from django.db import models
import metadata.models as app_models
from django.views.decorators.csrf import csrf_exempt
from crispy_forms.utils import render_crispy_form
from django import forms
from django.utils.html import escape
from django.views.generic import DetailView
from view_breadcrumbs import BaseBreadcrumbMixin, ListBreadcrumbMixin, DetailBreadcrumbMixin
from django.utils.functional import cached_property
from metadata.handle_upload import *
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

#import metadata.extendSession
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
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })
    
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

class BrowseProject(LoginRequiredMixin, View):
    template_name = 'showProject.html'
    
    def get(self,request,slug):
        obj = Project.objects.filter(created_by__first_name=slug).order_by('-pk')
        if(len(obj)==0):
            obj = Project.objects.filter(exp_project__json_type__name=slug).order_by('-pk').distinct()
        if(len(obj)==0):
            obj = Project.objects.filter(related__name=slug).order_by('-pk').distinct()
        if(len(obj)==0):
            obj = Project.objects.filter(status=slug).order_by('-pk').distinct()
        context = {
            'object': obj,
        }
        
        return render(request, self.template_name, context)
    

class DetailProject(LoginRequiredMixin, DetailBreadcrumbMixin, DetailView):
    template_name = 'detailProject.html'
    pk_url_kwarg = 'prj_pk'
    model = Project

    def get_context_data(self, **kwargs):
        context = super(DetailProject, self).get_context_data(**kwargs)
        prj = Project.objects.get(pk=self.kwargs['prj_pk'])
        #self.request.CustomSession['active_project'] = self.kwargs['prj_pk']
        exp = Experiment.objects.filter(project=self.kwargs['prj_pk']).order_by('-pk')
        run = SequencingRun.objects.filter(project=self.kwargs['prj_pk']).order_by('-pk')
        context = {
            'project': prj,
            'experiment': exp,
            'sequencingRun': run
        }
        return (context)
    
    @cached_property
    def crumbs(self):
        prj = Project.objects.get(pk=self.kwargs['prj_pk'])
        return [('Project: ' + prj.name, reverse('detailProject', kwargs={'prj_pk': prj.pk}))]


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

class ShowBiosource(LoginRequiredMixin, View):
    template_name = 'showBiosource.html'
    
    def get(self,request):
        obj = Biosource.objects.all().order_by('-pk')
        context = {
            'object': obj,
        }
        
        return render(request, self.template_name, context)

class AddBiosource(LoginRequiredMixin, CreateView):
    template_name = 'customForm.html'
    form_class = BiosourceForm
       
    def post(self, request, *args, **kwargs):
        existing_object = self.request.POST.get('choose_existing')
        if(existing_object):
            return HttpResponseRedirect(reverse('addBiosample', kwargs={'prj_pk':self.kwargs['prj_pk'], 'source_pk':existing_object}))
        else:
            return CreateView.post(self, request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(AddBiosource, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            json_values = createJSON(self.request)
            context['json_values']= json_values
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        form.instance.json_fields = createJSON(self.request)
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('addBiosample', kwargs={'prj_pk':self.kwargs['prj_pk'], 'source_pk':self.object.pk})
    
    
class DetailBiosource(LoginRequiredMixin, DetailView):
    template_name = 'detailClass.html'
    model = Biosource
    pk_url_kwarg = 'source_pk'
    
    def get_context_data(self, **kwargs):
        context = super(DetailBiosource, self).get_context_data(**kwargs)
        rel_bisam=self.object.sample_source.all().order_by('-pk')
        
        context = {
            'object': self.object,
            'rel_bisam': rel_bisam
        }
        return (context)
    
#     @cached_property
#    def crumbs(self):
#         return [('Project: '+self.request.session["active_project"], reverse('detailProject', kwargs={'prj_pk': self.request.session["active_project"]})),
#                 ('Biosource:', reverse('detailBiosource', kwargs={'source_pk': self.kwargs['source_pk']}))]
#         
         
#     
#         return [('Project: '+self.object.project.name, reverse('detailProject', kwargs={'prj_pk': self.object.project.pk})),
#                 ('Experiment: '+self.object.name, reverse('detailExperiment', kwargs={'exp_pk': self.object.pk}))]


class EditBiosource(LoginRequiredMixin, UpdateView):
    model = Biosource
    template_name = 'editFormJson.html'
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
    
    def get_context_data(self, **kwargs):
        context = super(AddBiosample, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            json_values = createJSON(self.request)
            context['json_values']= json_values
        return context

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
    template_name = 'editFormJson.html'
    form_class = BiosampleForm
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        form.instance.edited_at = timezone.now()
        form.instance.json_fields = createJSON(self.request)
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super(EditBiosample, self).get_initial()
        initial.update({'source_pk': self.kwargs['obj_pk']})
        return initial
    
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
    
    def get_context_data(self, **kwargs):
        context = super(AddExperiment, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            json_values = createJSON(self.request)
            context['json_values']= json_values
        return context
    
    def get_success_url(self):
        return reverse('detailProject', kwargs={'prj_pk':self.kwargs['prj_pk']})
    



class DetailExperiment(LoginRequiredMixin, DetailBreadcrumbMixin, DetailView):
    template_name = 'detailExperiment.html'
    model = Experiment
    pk_url_kwarg = 'exp_pk'
    
    def get_context_data(self, **kwargs):
        context = super(DetailExperiment, self).get_context_data(**kwargs)
        seqfiles=context["object"].file_exp.all().order_by('name')
        context["seqfiles"]=seqfiles
        return context
    
        
    @cached_property
    def crumbs(self):
        return [('Project: ' + self.object.project.name, reverse('detailProject', kwargs={'prj_pk': self.object.project.pk})),
                ('Experiment: ' + self.object.name, reverse('detailExperiment', kwargs={'exp_pk': self.object.pk}))]



class EditExperiment(LoginRequiredMixin, UpdateView):
    model = Experiment
    template_name = 'editFormJson.html'
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
###SequencingRun#######
class AddSequencingRun(LoginRequiredMixin, CreateView):
    template_name = 'customForm.html'
    form_class = SequencingRunForm
    
    def get_initial(self):
        initial = super(AddSequencingRun, self).get_initial()
        initial.update({'prj_pk': self.kwargs['prj_pk']})
        return initial
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        form.instance.project=Project.objects.get(pk=self.kwargs['prj_pk'])
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('detailProject', kwargs={'prj_pk':self.kwargs['prj_pk']})
    


class DetailSequencingRun(LoginRequiredMixin, View):
    template_name = 'detailSequencingRun.html'
    def get(self,request,run_pk):
        run = SequencingRun.objects.get(pk=run_pk)
        
        context = {
            'object': run,
        }
        
        return render(request, self.template_name, context)


class EditSequencingRun(LoginRequiredMixin, UpdateView):
    model = SequencingRun
    template_name = 'editForm.html'
    form_class = SequencingRunForm
    
    def get_initial(self):
        initial = super(EditSequencingRun, self).get_initial()
        initial.update({'prj_pk': self.kwargs['prj_pk']})
        return initial
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        form.instance.edited_at = timezone.now()
        return super().form_valid(form)
    
    def get_object(self):
        return get_object_or_404(SequencingRun, pk=self.kwargs['obj_pk'])
    
    def get_success_url(self):
        return reverse('detailSequencingRun', kwargs={'run_pk': self.kwargs['obj_pk']})
    

class DeleteSequencingRun(LoginRequiredMixin, DeleteView):
    model = SequencingRun
    template_name = 'delete.html'
    prj_pk = None
    
    def get_object(self):
        run = get_object_or_404(SequencingRun, pk=self.kwargs['obj_pk'])
        self.prj_pk = run.project.pk
        return run
    
    def get_success_url(self):
        return reverse('detailProject', kwargs={'prj_pk': self.prj_pk})

########################
###SequencingFile#######
class AddSeqencingFile(LoginRequiredMixin, CreateView):
    template_name = 'customForm.html'
    form_class = SeqencingFileForm
    
    def get_initial(self):
        initial = super(AddSeqencingFile, self).get_initial()
        initial.update({'prj_pk': self.kwargs['prj_pk'],'exp_pk':self.kwargs['exp_pk']})
        return initial
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        form.instance.project=Project.objects.get(pk=self.kwargs['prj_pk'])
        form.instance.experiment=Experiment.objects.get(pk=self.kwargs['exp_pk'])
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('detailExperiment', kwargs={'exp_pk': self.kwargs['exp_pk']})
    


class DetailSeqencingFile(LoginRequiredMixin, View):
    template_name = 'detailClass.html'
    def get(self,request,file_pk):
        file = SeqencingFile.objects.get(pk=file_pk)
        
        context = {
            'object': file,
        }
        
        return render(request, self.template_name, context)


class EditSeqencingFile(LoginRequiredMixin, UpdateView):
    model = SeqencingFile
    template_name = 'editForm.html'
    form_class = SeqencingFileForm
    
    def get_initial(self):
        initial = super(EditSeqencingFile, self).get_initial()
        initial.update({'prj_pk': self.kwargs['prj_pk']})
        return initial
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        form.instance.edited_at = timezone.now()
        return super().form_valid(form)
    
    def get_object(self):
        return get_object_or_404(SeqencingFile, pk=self.kwargs['obj_pk'])
    
    def get_success_url(self):
        return reverse('detailSeqencingFile', kwargs={'file_pk': self.kwargs['obj_pk']})
    

class DeleteSeqencingFile(LoginRequiredMixin, DeleteView):
    model = SeqencingFile
    template_name = 'delete.html'
    exp_pk = None
    
    def get_object(self):
        file = get_object_or_404(SeqencingFile, pk=self.kwargs['obj_pk'])
        self.exp_pk = file.experiment.pk
        return file
    
    def get_success_url(self):
        return reverse('detailExperiment', kwargs={'exp_pk': self.exp_pk})

########################


########################
class AddModification(LoginRequiredMixin, CreateView):
    template_name = 'customForm.html'
    form_class = ModificationForm
    

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST,request.FILES)
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

class DetailModification(LoginRequiredMixin, View):
    template_name = 'detailClass.html'
    def get(self,request,obj_pk):
        mod = Modification.objects.get(pk=obj_pk)
        
        context = {
            'object': mod,
        }
        
        return render(request, self.template_name, context)

class EditModification(LoginRequiredMixin, UpdateView):
    template_name = 'editForm.html'
    form_class = ModificationForm
    

    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        form.instance.edited_at = timezone.now()
        return super().form_valid(form)
    
    def get_object(self):
        return get_object_or_404(Modification, pk=self.kwargs['obj_pk'])
    
    def get_success_url(self):
        return reverse('detailModification', kwargs={'obj_pk': self.kwargs['obj_pk']})
    
class DeleteModification(LoginRequiredMixin, DeleteView):
    model = Modification
    template_name = 'delete.html'
    
    def get_object(self):
        return get_object_or_404(Modification, pk=self.kwargs['obj_pk'])
    
    def get_success_url(self):
        return reverse('showProject')
    

    
class AddTreatment(LoginRequiredMixin, CreateView):
    template_name = 'customForm.html'
    form_class = TreatmentForm
    
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST,request.FILES)
        if form.is_valid():
            newObject = None
            try:
                newObject = form.save(commit= False)
                newObject.created_by = self.request.user
                newObject.edited_by = self.request.user
                form.instance.json_fields = createJSON(self.request)
                newObject.save()
                
            except(forms.ValidationError):
                newObject = None
                
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' %(escape(newObject._get_pk_val()), escape(newObject)))

        
        else:
            json_values = createJSON(self.request)
            pageContext = {'form': form,'json_values':json_values}
            return render(request,self.template_name,pageContext)

class DetailTreatment(LoginRequiredMixin, View):
    template_name = 'detailClass.html'
    def get(self,request,obj_pk):
        treat = Treatment.objects.get(pk=obj_pk)
        
        context = {
            'object': treat,
        }
        
        return render(request, self.template_name, context)


class EditTreatment(LoginRequiredMixin, UpdateView):
    template_name = 'editForm.html'
    form_class = TreatmentForm
    

    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        form.instance.edited_at = timezone.now()
        form.instance.json_fields = createJSON(self.request)
        return super().form_valid(form)
    
    def get_object(self):
        return get_object_or_404(Treatment, pk=self.kwargs['obj_pk'])
    
    def get_success_url(self):
        return reverse('detailTreatment', kwargs={'obj_pk': self.kwargs['obj_pk']})

class DeleteTreatment(LoginRequiredMixin, DeleteView):
    model = Treatment
    template_name = 'delete.html'
    
    def get_success_url(self):
        return reverse('showProject')
    
    

class AddProtocol(LoginRequiredMixin, CreateView):
    template_name = 'customForm.html'
    form_class = ProtocolForm
    
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST,request.FILES)
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

    

class DetailProtocol(LoginRequiredMixin, View):
    template_name = 'detailClass.html'
    def get(self,request,obj_pk):
        pro = Protocol.objects.get(pk=obj_pk)
        
        context = {
            'object': pro,
        }
        
        return render(request, self.template_name, context)

class EditProtocol(LoginRequiredMixin, UpdateView):
    template_name = 'editForm.html'
    form_class = ProtocolForm
    

    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        form.instance.edited_at = timezone.now()
        return super().form_valid(form)
    
    def get_object(self):
        return get_object_or_404(Protocol, pk=self.kwargs['obj_pk'])
    
    def get_success_url(self):
        return reverse('detailProtocol', kwargs={'obj_pk': self.kwargs['obj_pk']})
    

class DeleteProtocol(LoginRequiredMixin, DeleteView):
    model = Protocol
    template_name = 'delete.html'
    
    def get_success_url(self):
        return reverse('showProject')

########################

##Import Sections
########################

def selectProjectforImport(request,slug):
    if request.method == 'POST':
        form = selectProjectforImportForm(request.POST, request.FILES)
        if form.is_valid():
            select_project_pk=request.POST.get('choose_project')
            if (slug=="experiments"):
                return HttpResponseRedirect('/importExperiments/'+select_project_pk)
            elif (slug=="sequencingrun"):
                return HttpResponseRedirect('/bulkAddSequencingRun/'+select_project_pk)
            elif (slug=="files"):
                return HttpResponseRedirect('/importSequencingFiles/'+select_project_pk)
            
    else:
        form = selectProjectforImportForm()

    return render(request, 'selectProject.html',{'form':form}) 


def importExperiments(request,prj_pk):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_experiments(request,request.FILES['upload_csv'])
            return HttpResponseRedirect('/detailProject/'+prj_pk)
    else:
        form = ImportForm()
     
    pageContext = {
        'form': form,
        'form_name':'experiments'
        }
    return render(request, 'upload.html', pageContext)   

def importSequencingFiles(request,prj_pk):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_sequencingfiles(request,prj_pk, request.FILES['upload_csv'])
            return HttpResponseRedirect('/detailProject/'+prj_pk)
    else:
        form = ImportForm()
     
    pageContext = {
        'form': form,
        'form_name':'sequencing fastq files'
        }
    return render(request, 'upload.html', pageContext)

def addData(request):
    return render(request, 'addData.html')

def bulkAddBiosource(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_biosource(request,request.FILES['upload_csv'])
            return HttpResponseRedirect('/showBiosource/')
    else:
        form = ImportForm()
     
    pageContext = {
        'form': form,
        'form_name':'biosource'
        }
    return render(request, 'upload.html', pageContext)

def bulkAddBiosample(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_biosample(request,request.FILES['upload_csv'])
            return HttpResponseRedirect('/showBiosource/')
    else:
        form = ImportForm()
     
    pageContext = {
        'form': form,
        'form_name':'biosample'
        }
    return render(request, 'upload.html', pageContext)

def bulkAddSequencingRun(request,prj_pk):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_sequencingruns(request,prj_pk, request.FILES['upload_csv'])
            return HttpResponseRedirect('/detailProject/'+prj_pk)
    else:
        form = ImportForm()
     
    pageContext = {
        'form': form,
        'form_name':'sequencing run'
        }
    return render(request, 'upload.html', pageContext)

from django.db.models import Count

@csrf_exempt                
def populateCharts(request,slug):
    if request.method == 'POST' and request.is_ajax():
        if (slug=="owner"):
            proj_owner=list(Project.objects.values('created_by__first_name').annotate(dcount=Count('created_by')).order_by())
            js_project=json.dumps(proj_owner)
            
        elif (slug=="assay"):
            proj_owner=list(Project.objects.values('exp_project__json_type__name').annotate(dcount=Count('exp_project__json_type__name')).order_by())
            js_project=json.dumps(proj_owner)
            
        elif (slug=="disease"):
            proj_owner=list(Project.objects.values('related__name').annotate(dcount=Count('related__name')).order_by())
            js_project=json.dumps(proj_owner)
        
        elif (slug=="status"):
            proj_owner=list(Project.objects.values('status').annotate(dcount=Count('status')).order_by())
            js_project=json.dumps(proj_owner)
            print(js_project)
            
        return JsonResponse(js_project, safe=False)
    else :
        return HttpResponse('<h1>Page was found</h1>')

