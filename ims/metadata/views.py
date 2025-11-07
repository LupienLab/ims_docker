from urllib.parse import unquote
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect, JsonResponse
from django.db.models import Value, CharField, F
from django.db.models.functions import Concat
from metadata.forms import *
from metadata.models import *
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.utils import timezone
from django.urls import reverse
from django.urls.base import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
import json
from django.views.decorators.csrf import csrf_exempt
from crispy_forms.utils import render_crispy_form
from django import forms
from django.utils.html import escape
from django.views.generic import DetailView
from view_breadcrumbs import DetailBreadcrumbMixin, BaseBreadcrumbMixin
from django.utils.functional import cached_property
from metadata.handle_upload import *
from django.contrib import messages
import binascii
import os
import pandas as pd
import ast
from .keycloak_client import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from ims.views import *
from user_profiles.utils import get_user_lab, is_admin
from .utils import get_projects_for_user

#import metadata.extendSession
# Create your views here.

####INDEX############

class KeycloakLoginView(LoginView):
  def get(self, request):
    login_url = get_keycloak_url(request)
    code = request.GET.get('code')
    if code:
      user_token,user_info = get_keycloak_user_token(request)
      username = user_info["preferred_username"]
      return reverse('index')
    return HttpResponseRedirect(login_url)

class Rview(View):
    def get(self,request):
        code = request.GET.get('code')
        if code:
            user_token,user_info = get_keycloak_user_token(request)
            username = user_info["preferred_username"]
            password = "imsdbuser1"
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                myusername=self.request.user.username
                request.session['myusername'] = myusername
                return HttpResponseRedirect(reverse('index'))
            else:
                logout_view2(request)
                messages.error(request, 'Unable to authenticate, please try again or contact admin')
                return HttpResponseRedirect(reverse('login'))
        else:
            return HttpResponseRedirect(reverse('index'))

class Index(LoginRequiredMixin, View):
  template_name = 'index.html'

  def get(self,request,**kwargs):
    usr = self.request.user
    context = {}
    if usr:
      projects = get_projects_for_user(usr)

      # Filter projects associated with the lab
      obj = projects.filter(status="Active").order_by('-pk').distinct('pk')
      context = {
          'object': obj,
      }
    return render(request, self.template_name, context)

class ActiveProjectsApiView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        # Filter active projects for the current user
        projects = get_projects_for_user(user).filter(status="Active").order_by('-pk').distinct('pk')

        # Serialize data for JSON response
        data = [
            {
                "name": project.name,
                "pk": project.pk,
                "url": request.build_absolute_uri(f"/detailProject/{project.pk}/")  # Adjust URL pattern as needed
            }
            for project in projects
        ]
        return JsonResponse(data, safe=False)
#######################
# def change_password(request):
#     if request.method == 'POST':
#         form = PasswordChangeForm(request.user, request.POST)
#         if form.is_valid():
#             user = form.save()
#             update_session_auth_hash(request, user)  # Important!
#             messages.success(request, 'Your password was successfully updated!')
#             return redirect('change_password')
#         else:
#             messages.error(request, 'Please correct the error below.')
#     else:
#         form = PasswordChangeForm(request.user)
#     return render(request, 'change_password.html', {
#         'form': form
#     })

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
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
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
    projects = get_projects_for_user(self.request.user)

    obj= projects.order_by('-pk')

    context = {
        'object': obj,
    }

    return render(request, self.template_name, context)

class BrowseProject(LoginRequiredMixin, View):
    template_name = 'showProject.html'

    def get(self,request,slug):
        user = request.user
        if is_admin(user):
            # Admins can see all projects matching any of the filters
            obj = Project.objects.filter(
                Q(created_by__first_name=slug) |
                Q(exp_project__json_type__name=slug) |
                Q(disease_site__name=slug) |
                Q(status=slug)
            ).order_by('-pk').distinct()
        else:
          user_lab = get_user_lab(user)
          if not user_lab:
            obj = Project.objects.none()
          else:
            obj = Project.objects.filter(
                  labs=user_lab
              ).filter(
                  Q(created_by__first_name=slug) |
                  Q(exp_project__json_type__name=slug) |
                  Q(disease_site__name=slug) |
                  Q(status=slug)
              ).order_by('-pk').distinct()

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
        prj = get_object_or_404(Project, id=self.kwargs['prj_pk'])
        usr= self.request.user
        lab = get_user_lab(usr)

        if not prj.labs.filter(id=lab.id).exists() and not is_admin(usr):
          raise PermissionDenied("You do not have access to this project.")
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

      disease_site=ChoiceDisease.objects.get(pk=self.request.POST.get('disease_site')).name
      disease_acr=disease_site.split("(")
      if(len(disease_acr)>1):
          site=disease_acr[1].split(")")[0]
      else:
          site=disease_acr[0]
      tissue_type=Choice.objects.get(pk=self.request.POST.get('tissue_type')).name

      name_string = "_".join([site,tissue_type,self.request.POST.get('user_name_string'),self.request.user.last_name,self.request.POST.get('starting_date')])


      form.instance.name = name_string

      form.save()

      return super().form_valid(form)


class EditProject(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'customForm.html'
    form_class = ProjectForm

    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        form.instance.edited_at = timezone.now()
        disease_site=ChoiceDisease.objects.get(pk=self.request.POST.get('disease_site')).name
        disease_acr=disease_site.split("(")
        if(len(disease_acr)>1):
            site=disease_acr[1].split(")")[0]
        else:
            site=disease_acr[0]
        tissue_type=Choice.objects.get(pk=self.request.POST.get('tissue_type')).name

        name_string = "_".join([site,tissue_type,self.request.POST.get('user_name_string'),self.request.user.last_name,self.request.POST.get('starting_date')])


        form.instance.name = name_string

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


class DetailBiosource(LoginRequiredMixin, BaseBreadcrumbMixin, DetailView):
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

    @cached_property
    def crumbs(self):
      return [
          ('Biosource: ' + self.object.name, reverse('detailBiosource', kwargs={'source_pk': self.object.pk}))
      ]

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
        return bio

    def get_success_url(self):
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
    biosource_pk = None

    def get_object(self):
        sample = get_object_or_404(Biosample, pk=self.kwargs['obj_pk'])
        self.biosource_pk = sample.biosource.pk
        return sample

    def get_success_url(self):
        return reverse('detailBiosource', kwargs={'source_pk': self.biosource_pk})



######################

####EXPERIMENT########

class AddExperiment(LoginRequiredMixin, CreateView):
    template_name = 'customForm.html'
    form_class = ExperimentForm

    def form_valid(self, form):
        form.instance.uid=binascii.hexlify(os.urandom(3)).decode()
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
        prj = get_object_or_404(Project, id=self.object.project.pk)
        usr= self.request.user
        lab = get_user_lab(usr)

        if not prj.labs.filter(id=lab.id).exists() and not is_admin(usr):
          raise PermissionDenied("You do not have access to this project.")
        seqfiles=context["object"].file_exp.all().order_by('pk')
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

class BrowseExperimentGrid(LoginRequiredMixin, View):
  template_name = 'showExperiments.html'

  def get(self,request,slug_disease,slug_assay):
    projects_lab= get_projects_for_user(self.request.user)
    obj = Experiment.objects.filter(json_type__name=slug_assay, project__disease_site__name=slug_disease, project__in=projects_lab).order_by('-pk').distinct()
    context = {
        'object': obj,
    }

    return render(request, self.template_name, context)

class BrowseExperimentGridApiView(LoginRequiredMixin, View):
    def get(self, request, slug_disease, slug_assay):
        # Get projects accessible to the user
        projects_lab = get_projects_for_user(request.user)
        decoded_disease = unquote(slug_disease)

        # Filter experiments by assay and disease site within user's projects
        experiments = Experiment.objects.filter(
            json_type__name=slug_assay,
            project__disease_site__name=decoded_disease,
            project__in=projects_lab
        ).order_by('-pk').distinct()

        # Serialize the experiments
        data = []
        for exp in experiments:
            # Serialize tissue types as a numbered list string
            tissue_list = "\n".join([f"({i+1}) {t.name}" for i,t in enumerate(exp.project.tissue_type.all())])

            # Optionally add target only if assay is ChIP-seq
            target = ""
            if exp.json_type and exp.json_type.name == "ChIP-seq":
                json_fields = exp.json_fields or {}
                target = json_fields.get("targeted_factor", "")

            data.append({
                "id": exp.pk,
                "project_name": exp.project.name if exp.project else "",
                "project_url": request.build_absolute_uri(f"/detailProject/{exp.project.pk}/") if exp.project else "",
                "experiment_name": exp.name,
                "experiment_url": request.build_absolute_uri(f"/detailExperiment/{exp.pk}/"),
                "tissue_type": tissue_list,
                "disease_site": exp.project.disease_site.name if exp.project and exp.project.disease_site else "",
                "assay": exp.json_type.name if exp.json_type else "",
                "target": target,
                "owner": str(exp.created_by),
            })

        return JsonResponse(data, safe=False)

class AddExperimentLabels(LoginRequiredMixin, View):
    template_name = 'addExperimentLabels.html'
    form_class = ExperimentLabelsFormSet


    def get(self,request,prj_pk):
        formset = self.form_class()
        for form in formset:
            form.fields["experiments"].queryset = Experiment.objects.filter(project_id=prj_pk)
        context = {
            'formset': formset

        }
        return render(request, self.template_name,context)

    def post(self,request,prj_pk):
        formset = self.form_class(request.POST)
        if formset.is_valid():
            for form in formset:
                cd = form.cleaned_data
                selected_experiment=cd.get("experiments")
                label=cd.get("label")
                exp=Experiment.objects.get(pk=selected_experiment.pk)
                exp.uid=label
                exp.save()

            return HttpResponseRedirect('/detailProject/'+self.kwargs['prj_pk'])
        else:
            for form in formset:
                form.fields["experiments"].queryset = Experiment.objects.filter(project_id=prj_pk)
            context = {
            'formset': formset
            }
            return render(request, self.template_name,context)


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


class ArchiveSequencingRun(LoginRequiredMixin,View):
    template_name = 'archiveRunForm.html'
    form_class = ArchiveSequencingRunForm

    def get(self,request,prj_pk):
        form = self.form_class()
        form.fields["run_name"].queryset = SequencingRun.objects.filter(project=self.kwargs['prj_pk']).order_by('-pk')
        context = {
            'form': form

        }
        return render(request, self.template_name,context)

    def post(self,request,prj_pk):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            archive_path=cd.get("archive_path")
            runs=cd.get("run_name")
            for srun in runs:
                rfiles=SeqencingFile.objects.filter(run=srun)
                if(len(rfiles)>0):
                    for file in rfiles:
                        file.archived_path=archive_path
                        file.save()
            return HttpResponseRedirect('/detailProject/'+self.kwargs['prj_pk'])
        else:
            form.fields["run_name"].queryset = SequencingRun.objects.filter(project=self.kwargs['prj_pk']).order_by('-pk')
            context = {
            'form': form
            }
            return render(request, self.template_name,context)



class AddFastqcResults(LoginRequiredMixin, View):
    template_name = 'addFastQC.html'
    form_class = AddFastqcResultsForm


    def get(self,request,prj_pk):
        form = self.form_class()
        form.fields["selected_fastqs"].queryset = SeqencingFile.objects.filter(project=prj_pk).order_by('name')

        context = {
            'form': form
        }
        return render(request, self.template_name,context)

    def post(self,request,prj_pk):
        form = self.form_class(request.POST,request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            selected_fastqs=cd.get("selected_fastqs")
            fastqc_html=request.FILES['qc_html']
            c=0
            for f in selected_fastqs:
                if(c==0):
                    c+=1
                    seq_file=f
                    seq_file.fastqc_html=fastqc_html
                    seq_file.save()
                else:
                    seq_file=f
                    seq_file.fastqc_html=selected_fastqs[0].fastqc_html
                    seq_file.save()

            messages.add_message(request, messages.SUCCESS, 'FastQC/MultiQC reports are added successfully')
            return HttpResponseRedirect('/detailProject/'+self.kwargs['prj_pk'])
        else:
            form.fields["selected_fastqs"].queryset = SeqencingFile.objects.filter(project=prj_pk).order_by('name')

            context = {
            'form': form
            }
            return render(request, self.template_name,context)



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
        exp=SeqencingFile.objects.get(pk=self.kwargs['obj_pk']).experiment.pk
        initial.update({'prj_pk': self.kwargs['prj_pk'],'exp_pk':exp})
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
########################
###Experiment Tags#######
class AddExperimentTag(LoginRequiredMixin, CreateView):
    template_name = 'customForm.html'
    form_class = ExperimentTagForm

    def get_initial(self):
        initial = super(AddExperimentTag, self).get_initial()
        initial.update({'prj_pk': self.kwargs['prj_pk']})
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        form.instance.project=Project.objects.get(pk=self.kwargs['prj_pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('detailProject', kwargs={'prj_pk':self.kwargs['prj_pk']})



class DetailExperimentTag(LoginRequiredMixin, View):
    template_name = 'detailExperimentTag.html'
    def get(self,request,slug):
        tag = ExperimentTag.objects.get(name=slug)

        context = {
            'object': tag,
        }

        return render(request, self.template_name, context)


class EditExperimentTag(LoginRequiredMixin, UpdateView):
    model = ExperimentTag
    template_name = 'editForm.html'
    form_class = ExperimentTagForm

    def get_initial(self):
        initial = super(EditExperimentTag, self).get_initial()
        initial.update({'prj_pk': self.kwargs['prj_pk']})
        return initial

    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        form.instance.edited_at = timezone.now()
        return super().form_valid(form)

    def get_object(self):
        return get_object_or_404(ExperimentTag, pk=self.kwargs['obj_pk'])

    def get_success_url(self):
        return reverse('detailProject', kwargs={'prj_pk': self.kwargs['prj_pk']})


class DeleteExperimentTag(LoginRequiredMixin, DeleteView):
    model = ExperimentTag
    template_name = 'delete.html'
    prj_pk = None

    def get_object(self):
        run = get_object_or_404(ExperimentTag, pk=self.kwargs['obj_pk'])
        self.prj_pk = run.project.pk
        return run

    def get_success_url(self):
        return reverse('detailProject', kwargs={'prj_pk': self.prj_pk})

########################


##Import Sections
########################
@login_required
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

@login_required
def importExperiments(request,prj_pk):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            df=getdf(request,request.FILES['upload_csv'])
            pageContext = {
            'target': "experiments",
            'dataFrame':df.to_html(classes='table table-bordered table-hover data_table mystyle gridjs-table'),
            'df':df.to_json()
            }
            return render(request, 'showDataFrame.html', pageContext)

        else:
            if "upload" in request.POST:
                htmlDf = pd.io.json.read_json(request.POST.get("htmldf"))
                df=pd.DataFrame.from_dict(htmlDf)
                handle_uploaded_experiments(request, df)
                return HttpResponseRedirect('/detailProject/'+prj_pk)

            elif "cancel" in request.POST:
                return HttpResponseRedirect('/addData/')

    else:
        form = ImportForm()

    pageContext = {
        'form': form,
        'form_name':'experiments'
        }
    return render(request, 'upload.html', pageContext)

@login_required
def importSequencingFiles(request,prj_pk):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            df=getdf(request,request.FILES['upload_csv'])
            pageContext = {
            'target': "sequencing files",
            'dataFrame':df.to_html(classes='table table-bordered table-hover data_table mystyle gridjs-table'),
            'df':df.to_json()
            }
            return render(request, 'showDataFrame.html', pageContext)

        else:
            if "upload" in request.POST:
                htmlDf = pd.io.json.read_json(request.POST.get("htmldf"))
                df=pd.DataFrame.from_dict(htmlDf)
                handle_uploaded_sequencingfiles(request,prj_pk,df)
                return HttpResponseRedirect('/detailProject/'+prj_pk)

            elif "cancel" in request.POST:
                return HttpResponseRedirect('/addData/')

    else:
        form = ImportForm()

    pageContext = {
        'form': form,
        'form_name':'sequencing fastq files'
        }
    return render(request, 'upload.html', pageContext)

@login_required
def addData(request):
    return render(request, 'addData.html')

@login_required
def bulkAddBiosource(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            df=getdf(request,request.FILES['upload_csv'])
            pageContext = {
            'target': "biosource",
            'dataFrame':df.to_html(classes='table table-bordered table-hover data_table mystyle gridjs-table'),
            'df':df.to_json()
            }
            return render(request, 'showDataFrame.html', pageContext)

        else:
            if "upload" in request.POST:
                htmlDf = pd.io.json.read_json(request.POST.get("htmldf"))
                df=pd.DataFrame.from_dict(htmlDf)
                handle_uploaded_biosource(request, df)
                return HttpResponseRedirect('/showBiosource/')

            elif "cancel" in request.POST:
                return HttpResponseRedirect('/addData/')

    else:
        form = ImportForm()

    pageContext = {
        'form': form,
        'form_name':'biosource'
        }
    return render(request, 'upload.html', pageContext)

@login_required
def bulkAddBiosample(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            df=getdf(request,request.FILES['upload_csv'])
            pageContext = {
            'target': "biosample",
            'dataFrame':df.to_html(classes='table table-bordered table-hover data_table mystyle gridjs-table'),
            'df':df.to_json()
            }
            return render(request, 'showDataFrame.html', pageContext)

        else:
            if "upload" in request.POST:
                htmlDf = pd.io.json.read_json(request.POST.get("htmldf"))
                df=pd.DataFrame.from_dict(htmlDf)
                handle_uploaded_biosample(request, df)
                return HttpResponseRedirect('/showBiosource/')

            elif "cancel" in request.POST:
                return HttpResponseRedirect('/addData/')

    else:
        form = ImportForm()

    pageContext = {
        'form': form,
        'form_name':'biosample'
        }
    return render(request, 'upload.html', pageContext)

@login_required
def bulkAddSequencingRun(request,prj_pk):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            df=getdf(request,request.FILES['upload_csv'])
            pageContext = {
            'target': "sequencing run",
            'dataFrame':df.to_html(classes='table table-bordered table-hover data_table mystyle gridjs-table'),
            'df':df.to_json()
            }
            return render(request, 'showDataFrame.html', pageContext)

        else:
            if "upload" in request.POST:
                htmlDf = pd.io.json.read_json(request.POST.get("htmldf"))
                df=pd.DataFrame.from_dict(htmlDf)
                handle_uploaded_sequencingruns(request,prj_pk,df)
                return HttpResponseRedirect('/detailProject/'+prj_pk)

            elif "cancel" in request.POST:
                return HttpResponseRedirect('/addData/')

    else:
        form = ImportForm()

    pageContext = {
        'form': form,
        'form_name':'sequencing run'
        }
    return render(request, 'upload.html', pageContext)

from django.db.models import Count

@login_required
def get_owners(request):
    owners = Project.objects.annotate(
        full_name=Concat(
            F('created_by__first_name'),
            Value(' '),
            F('created_by__last_name'),
            output_field=CharField()
        )
    ).values('created_by__id', 'full_name').distinct().order_by('full_name')

    owner_list = [{'id': o['created_by__id'], 'name': o['full_name']} for o in owners]

    return JsonResponse(owner_list, safe=False)

@login_required
def get_statuses(request):
    statuses = Project.objects.values_list('status', flat=True).distinct().order_by('status')
    return JsonResponse(list(statuses), safe=False)

@login_required
def get_diseases(request):
    diseases = Project.objects.values_list('disease_site__name', flat=True).distinct().order_by('disease_site__name')
    return JsonResponse(list(diseases), safe=False)

@csrf_exempt
@login_required
def populateDashboard(request, slug):
    # Accept both POST and GET for flexibility
    params = request.POST if request.method == 'POST' else request.GET

    owner_filter = params.get('owner')
    status_filter = params.get('status')
    disease_filter = params.get('disease')

    queryset = Project.objects.all()

    # Apply filters if present
    if owner_filter:
        queryset = queryset.filter(created_by__id=owner_filter)
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if disease_filter:
        queryset = queryset.filter(disease_site__name=disease_filter)

    if slug == "owner":
      # Annotate full name by concatenating first and last name for clarity (optional)
      data = list(
          queryset.annotate(
              full_name=Concat(
                  F('created_by__first_name'),
                  Value(' '),
                  F('created_by__last_name'),
                  output_field=CharField()
              )
          )
          .values('created_by__id', 'full_name', 'disease_site__name')
          .annotate(dcount=Count('id'))
          .order_by('full_name', 'disease_site__name')
      )

      # Extract unique owners and diseases using IDs and names
      owners = sorted({(item['created_by__id'], item['full_name']) for item in data})
      diseases = sorted(set(item['disease_site__name'] for item in data if item['disease_site__name']))

      # Create a mapping from owner id to index
      owner_index = {owner[0]: idx for idx, owner in enumerate(owners)}

      # Initialize counts dictionary (disease -> counts list aligned with owners)
      counts = {disease: [0] * len(owners) for disease in diseases}

      for item in data:
          if item['disease_site__name']:
              owner_id = item['created_by__id']
              counts[item['disease_site__name']][owner_index[owner_id]] = item['dcount']

      # Convert owners from tuple(id, name) to list of dicts for frontend ease
      owners_list = [{'id': o[0], 'name': o[1]} for o in owners]

      return JsonResponse({'owners': owners_list, 'diseases': diseases, 'counts': counts})

    if slug == "assay":
        data = list(queryset.values('exp_project__json_type__name')
                    .exclude(exp_project__json_type__name__isnull=True)
                    .annotate(dcount=Count('exp_project__json_type__name'))
                    .order_by())
        for item in data:
          item['assay_type'] = item.pop('exp_project__json_type__name')
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

@csrf_exempt
@login_required
def populateCharts(request,slug):
  if request.method == 'POST':
    if (slug=="owner"):
      proj_owner=list(Project.objects.values('created_by__first_name').annotate(dcount=Count('created_by')).order_by())
      js_project=json.dumps(proj_owner)

    elif (slug=="assay"):
      proj_owner=list(Project.objects.values('exp_project__json_type__name').exclude(exp_project__json_type__name__isnull=True).annotate(dcount=Count('exp_project__json_type__name')).order_by())
      js_project=json.dumps(proj_owner)

    elif (slug=="disease"):
      proj_owner=list(Project.objects.values('disease_site__name').annotate(dcount=Count('disease_site__name')).order_by())
      js_project=json.dumps(proj_owner)

    elif (slug=="status"):
      proj_owner=list(Project.objects.values('status').annotate(dcount=Count('status')).order_by())
      js_project=json.dumps(proj_owner)

    elif (slug.startswith("tags")):
      s=slug.split("_")
      tag_experiments=list(ExperimentTag.objects.filter(project=s[1]).values('name').annotate(dcount=Count('experiment')).order_by())
      js_project=json.dumps(tag_experiments)

    elif (slug.startswith("grid")):
      slug_vals=slug.split("+")
      diseaseList=list(ChoiceDisease.objects.filter(class_type="disease_site").values_list('name', flat=True).order_by('id'))
      assayList=list(JsonObj.objects.filter(json_type="experiment_type").values_list('name', flat=True).order_by('id'))
      cancer_matrix = []
      data = {}
      data['Disease-site'] = diseaseList
      for row in diseaseList:
        for col in assayList:
          if(data.get(col) is None):
            data[col] = []
          no_of_exp=len(Experiment.objects.filter(json_type__name=col, project__disease_site__name=row))
          data[col].append(no_of_exp)

      # Create a DataFrame
      df = pd.DataFrame(data)

      # Sort the DataFrame by the 'ATAC-seq' column in descending order
      if(len(slug_vals) > 1):
        sorted_df = df.sort_values(by=slug_vals[1], ascending=ast.literal_eval(slug_vals[2]))
      else:
        sorted_df = df

      # Remove rows where the sum of numeric values is zero
      filtered_df = sorted_df[sorted_df[assayList].sum(axis=1) != 0]

      return JsonResponse(filtered_df.to_dict(orient='records'), safe=False)

    return JsonResponse(js_project, safe=False)
  else :
    return HttpResponse('<h1>Page was found</h1>')

