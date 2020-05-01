'''
Created on Feb. 26, 2020

@author: ankita
'''
from django.forms import ModelForm, widgets
from metadata.models import *
from django import forms
from django.forms import ModelChoiceField
from metadata.widgets import *


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        exclude = ('created_at','created_by','edited_at','edited_by',)
        fields = ('name','contributor','status','description',)

class ExperimentForm(ModelForm):
    class Meta:
        model = Experiment 
        exclude = ('created_at','created_by','edited_at','edited_by','json_fields','biosample')
        fields = ('name','bio_rep_no','tec_rep_no','modification','treatment','json_type','protocol','description')
        widgets = {
            'modification': RelatedFieldWidgetCanAdd(Modification,'addModification'),
            'treatment': RelatedFieldWidgetCanAdd(Treatment,'addTreatment'),
        }
        
        
class BiosourceForm(ModelForm):
    choose_existing = ModelChoiceField(queryset = Biosource.objects.all(),required=False,help_text='Choose from existing list')
    class Meta:
        model = Biosource
        exclude = ('created_at','created_by','edited_at','edited_by','json_fields')
        fields = ('choose_existing','name','disease','disease_ontology_uri','source_organism','description','json_type')

class BiosampleForm(ModelForm):
    choose_existing = ModelChoiceField(queryset = Biosample.objects.all(),required=False,help_text='Choose from existing list')
    
    def __init__(self, *args, **kwargs):
        source_pk = kwargs.get('initial')['source_pk']
        super(BiosampleForm, self).__init__(*args, **kwargs)
        if source_pk:
            self.fields['choose_existing'].queryset = Biosample.objects.filter(biosource=source_pk)
    
    class Meta:
        model = Biosample
        exclude = ('created_at','created_by','edited_at','edited_by','json_fields', 'biosource')
        fields = ('choose_existing','name','sample_id','sample_ontology_uri','collection_date','collection_method','delivery_date','lab_name','contact_person','contact_info','description','json_type')
        widgets = {
            'collection_date': forms.DateInput(attrs={'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ModificationForm(ModelForm):
    class Meta:
        model = Modification
        exclude = ('created_at','created_by','edited_at','edited_by')
        fields = ('name','modification_type','genomic_change','guide_rnas','description')

class TreatmentForm(ModelForm):
    class Meta:
        model = Treatment
        exclude = ('created_at','created_by','edited_at','edited_by','json_fields')
        fields = ('name','json_type','description')


class FieldsForm(forms.Form): 
    def __init__(self, *args, **kwargs):
        super(FieldsForm, self).__init__(*args)
        
        field_values=kwargs.get('initial')
        #print(field_values['field_values'].get("null"))
        null_json=("null" in field_values['field_values'])
        if(bool(field_values) and (not null_json)):
            json_field_values = sorted(field_values['field_values'].items(), key=lambda item: item[1]["order"])
            for key,values in json_field_values:
                if(values["data"]=="CharField"):
                    #self.fields[key] = getattr(forms, values["data"])(max_length=200, initial=values["old"],help_text=values["help"])
                    self.fields[key] = forms.CharField(max_length=200, initial=values["old"],help_text=values["help"])
                elif(values["data"]=="DateField"):
                    self.fields[key] = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), initial=values["old"],help_text=values["help"])
                elif(values["data"]=="FloatField"):
                    self.fields[key] = forms.FloatField(initial=values["old"],help_text=values["help"])
                elif(values["data"]=="IntegerField"):
                    self.fields[key] = forms.IntegerField(initial=values["old"],help_text=values["help"])
                elif(values["data"]=="ChoiceField"):
                    VAL_CHOICES = []
                    for k,v in values["choices"].items():
                        VAL_CHOICES.append((v,v))
                    self.fields[key] = forms.ChoiceField(choices = VAL_CHOICES, initial=values["old"],help_text=values["help"])
                if(values["required"]=="no"):
                    self.fields[key].required = False
        
        
    
    