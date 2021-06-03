'''
Created on Feb. 26, 2020

@author: ankita
'''
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from . import views
from metadata.views import *
from metadata.autocompleteForeignkey import *
from metadata.handleExport import *


urlpatterns = [
    url(r'^$', Index.as_view(), name='index'),
    url(r'^password/$', views.change_password, name='change_password'),
    
    url(r'^showProject/$', ShowProject.as_view(), name='showProject'),
    url(r'^addProject/$', AddProject.as_view(), name='addProject'),
    url(r'^detailProject/(?P<prj_pk>[0-9]+)/$', DetailProject.as_view(), name='detailProject'),
    url(r'^editProject/(?P<prj_pk>[0-9]+)/$', EditProject.as_view(), name='editProject'),
    url(r'^deleteProject/(?P<prj_pk>[0-9]+)/$', DeleteProject.as_view(), name='deleteProject'),
    url(r'^browseProject/(?P<slug>[\w\ \(\)-]+)/$', BrowseProject.as_view(), name='browseProject'),
    
    url(r'^addExperiment/(?P<prj_pk>[0-9]+)/(?P<sample_pk>[0-9]+)/$', AddExperiment.as_view(), name='addExperiment'),
    url(r'^detailExperiment/(?P<exp_pk>[0-9]+)/$', DetailExperiment.as_view(), name='detailExperiment'),
    url(r'^editExperiment/(?P<exp_pk>[0-9]+)/$', EditExperiment.as_view(), name='editExperiment'),
    url(r'^deleteExperiment/(?P<exp_pk>[0-9]+)/$', DeleteExperiment.as_view(), name='deleteExperiment'),
    url(r'^browseExperimentGrid/(?P<slug_disease>[\w\ \(\)-]+)/(?P<slug_assay>[\w-]+)/$', BrowseExperimentGrid.as_view(), name='browseExperimentGrid'),
    url(r'^addExperimentLabels/(?P<prj_pk>[0-9]+)/$', AddExperimentLabels.as_view(), name='addExperimentLabels'),
    
    url(r'^addBiosource/(?P<prj_pk>[0-9]+)/$', AddBiosource.as_view(), name='addBiosource'),
    url(r'^showBiosource/$', ShowBiosource.as_view(), name='showBiosource'),
    url(r'^detailBiosource/(?P<source_pk>[0-9]+)/$', DetailBiosource.as_view(), name='detailBiosource'),
    url(r'^editBiosource/(?P<obj_pk>[0-9]+)/$', EditBiosource.as_view(), name='editBiosource'),
    url(r'^deleteBiosource/(?P<obj_pk>[0-9]+)/$', DeleteBiosource.as_view(), name='deleteBiosource'),
    
    url(r'^addBiosample/(?P<prj_pk>[0-9]+)/(?P<source_pk>[0-9]+)/$', AddBiosample.as_view(), name='addBiosample'),
    url(r'^detailBiosample/(?P<sample_pk>[0-9]+)/$', DetailBiosample.as_view(), name='detailBiosample'),
    url(r'^editBiosample/(?P<obj_pk>[0-9]+)/$', EditBiosample.as_view(), name='editBiosample'),
    url(r'^deleteBiosample/(?P<obj_pk>[0-9]+)/$', DeleteBiosample.as_view(), name='deleteBiosample'),
    
    url(r'^addSequencingRun/(?P<prj_pk>[0-9]+)/$', AddSequencingRun.as_view(), name='addSequencingRun'),
    url(r'^detailSequencingRun/(?P<run_pk>[0-9]+)/$', DetailSequencingRun.as_view(), name='detailSequencingRun'),
    url(r'^editSequencingRun/(?P<prj_pk>[0-9]+)/(?P<obj_pk>[0-9]+)/$', EditSequencingRun.as_view(), name='editSequencingRun'),
    url(r'^deleteSequencingRun/(?P<obj_pk>[0-9]+)/$', DeleteSequencingRun.as_view(), name='deleteSequencingRun'),
    
    url(r'^addSeqencingFile/(?P<prj_pk>[0-9]+)/(?P<exp_pk>[0-9]+)/$', AddSeqencingFile.as_view(), name='addSeqencingFile'),
    url(r'^detailSeqencingFile/(?P<file_pk>[0-9]+)/$', DetailSeqencingFile.as_view(), name='detailSeqencingFile'),
    url(r'^editSeqencingFile/(?P<prj_pk>[0-9]+)/(?P<obj_pk>[0-9]+)/$', EditSeqencingFile.as_view(), name='editSeqencingFile'),
    url(r'^deleteSeqencingFile/(?P<obj_pk>[0-9]+)/$', DeleteSeqencingFile.as_view(), name='deleteSeqencingFile'),
    

    url(r'^addModification/$', AddModification.as_view(), name='addModification'),
    url(r'^detailModification/(?P<obj_pk>[0-9]+)/$', DetailModification.as_view(), name='detailModification'),
    url(r'^editModification/(?P<obj_pk>[0-9]+)/$', EditModification.as_view(), name='editModification'),
    url(r'^deleteModification/(?P<obj_pk>[0-9]+)/$', DeleteModification.as_view(), name='deleteModification'),
    
    
    
    url(r'^addTreatment/$', AddTreatment.as_view(), name='addTreatment'),
    url(r'^detailTreatment/(?P<obj_pk>[0-9]+)/$', DetailTreatment.as_view(), name='detailTreatment'),
    url(r'^editTreatment/(?P<obj_pk>[0-9]+)/$', EditTreatment.as_view(), name='editTreatment'),
    url(r'^deleteTreatment/(?P<obj_pk>[0-9]+)/$', DeleteTreatment.as_view(), name='deleteTreatment'),
    
    
    
    url(r'^addProtocol/$', AddProtocol.as_view(), name='addProtocol'),
    url(r'^detailProtocol/(?P<obj_pk>[0-9]+)/$', DetailProtocol.as_view(), name='detailProtocol'),
    url(r'^editProtocol/(?P<obj_pk>[0-9]+)/$', EditProtocol.as_view(), name='editProtocol'),
    url(r'^deleteProtocol/(?P<obj_pk>[0-9]+)/$', DeleteProtocol.as_view(), name='deleteProtocol'),
    
    
    url(r'^addFields/$', views.addFields, name='addFields'),
    url(r'^addData/$', views.addData, name='addData'),
    url(r'^populateCharts/(?P<slug>[\w-]+)/$', views.populateCharts, name='populateCharts'),
    url(r'^populateCharts/(?P<slug>[\w\+-]+)$', views.populateCharts, name='populateCharts'),
    
    
    url(r'^bulkAddBiosource/$', views.bulkAddBiosource, name='bulkAddBiosource'),
    url(r'^bulkAddBiosample/$', views.bulkAddBiosample, name='bulkAddBiosample'),
    url(r'^selectProjectforImport/(?P<slug>[\w-]+)/$', views.selectProjectforImport, name='selectProjectforImport'),
    url(r'^importExperiments/(?P<prj_pk>[0-9]+)/$', views.importExperiments, name='importExperiments'),
    url(r'^importSequencingFiles/(?P<prj_pk>[0-9]+)/$', views.importSequencingFiles, name='importSequencingFiles'),
    url(r'^bulkAddSequencingRun/(?P<prj_pk>[0-9]+)/$', views.bulkAddSequencingRun, name='bulkAddSequencingRun'),
    
    
    url(r'^biosourceAutocomplete/$',BiosourceAutocomplete.as_view(),name='biosourceAutocomplete'),
    url(r'^biosampleAutocomplete/$',BiosampleAutocomplete.as_view(),name='biosampleAutocomplete'),
    url(r'^projectAutocomplete/$',ProjectAutocomplete.as_view(),name='projectAutocomplete'),
    
    url(r'^addExperimentTag/(?P<prj_pk>[0-9]+)/$', AddExperimentTag.as_view(), name='addExperimentTag'),
    url(r'^detailExperimentTag/(?P<slug>[\w-]+)/$', DetailExperimentTag.as_view(), name='detailExperimentTag'),
    url(r'^editExperimentTag/(?P<prj_pk>[0-9]+)/(?P<obj_pk>[0-9]+)/$', EditExperimentTag.as_view(), name='editExperimentTag'),
    url(r'^deleteExperimentTag/(?P<obj_pk>[0-9]+)/$', DeleteExperimentTag.as_view(), name='deleteExperimentTag'),
    
    
    
    url(r'^exportSequencingform/(?P<prj_pk>[0-9]+)/$', exportSequencingform, name='exportSequencingform'),
    url(r'^exportform/(?P<prj_pk>[0-9]+)/(?P<slug>[\w-]+)/$', exportform, name='exportform'),
    
    

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
