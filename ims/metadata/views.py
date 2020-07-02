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
from django.views.generic import DetailView
from view_breadcrumbs import BaseBreadcrumbMixin, ListBreadcrumbMixin, DetailBreadcrumbMixin
from django.utils.functional import cached_property

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

class DetailProject(LoginRequiredMixin, View, DetailBreadcrumbMixin):
    template_name = 'detailProject.html'
    def get(self,request,prj_pk):
        prj = Project.objects.get(pk=prj_pk)
        exp = Experiment.objects.filter(project=prj_pk).order_by('-pk')
        run = SequencingRun.objects.filter(project=prj_pk).order_by('-pk')
        context = {
            'project': prj,
            'experiment': exp,
            'sequencingRun': run
        }
        
        return render(request, self.template_name, context)
    
    @cached_property
    def crumbs(self):
        return [('Project:', reverse('detailProject', kwargs={'prj_pk': self.kwargs['prj_pk']}))]
        
      

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
    
    
class DetailBiosource(LoginRequiredMixin, DetailBreadcrumbMixin, DetailView):
    template_name = 'detailClass.html'
    model = Biosource
    pk_url_kwarg = 'source_pk'
    

    @cached_property
    def crumbs(self):
        return [('Biosource:', reverse('detailBiosource', kwargs={'source_pk': self.kwargs['source_pk']}))]
        
         
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
    
    def get_success_url(self):
        return reverse('detailProject', kwargs={'prj_pk':self.kwargs['prj_pk']})
    



class DetailExperiment(LoginRequiredMixin, DetailBreadcrumbMixin, DetailView):
    template_name = 'detailExperiment.html'
    model = Experiment
    pk_url_kwarg = 'exp_pk'
    

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
        initial.update({'prj_pk': self.kwargs['prj_pk']})
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

########################

##Import Sections
########################

# class ImportExperiments(LoginRequiredMixin, View):
#     template_name = 'customForm.html'
#     form_class = ImportForm
#     
#     def post(self, request, *args, **kwargs):
#         prj_pk=self.kwargs['prj_pk']
#         form = self.form_class(request.POST, request.FILES)
#         if form.is_valid():
#             handle_uploaded_file(request.FILES['file'])
#             return HttpResponseRedirect('/success/url/')
#         else:
#             form = self.form_class()
#             
#         pageContext = {'form': form}
#         return render(request,self.template_name,pageContext)
#     
from metadata.handle_upload import handle_uploaded_experiments
def importExperiments(request,prj_pk):
    if request.method == 'POST':
        print("post")
        form = ImportForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            print("hi")
            handle_uploaded_experiments(request.FILES['upload_csv'])
            return HttpResponseRedirect('/detailProject/'+prj_pk)
    else:
        form = ImportForm()
     
    pageContext = {
        'form': form,
        'form_name':'Experiments'
        }
    return render(request, 'upload.html', pageContext)   


# class importExperiments(View): 
#     template_name = 'upload.html'
#     form_class = ImportForm
#     
#     def get(self, *args, **kwargs):
#         form = self.form_class()
#         return render(self.request, self.template_name,{'form':form, 'form_class':"Experiments"})
#     
#     def post(self, *args, **kwargs):
#         prj_pk=self.kwargs['prj_pk']
#         form = self.form_class(self.request.POST, self.request.FILES)
#         if form.is_valid():
#             handle_uploaded_experiments(self.request.FILES['file'])
#             return HttpResponseRedirect('detailProject/'+prj_pk)
#         else:
#             return render(request, self.template_name,{'form':form, 'form_class':"Experiments"})




