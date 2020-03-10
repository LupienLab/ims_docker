'''
Created on Feb. 26, 2020

@author: ankita
'''
from django.forms import ModelForm
from metadata.models import *

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        exclude = ('created_at','created_by','edited_at','edited_by',)
        fields = ('name','contributor','status','description',)

class ExperimentForm(ModelForm):
    class Meta:
        model = Experiment
        exclude = ('created_at','created_by','edited_at','edited_by',)
        fields = ('name','bio_rep_no','tec_rep_no','type','protocol','description',)