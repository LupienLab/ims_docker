'''
Created on Feb. 26, 2020

@author: ankita
'''
from django.forms import ModelForm, widgets
from metadata.models import *
from django import forms
from django.forms import ModelChoiceField
from metadata.widgets import *
from dal import autocomplete
from dal import forward
from ims import settings
from django.forms import formset_factory

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        exclude = ('name','created_at','created_by','edited_at','edited_by','lab_name', 'labs')
        fields = ('user_name_string','starting_date','disease_site','tissue_type','contributor','status','description',)
        #fields = ('contributor','status','description',)

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        #self.fields['origin'].queryset = self.fields['origin'].queryset.order_by('name')



class ExperimentForm(ModelForm):
    class Meta:
        model = Experiment
        exclude = ('created_at','created_by','edited_at','edited_by','json_fields','biosample','uid')
        fields = ('name','biosample_quantity','biosample_quantity_units','concentration_of_sample','volume_of_sample','bio_rep_no','tec_rep_no','json_type','protocol','description')
        widgets = {
            'protocol': RelatedFieldWidgetCanAdd(Treatment,'addProtocol'),
        }


class BiosourceForm(ModelForm):
    choose_existing = ModelChoiceField(queryset = Biosource.objects.all(),required=False, widget=autocomplete.ModelSelect2(url='biosourceAutocomplete'), help_text='Choose from existing list')
    class Meta:
        model = Biosource
        exclude = ('created_at','created_by','edited_at','edited_by','json_fields')
        fields = ('choose_existing','name','disease','source_organism','description','json_type')

class BiosampleForm(ModelForm):

    choose_existing = ModelChoiceField(queryset = Biosample.objects.all(),required=False, help_text='Choose from existing list')

    def __init__(self, *args, **kwargs):
        source_pk = kwargs.get('initial')['source_pk']

        super(BiosampleForm, self).__init__(*args, **kwargs)
        if source_pk:

            self.fields['choose_existing'] = ModelChoiceField(queryset = Biosample.objects.all(),required=False,widget=autocomplete.ModelSelect2(url='biosampleAutocomplete',forward=(forward.Const(source_pk, 'f4'),)), help_text='Choose from existing list')

    class Meta:
        model = Biosample
        exclude = ('created_at','created_by','edited_at','edited_by','json_fields', 'biosource')
        fields = ('choose_existing','name','sample_id','collection_date','modification','treatment','collection_method','delivery_date','lab_name','contact_person','contact_info','description','json_type')
        widgets = {
            'collection_date': forms.DateInput(),
            'delivery_date': forms.DateInput(),
            'modification': RelatedFieldWidgetCanAdd(Modification,'addModification'),
            'treatment': RelatedFieldWidgetCanAdd(Treatment,'addTreatment'),
        }

class ModificationForm(ModelForm):
    class Meta:
        model = Modification
        exclude = ('created_at','created_by','edited_at','edited_by')
        fields = ('name','attachment','modification_type','genomic_change','guide_rnas','description')

class TreatmentForm(ModelForm):
    class Meta:
        model = Treatment
        exclude = ('created_at','created_by','edited_at','edited_by','json_fields')
        fields = ('name','attachment','json_type','description')

class ProtocolForm(ModelForm):
    class Meta:
        model = Protocol
        exclude = ('created_at','created_by','edited_at','edited_by')
        fields = ('name','attachment','class_type','description')

class SequencingRunForm(ModelForm):
    class Meta:
        model = SequencingRun
        exclude = ('created_at','created_by','edited_at','edited_by','project',)
        fields = ('name','sequencing_center','sequencing_instrument','experiment','submission_date','retrieval_date','description',)
        widgets = {
            'submission_date': forms.DateInput(),
            'retrieval_date': forms.DateInput(),
        }

    def __init__(self, *args, **kwargs):
        prj_pk = kwargs.get('initial')['prj_pk']
        super(SequencingRunForm, self).__init__(*args, **kwargs)
        if prj_pk:
            self.fields['experiment'].queryset = Experiment.objects.filter(project=prj_pk).order_by('-pk')


class SeqencingFileForm(ModelForm):
    class Meta:
        model = SeqencingFile
        exclude = ('created_at','created_by','edited_at','edited_by','project','experiment')
        fields = ('name','file_format','assay','paired_end','related_files','read_length','cluster_path','duplicate_path','archived_path','md5sum','fastqc_html','run','description',)

    def __init__(self, *args, **kwargs):
        prj_pk = kwargs.get('initial')['prj_pk']
        exp_pk = kwargs.get('initial')['exp_pk']
        super(SeqencingFileForm, self).__init__(*args, **kwargs)
        if prj_pk:
            self.fields['run'].queryset = SequencingRun.objects.filter(project=prj_pk).order_by('-pk')
        if exp_pk:
            self.fields['related_files'].queryset = SeqencingFile.objects.filter(experiment=exp_pk).order_by('-pk')


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
                elif(values["data"]=="Textarea"):
                    self.fields[key] = forms.CharField(widget=forms.Textarea, initial=values["old"],help_text=values["help"])
                elif(values["data"]=="DateField"):
                    self.fields[key] = forms.DateField(widget=forms.widgets.DateInput(), initial=values["old"],help_text=values["help"])
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


class ImportForm(forms.Form):
    upload_csv=forms.FileField()

class selectProjectforImportForm(forms.Form):
    choose_project = ModelChoiceField(queryset = Project.objects.all(),required=False, widget=autocomplete.ModelSelect2(url='projectAutocomplete'), help_text='Choose project from existing list for bulk upload')

class ExperimentTagForm(ModelForm):
    class Meta:
        model = ExperimentTag
        exclude = ('created_at','created_by','edited_at','edited_by','project')
        fields = ('name','experiment','description')

    def __init__(self, *args, **kwargs):
        prj_pk = kwargs.get('initial')['prj_pk']
        super(ExperimentTagForm, self).__init__(*args, **kwargs)
        if prj_pk:
            self.fields['experiment'].queryset = Experiment.objects.filter(project=prj_pk).order_by('-pk')


class SequencingForm(forms.Form):
    BP_CHOICES= [
    ('50bp', '50bp'),
    ('100bp', '100bp'),
    ('75bp', '75bp'),
    ('36bp', '36bp')
    ]
    SAMPLE_CHOICES=[
        ('No','No'),
        ('Yes','Yes')
        ]
    SEQ_CHOICES=[
        ('Paired-end','Paired-end'),
        ('Single Read','Single Read')
        ]

    choose_experiments = forms.ModelMultipleChoiceField(queryset = Experiment.objects.all(), help_text="select all experiments to export")
    data_recipient_contact_name=forms.CharField(max_length=100, help_text="Data recipient contact name")
    data_recipient_contact_email=forms.EmailField()
    grant=forms.CharField(max_length=100,required=False, help_text="Grant or PO Number")
    buffer = forms.CharField(max_length=100, required=False, help_text="Buffer or media EB, PBS, Water, etc")
    bp_length = forms.CharField(widget=forms.Select(choices=BP_CHOICES),help_text="bp length for sequencing")
    low_diversity_sample = forms.CharField(widget=forms.Select(choices=SAMPLE_CHOICES),help_text="Low diversity sample")
    sequencing_type = forms.CharField(widget=forms.Select(choices=SEQ_CHOICES),help_text="Sequencing Type")
    multiplexing_sequencing = forms.CharField(widget=forms.Select(choices=SAMPLE_CHOICES),help_text="Multiplexing Sequencing")
    instructions = forms.CharField(widget=forms.Textarea, required=False, help_text="Experimental Conditions and Sequencing Instructions")

    class Meta:
        fields = ('choose_experiments','data_recipient_contact_name','data_recipient_contact_email','buffer','instructions')

    def __init__(self, *args, **kwargs):
        prj_pk = kwargs.get('initial')['prj_pk']
        super(SequencingForm, self).__init__(*args, **kwargs)
        if prj_pk:
            self.fields['choose_experiments'].queryset = Experiment.objects.filter(project=prj_pk).order_by('-pk')



class selectExperimentsForm(forms.Form):
    choose_experiments = forms.ModelMultipleChoiceField(queryset = Experiment.objects.all(), help_text="select all experiments to be exported")

    def __init__(self, *args, **kwargs):
        prj_pk = kwargs.get('initial')['prj_pk']
        super(selectExperimentsForm, self).__init__(*args, **kwargs)
        if prj_pk:
            self.fields['choose_experiments'].queryset = Experiment.objects.filter(project=prj_pk).order_by('-pk')


class ExperimentLabelsForm(forms.Form):
    experiments = forms.ModelChoiceField (Experiment.objects.all(), required=True,
                                                   help_text="Select an experiment.")

    label = forms.CharField(
        label='Experiment label',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter experiment label here'
        })
    )

    def __init__(self, *args, **kwargs):
        super(ExperimentLabelsForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False


ExperimentLabelsFormSet = formset_factory(ExperimentLabelsForm, extra=1)

class ArchiveSequencingRunForm(forms.Form):
    run_name = forms.ModelMultipleChoiceField(queryset = SequencingRun.objects.all(), help_text="Run to be archived. All related sequencing file path will be updated with the archived path.")
    archive_path = forms.CharField(max_length=1000, help_text="S3 path, where files are archived")

    def __init__(self, *args, **kwargs):
        super(ArchiveSequencingRunForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False



class AddFastqcResultsForm(forms.Form):
    qc_html=forms.FileField()
    selected_fastqs = forms.ModelMultipleChoiceField(queryset = SeqencingFile.objects.all(), help_text="select fastqs files for added in these results",
                                                widget = forms.CheckboxSelectMultiple())


    def __init__(self, *args, **kwargs):
        super(AddFastqcResultsForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False



