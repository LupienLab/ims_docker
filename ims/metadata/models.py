from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from metadata.validators import alphanumeric

# Create your models here.


class UserLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this object is added to the system")
    created_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_created',
                                   on_delete=models.CASCADE, help_text="Who created this object",)
    edited_at = models.DateTimeField(auto_now_add=True, verbose_name="Last edited at", help_text="When this object was edited last")
    edited_by = models.ForeignKey(User, verbose_name="Last edited by", related_name='%(app_label)s_%(class)s_edited',
                                  on_delete=models.CASCADE, help_text="Who edited this object last")
    description = models.TextField(null=True, blank=True, help_text="Notes for the object")
    
    class Meta:
        abstract = True

class Choice(models.Model):
    name = models.CharField(max_length=50, null=False, help_text="Name of the choice")
    class_type = models.CharField(max_length=50, null=False, help_text="Class/type of the choice")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['class_type'] 

class Contributing_Lab(models.Model):
    def contact_default():
        return ('to1@example.com')

    lab_name = models.ForeignKey(Choice, verbose_name="contributing lab", related_name='lab_name', limit_choices_to={'class_type': "lab_name"}, null=True, blank=True, on_delete=models.SET_NULL, help_text="Name of the contributing lab")
    contact_person = models.CharField(max_length=100, null=True, blank=True, help_text="Name of contact person")
    contact_info = models.EmailField(max_length=254, null=True, blank=True, help_text="Email id for contact person")
    delivery_date = models.DateField(null=True, blank=True, help_text="Delivery date for the object")

    class Meta:
        abstract = True
         
    
class Project(UserLog):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Archived', 'Archived'),
    )
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the project")
    contributor = models.ManyToManyField(
        User, related_name='project_contibutor', blank=True, help_text="Collaborating members for this project")
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default="Active",
                              help_text="Is project currently in progress")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        


class Protocol(UserLog):
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the protocol")
    attachment = models.FileField(upload_to='uploads/', null=True, blank=True)
    class_type = models.ForeignKey(Choice, limit_choices_to={'class_type': "protocol_type"}, null=True, blank=True, on_delete=models.SET_NULL, help_text="The category that best describes the protocol or document")
    
    def __str__(self):
        return self.name

class JsonObj(models.Model): 
    def fields_default():
        return {"null": ""}
    
    name = models.CharField(max_length=500, unique=True, help_text="Name of the object")
    json_type = models.CharField(max_length=50, null=False, help_text="Class/type of the object")
    json_fields = JSONField(default=fields_default) 
    
    def __str__(self):
        return self.name

class Biosource(UserLog):
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the Biosource")
    disease=models.CharField(max_length=500, null=True, blank=True, help_text="Name of the disease")
    disease_ontology_uri= models.CharField(max_length=500, null=True, blank=True, help_text="disease ontology uri")
    source_organism = models.ForeignKey(Choice, related_name='source_organism', limit_choices_to={'class_type': "source_organism"}, null=True, blank=True, on_delete=models.SET_NULL, help_text="Source of the biomaterial/biosource")
    json_type = models.ForeignKey(JsonObj, verbose_name="biomaterial type" ,related_name='biomaterial_type', limit_choices_to={'json_type': "biomaterial_type"}, on_delete=models.CASCADE, help_text="The categorization of the biomaterial/biosource")
    json_fields = JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    
class Biosample(UserLog, Contributing_Lab):
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the biosample")
    biosource = models.ForeignKey(Biosource,related_name='sample_source', null=False, on_delete=models.CASCADE, help_text="Related biosource")
    sample_id = models.CharField(max_length=100, null=False, default="", help_text="Sample id")
    sample_ontology_uri= models.CharField(max_length=500, null=True, blank=True, help_text="Sample ontology uri")
    collection_date = models.DateField(help_text="Collection date for this biosample")
    collection_method = models.CharField(max_length=100, null=True, blank=True, help_text="Method of collection for this biosample")
    json_type = models.ForeignKey(JsonObj, verbose_name="cell culture details" ,related_name='cell_culture_details', limit_choices_to={'json_type': "cell_culture_details"}, on_delete=models.CASCADE, help_text="Cell culture details of sample")
    json_fields = JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.name 
 
    
class Modification(UserLog):
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the modification")
    modification_type = models.ForeignKey(Choice, limit_choices_to={'class_type': "modification_type"}, related_name='modification_type', null=True, blank=True, on_delete=models.SET_NULL, help_text="The method used to make the genomic modification")
    genomic_change = models.ForeignKey(Choice, limit_choices_to={'class_type': "genomic_change"}, related_name='genomic_change', null=True, blank=True, on_delete=models.SET_NULL, help_text="The method used to make the genomic modification")
    guide_rnas = models.CharField(max_length=100, null=True, blank=True, help_text="The guide RNA sequences used in Crispr targetting")
    
    def __str__(self):
        return self.name
    
class Treatment(UserLog): 
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the treatment")
    json_type = models.ForeignKey(JsonObj, verbose_name="treatment type", limit_choices_to={'json_type': "treatment_type"}, on_delete=models.CASCADE, help_text="The method used to make the treatment")
    json_fields = JSONField(null=True, blank=True)

    def __str__(self):
        return self.name
 
class Experiment(UserLog): 
    project = models.ForeignKey(Project,related_name='exp_project', on_delete=models.CASCADE,)
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the experiment")
    biosample = models.ForeignKey(Biosample,related_name='exp_biosample', null=False, on_delete=models.CASCADE, help_text="Related biosample")
    bio_rep_no = models.IntegerField(null=False, default=1, help_text="Biological replicate number")
    tec_rep_no = models.IntegerField(null=False, default=1, help_text="Technical replicate number")
    modification = models.ForeignKey(Modification,related_name='exp_modification', null=True, blank=True, on_delete=models.SET_NULL, help_text="Expression or targeting vectors stably transfected to generate Crispr'ed or other genomic modification")
    treatment = models.ForeignKey(Treatment,related_name='exp_treatment', null=True, blank=True, on_delete=models.SET_NULL, help_text="Chemical/RNAi treatment")
    protocol = models.ForeignKey(Protocol,related_name='exp_protocol', null=True, blank=True, on_delete=models.SET_NULL, help_text="Reference protocol document") 
    json_type = models.ForeignKey(JsonObj, verbose_name="experiment type", limit_choices_to={'json_type': "experiment_type"}, on_delete=models.CASCADE, help_text="The category that best describes the experiment")
    json_fields = JSONField(null=True, blank=True) 
    
    def __str__(self):
        return self.name
    
     
    



