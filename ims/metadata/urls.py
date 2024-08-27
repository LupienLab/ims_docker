'''
Created on Feb. 26, 2020

@author: ankita
'''
from django.urls import re_path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from metadata.views import *
from metadata.autocompleteForeignkey import *
from metadata.handleExport import *


urlpatterns = [
    re_path(r'^$', Rview.as_view(), name='rview'),
    #url(r'^index/(?P<username>[\w-]+)/$', Index.as_view(), name='index'),
    re_path(r'^index/$', Index.as_view(), name='index'),
    re_path(r'^keycloak_login/$', KeycloakLoginView.as_view(), name='keycloak_login'),
    # url(r'^password/$', views.change_password, name='change_password'),

    re_path(r'^showProject/$', ShowProject.as_view(), name='showProject'),
    re_path(r'^addProject/$', AddProject.as_view(), name='addProject'),
    re_path(r'^detailProject/(?P<prj_pk>[0-9]+)/$', DetailProject.as_view(), name='detailProject'),
    re_path(r'^editProject/(?P<prj_pk>[0-9]+)/$', EditProject.as_view(), name='editProject'),
    re_path(r'^deleteProject/(?P<prj_pk>[0-9]+)/$', DeleteProject.as_view(), name='deleteProject'),
    re_path(r'^browseProject/(?P<slug>[\w\ \(\)-]+)/$', BrowseProject.as_view(), name='browseProject'),

    re_path(r'^addExperiment/(?P<prj_pk>[0-9]+)/(?P<sample_pk>[0-9]+)/$', AddExperiment.as_view(), name='addExperiment'),
    re_path(r'^detailExperiment/(?P<exp_pk>[0-9]+)/$', DetailExperiment.as_view(), name='detailExperiment'),
    re_path(r'^editExperiment/(?P<exp_pk>[0-9]+)/$', EditExperiment.as_view(), name='editExperiment'),
    re_path(r'^deleteExperiment/(?P<exp_pk>[0-9]+)/$', DeleteExperiment.as_view(), name='deleteExperiment'),
    re_path(r'^browseExperimentGrid/(?P<slug_disease>[\w\ \(\)-]+)/(?P<slug_assay>[\w-]+)/$', BrowseExperimentGrid.as_view(), name='browseExperimentGrid'),
    re_path(r'^addExperimentLabels/(?P<prj_pk>[0-9]+)/$', AddExperimentLabels.as_view(), name='addExperimentLabels'),

    re_path(r'^addBiosource/(?P<prj_pk>[0-9]+)/$', AddBiosource.as_view(), name='addBiosource'),
    re_path(r'^showBiosource/$', ShowBiosource.as_view(), name='showBiosource'),
    re_path(r'^detailBiosource/(?P<source_pk>[0-9]+)/$', DetailBiosource.as_view(), name='detailBiosource'),
    re_path(r'^editBiosource/(?P<obj_pk>[0-9]+)/$', EditBiosource.as_view(), name='editBiosource'),
    re_path(r'^deleteBiosource/(?P<obj_pk>[0-9]+)/$', DeleteBiosource.as_view(), name='deleteBiosource'),

    re_path(r'^addBiosample/(?P<prj_pk>[0-9]+)/(?P<source_pk>[0-9]+)/$', AddBiosample.as_view(), name='addBiosample'),
    re_path(r'^detailBiosample/(?P<sample_pk>[0-9]+)/$', DetailBiosample.as_view(), name='detailBiosample'),
    re_path(r'^editBiosample/(?P<obj_pk>[0-9]+)/$', EditBiosample.as_view(), name='editBiosample'),
    re_path(r'^deleteBiosample/(?P<obj_pk>[0-9]+)/$', DeleteBiosample.as_view(), name='deleteBiosample'),

    re_path(r'^addSequencingRun/(?P<prj_pk>[0-9]+)/$', AddSequencingRun.as_view(), name='addSequencingRun'),
    re_path(r'^detailSequencingRun/(?P<run_pk>[0-9]+)/$', DetailSequencingRun.as_view(), name='detailSequencingRun'),
    re_path(r'^editSequencingRun/(?P<prj_pk>[0-9]+)/(?P<obj_pk>[0-9]+)/$', EditSequencingRun.as_view(), name='editSequencingRun'),
    re_path(r'^deleteSequencingRun/(?P<obj_pk>[0-9]+)/$', DeleteSequencingRun.as_view(), name='deleteSequencingRun'),
    re_path(r'^archiveSequencingRun/(?P<prj_pk>[0-9]+)/$', ArchiveSequencingRun.as_view(), name='archiveSequencingRun'),
    re_path(r'^addFastqcResults/(?P<prj_pk>[0-9]+)/$', AddFastqcResults.as_view(), name='addFastqcResults'),


    re_path(r'^addSeqencingFile/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/$', AddSeqencingFile.as_view(), name='addSeqencingFile'),
    re_path(r'^detailSeqencingFile/(?P<file_pk>[0-9]+)/$', DetailSeqencingFile.as_view(), name='detailSeqencingFile'),
    re_path(r'^editSeqencingFile/(?P<prj_pk>[0-9]+)/(?P<obj_pk>[0-9]+)/$', EditSeqencingFile.as_view(), name='editSeqencingFile'),
    re_path(r'^deleteSeqencingFile/(?P<obj_pk>[0-9]+)/$', DeleteSeqencingFile.as_view(), name='deleteSeqencingFile'),


    re_path(r'^addModification/$', AddModification.as_view(), name='addModification'),
    re_path(r'^detailModification/(?P<obj_pk>[0-9]+)/$', DetailModification.as_view(), name='detailModification'),
    re_path(r'^editModification/(?P<obj_pk>[0-9]+)/$', EditModification.as_view(), name='editModification'),
    re_path(r'^deleteModification/(?P<obj_pk>[0-9]+)/$', DeleteModification.as_view(), name='deleteModification'),



    re_path(r'^addTreatment/$', AddTreatment.as_view(), name='addTreatment'),
    re_path(r'^detailTreatment/(?P<obj_pk>[0-9]+)/$', DetailTreatment.as_view(), name='detailTreatment'),
    re_path(r'^editTreatment/(?P<obj_pk>[0-9]+)/$', EditTreatment.as_view(), name='editTreatment'),
    re_path(r'^deleteTreatment/(?P<obj_pk>[0-9]+)/$', DeleteTreatment.as_view(), name='deleteTreatment'),



    re_path(r'^addProtocol/$', AddProtocol.as_view(), name='addProtocol'),
    re_path(r'^detailProtocol/(?P<obj_pk>[0-9]+)/$', DetailProtocol.as_view(), name='detailProtocol'),
    re_path(r'^editProtocol/(?P<obj_pk>[0-9]+)/$', EditProtocol.as_view(), name='editProtocol'),
    re_path(r'^deleteProtocol/(?P<obj_pk>[0-9]+)/$', DeleteProtocol.as_view(), name='deleteProtocol'),


    re_path(r'^addFields/$', views.addFields, name='addFields'),
    re_path(r'^addData/$', views.addData, name='addData'),
    re_path(r'^populateCharts/(?P<slug>[\w-]+)/$', views.populateCharts, name='populateCharts'),
    re_path(r'^populateCharts/(?P<slug>[\w\+-]+)$', views.populateCharts, name='populateCharts'),


    re_path(r'^bulkAddBiosource/$', views.bulkAddBiosource, name='bulkAddBiosource'),
    re_path(r'^bulkAddBiosample/$', views.bulkAddBiosample, name='bulkAddBiosample'),
    re_path(r'^selectProjectforImport/(?P<slug>[\w-]+)/$', views.selectProjectforImport, name='selectProjectforImport'),
    re_path(r'^importExperiments/(?P<prj_pk>[0-9]+)/$', views.importExperiments, name='importExperiments'),
    re_path(r'^importSequencingFiles/(?P<prj_pk>[0-9]+)/$', views.importSequencingFiles, name='importSequencingFiles'),
    re_path(r'^bulkAddSequencingRun/(?P<prj_pk>[0-9]+)/$', views.bulkAddSequencingRun, name='bulkAddSequencingRun'),


    re_path(r'^biosourceAutocomplete/$',BiosourceAutocomplete.as_view(),name='biosourceAutocomplete'),
    re_path(r'^biosampleAutocomplete/$',BiosampleAutocomplete.as_view(),name='biosampleAutocomplete'),
    re_path(r'^projectAutocomplete/$',ProjectAutocomplete.as_view(),name='projectAutocomplete'),

    re_path(r'^addExperimentTag/(?P<prj_pk>[0-9]+)/$', AddExperimentTag.as_view(), name='addExperimentTag'),
    re_path(r'^detailExperimentTag/(?P<slug>[\w-]+)/$', DetailExperimentTag.as_view(), name='detailExperimentTag'),
    re_path(r'^editExperimentTag/(?P<prj_pk>[0-9]+)/(?P<obj_pk>[0-9]+)/$', EditExperimentTag.as_view(), name='editExperimentTag'),
    re_path(r'^deleteExperimentTag/(?P<obj_pk>[0-9]+)/$', DeleteExperimentTag.as_view(), name='deleteExperimentTag'),



    re_path(r'^exportSequencingform/(?P<prj_pk>[0-9]+)/$', exportSequencingform, name='exportSequencingform'),
    re_path(r'^exportform/(?P<prj_pk>[0-9]+)/(?P<slug>[\w-]+)/$', exportform, name='exportform'),
    re_path(r'^exportSequencingdata/$', exportSequencingdata, name='exportSequencingdata'),
    re_path(r'^exportnoSequencingdata/$', exportnoSequencingdata, name='exportnoSequencingdata'),



] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
