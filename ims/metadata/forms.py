'''
Created on Feb. 26, 2020

@author: ankita
'''
from django.forms import ModelForm
from metadata.models import *

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        exclude = ('created_at','created_by','edited_at','edited_by','owner')
        #exclude = ('',)