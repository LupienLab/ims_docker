from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from metadata.validators import alphanumeric
from django.utils.translation import gettext_lazy as _
from model_clone import CloneMixin
from email.policy import default
from django.utils.timezone import now

# Create your models here.

User.__str__ = lambda user: user.get_full_name()

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
    name = models.CharField(max_length=50, null=False, help_text="Name of the choice (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
    class_type = models.CharField(max_length=50, null=False, help_text="Class/type of the choice")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['class_type']

class ChoiceDisease(models.Model):
    name = models.CharField(max_length=50, null=False, help_text="Name of the choice (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
    class_type = models.CharField(max_length=50, null=False, help_text="Class/type of the choice")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['class_type'] 

class Contributing_Lab(models.Model):
    def contact_default():
        return ('to1@example.com')

    lab_name = models.ForeignKey(Choice, verbose_name="contributing lab", related_name='lab_name', limit_choices_to={'class_type': "lab_name"}, null=True, blank=True, on_delete=models.SET_NULL, help_text="Name of the contributing lab (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
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
 
    user_name_string = models.CharField(max_length=8, validators=[alphanumeric],  default="default" ,help_text="Max length=8 char, user defined relevant string for the project (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
    starting_date = models.DateField(help_text="When the project was started", default=now)
    disease_site =  models.ForeignKey(ChoiceDisease, default=5, limit_choices_to={'class_type': "disease_site"}, related_name='disease_site', on_delete=models.CASCADE, help_text="Type of cancer")
    tissue_type = models.ManyToManyField(Choice, default=5, related_name='tissue_type', limit_choices_to={'class_type': "tissue_type"},help_text="Tissue type of cancer")
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="User defined relevant string for the project (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
    #origin = models.ManyToManyField(ChoiceDisease, related_name='project_related', limit_choices_to={'class_type': "project_related"}, blank=True,  help_text="Name of the related body part or disease")
    contributor = models.ManyToManyField(
        User, related_name='project_contibutor', blank=True, help_text="Collaborating members for this project")
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default="Active",
                              help_text="Is project currently in progress")
     
#     name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the project (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
#     related = models.ManyToManyField(ChoiceDisease, related_name='project_related', limit_choices_to={'class_type': "project_related"}, blank=True,  help_text="Name of the related body part or disease (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
#     contributor = models.ManyToManyField(
#         User, related_name='project_contibutor', blank=True, help_text="Collaborating members for this project")
#     status = models.CharField(choices=STATUS_CHOICES, max_length=10, default="Active",
#                               help_text="Is project currently in progress")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        
        


class Protocol(UserLog):
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the protocol (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
    attachment = models.FileField(upload_to='media/', null=True, blank=True)
    class_type = models.ForeignKey(Choice, limit_choices_to={'class_type': "protocol_type"}, null=True, blank=True, on_delete=models.SET_NULL, help_text="The category that best describes the protocol or document")
    
    def __str__(self):
        return self.name

class JsonObj(models.Model): 
    def fields_default():
        return {"null": ""}
    
    name = models.CharField(max_length=500, unique=True, help_text="Name of the object (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
    json_type = models.CharField(max_length=50, null=False, help_text="Class/type of the object")
    json_fields = JSONField(default=fields_default) 
    
    def __str__(self):
        return self.name

class Modification(UserLog):
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the modification (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
    modification_type = models.ForeignKey(Choice, limit_choices_to={'class_type': "modification_type"}, related_name='modification_type', null=True, blank=True, on_delete=models.SET_NULL, help_text="The method used to make the genomic modification")
    genomic_change = models.ForeignKey(Choice, limit_choices_to={'class_type': "genomic_change"}, related_name='genomic_change', null=True, blank=True, on_delete=models.SET_NULL, help_text="The method used to make the genomic modification")
    guide_rnas = models.CharField(max_length=100, null=True, blank=True, help_text="The guide RNA sequences used in Crispr targetting")
    attachment = models.FileField(upload_to='media/', null=True, blank=True)
    
    def __str__(self):
        return self.name
    
class Treatment(UserLog): 
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the treatment (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
    json_type = models.ForeignKey(JsonObj, verbose_name="treatment type", limit_choices_to={'json_type': "treatment_type"}, on_delete=models.CASCADE, help_text="The method used to make the treatment")
    json_fields = JSONField(null=True, blank=True)
    attachment = models.FileField(upload_to='media/', null=True, blank=True)

    def __str__(self):
        return self.name

class Biosource(UserLog):
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the Biosource (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
    disease=models.CharField(max_length=500, null=True, blank=True, help_text="Name of the disease")
    source_organism = models.ForeignKey(Choice, related_name='source_organism', limit_choices_to={'class_type': "source_organism"}, null=True, blank=True, on_delete=models.SET_NULL, help_text="Source of the biomaterial/biosource")
    json_type = models.ForeignKey(JsonObj, verbose_name="biomaterial type" ,related_name='biomaterial_type', limit_choices_to={'json_type': "biomaterial_type"}, on_delete=models.CASCADE, help_text="The categorization of the biomaterial/biosource")
    json_fields = JSONField(null=True, blank=True)
    
    def __str__(self): 
        return self.name
    

    
class Biosample(UserLog, Contributing_Lab,CloneMixin):
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the biosample, e.g. HeLa-p14-11302019 (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
    biosource = models.ForeignKey(Biosource,related_name='sample_source', null=False, on_delete=models.CASCADE, help_text="Related biosource")
    sample_id = models.CharField(max_length=100, null=False, default="", help_text="Sample id / id given on sequencing form e.g. 080144A")
    #sample_type  = models.ForeignKey(Choice, related_name='sample_type', default="44",limit_choices_to={'class_type': "sample_type"}, on_delete=models.CASCADE, help_text="Sample Type")
    modification = models.ForeignKey(Modification,related_name='exp_modification', null=True, blank=True, on_delete=models.SET_NULL, help_text="Expression or targeting vectors stably transfected to generate Crispr'ed or other genomic modification")
    treatment = models.ForeignKey(Treatment,related_name='exp_treatment', null=True, blank=True, on_delete=models.SET_NULL, help_text="Chemical/RNAi treatment")
    collection_date = models.DateField(null=True, blank=True, help_text="Collection date for this biosample")
    collection_method = models.CharField(max_length=100, null=True, blank=True, help_text="Method of collection for this biosample")
    json_type = models.ForeignKey(JsonObj, verbose_name="Culture details" ,related_name='culture_details', limit_choices_to={'json_type': "culture_details"}, on_delete=models.CASCADE, help_text="Culture details of sample")
    json_fields = JSONField(null=True, blank=True) 
    
    def __str__(self):
        return self.name
    
    
#     _clone_many_to_many_fields = ['']


 
class Experiment(UserLog,CloneMixin): 
    project = models.ForeignKey(Project,related_name='exp_project', on_delete=models.CASCADE,)
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the experiment, e.g. K562-p11-DpnII-02202020-R1-T1 (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
    uid = models.CharField(max_length=10, default="G7HXXY", help_text="Label for sequencing form")
    biosample = models.ForeignKey(Biosample,related_name='exp_biosample', null=False, on_delete=models.CASCADE, help_text="Related biosample")
    biosample_quantity = models.IntegerField(null=False, help_text="The amount of starting Biological sample going into the experiment")
    biosample_quantity_units = models.ForeignKey(Choice, related_name='biosample_quantity_units', limit_choices_to={'class_type': "quantity_units"}, null=True, blank=True, on_delete=models.SET_NULL, help_text="The units that go along with the biological sample quantity")
    concentration_of_sample=models.CharField(max_length=100, null=True, blank=True, help_text="For DNA and Libraries, concentration of sample (ng/ul)")
    volume_of_sample=models.CharField(max_length=100, null=True, blank=True, help_text="For Fresh cells, DNA and Libraries, Sample volume (uL or pellet)")
    bio_rep_no = models.IntegerField(null=False, default=1, help_text="Biological replicate number")
    tec_rep_no = models.IntegerField(null=False, default=1, help_text="Technical replicate number")
    protocol = models.ForeignKey(Protocol,related_name='exp_protocol', null=True, blank=True, on_delete=models.SET_NULL, help_text="Reference protocol document") 
    json_type = models.ForeignKey(JsonObj, verbose_name="experiment type", limit_choices_to={'json_type': "experiment_type"}, on_delete=models.CASCADE, help_text="The category that best describes the experiment")
    json_fields = JSONField(null=True, blank=True) 
    
    def __str__(self):
        return self.name
    
    
#     _clone_many_to_many_fields = [''] 

  
    
class SequencingRun(UserLog):
    name = models.CharField(max_length=300, null=False, default="", validators=[alphanumeric],help_text="Name of the sequencing run (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
    project = models.ForeignKey(Project, related_name='run_project', on_delete=models.CASCADE,)
    experiment = models.ManyToManyField(Experiment, related_name='run_experiment')
    sequencing_center = models.ForeignKey(Choice, related_name='run_sequencing_center', limit_choices_to={'class_type': "sequencing_center"}, null=True, blank=True, on_delete=models.SET_NULL, help_text="Where the sequencing has been done")
    sequencing_instrument = models.ForeignKey(Choice, related_name='run_sequencing_instrument', limit_choices_to={'class_type': "sequencing_instrument"}, null=True, blank=True, on_delete=models.SET_NULL, help_text="Instrument used for sequencing")
    submission_date = models.DateField(help_text="Submission date for sample")
    #retrieval_date = models.DateField(null=True, blank=True, help_text="Collection date for sample")
#     submitted = models.BooleanField(default=False,help_text="Is sample submitted for sequencing") 
#     approved = models.BooleanField(default=False,help_text="Is sample approved for sequencing")
    
    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = ('project', 'name',)
     
class SeqencingFile(UserLog):
    PAIR_CHOICES = (
        ('', ''),
        ('1', '1'),
        ('2', '2'),
        ('index', 'index'),
    )
    name = models.CharField(max_length=300, null=False, default="", validators=[alphanumeric],help_text="Name of the sequencing file (allowed characters [0-9a-zA-Z-._], no spaces allowed)")
    project = models.ForeignKey(Project, related_name='file_Project', on_delete=models.CASCADE,)
    paired_end = models.CharField(
        max_length=8,
        choices=PAIR_CHOICES,
        default='',
        null=True,
        blank=True,
        help_text="Which pair the file belongs to (if paired end library)"
    )    
    read_length = models.IntegerField(null=True, blank=True, help_text="Length of sequencing reads in base pairs for fastq files")
    cluster_path = models.CharField(max_length=1000, null=False, default="", help_text="Path on the cluster including the file name and extension e.g /mnt/work1/users/lupiengroup/Projects/folder/test.fastq.gz")
    md5sum = models.CharField(max_length=32, null=True, blank=True, default="",help_text="md5sum")
    related_files = models.ForeignKey('SeqencingFile', null=True, blank=True,on_delete=models.SET_NULL, help_text="Related paired file reference")
    run = models.ForeignKey(SequencingRun, related_name='file_run', on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, related_name='file_exp', on_delete=models.CASCADE)
    file_format = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True, default="", related_name='fileChoice', limit_choices_to={'class_type': "file_format"}, help_text="Type of file format")
    
    def __str__(self):  
        return self.name
    
    class Meta:
        unique_together = ('project', 'name',)

class ExperimentTag(UserLog):
    name = models.CharField(max_length=300, null=False, default="", validators=[alphanumeric],help_text="Name of the tags (Unique throughout system. Allowed characters [0-9a-zA-Z-._], no spaces allowed)")
    project = models.ForeignKey(Project, related_name='tag_project', on_delete=models.CASCADE,)
    experiment = models.ManyToManyField(Experiment, related_name='tag_experiment')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name',)





    