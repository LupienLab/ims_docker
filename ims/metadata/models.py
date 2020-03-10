from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from metadata.validators import alphanumeric

# Create your models here.


class UserLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this object is added to the system")
    created_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_created',
                                   on_delete=models.CASCADE, help_text="Who created this object",)
    edited_at = models.DateTimeField(auto_now_add=True, help_text="When this object was edited last")
    edited_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_edited',
                                  on_delete=models.CASCADE, help_text="Who edited this object last")
    description = models.TextField(null=True, blank=True, help_text="Notes for the object")
    
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
        

class Contributing_Lab(models.Model):
    def contact_default():
        return {"email": "to1@example.com"}

    lab_name = models.CharField(max_length=100, null=False, default="", help_text="Name of the lab")
    contact_person = models.CharField(max_length=100, null=False, default="", help_text="Name of contact person")
    contact_info = JSONField("ContactInfo", default=contact_default) 

    def __str__(self):
        return self.lab_name

    class Meta:
        ordering = ['lab_name']

class Choice(models.Model):
    name = models.CharField(max_length=50, null=False, help_text="Name of the choice")
    type = models.CharField(max_length=50, null=False, help_text="Class/type of the choice")
    
    def __str__(self):
        return self.name
    

class Protocol(UserLog):
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the protocol")
    attachment = models.FileField(upload_to='uploads/', null=True, blank=True)
    type = models.ForeignKey(Choice, limit_choices_to={'type': "protocol_type"}, null=True, blank=True, on_delete=models.SET_NULL, help_text="The category that best describes the protocol or document")
    
    def __str__(self):
        return self.name

class JsonObj(models.Model):
    def fields_default():
        return {"null": ""}
    
    name = models.CharField(max_length=500, unique=True, help_text="Name of the object")
    type = models.CharField(max_length=50, null=False, help_text="Class/type of the object")
    fields = JSONField("fields", default=fields_default) 
    
    def __str__(self):
        return self.name

class Experiment(UserLog):
    project = models.ForeignKey(Project,related_name='exp_project', on_delete=models.CASCADE,)
    name = models.CharField(max_length=500, unique=True, validators=[alphanumeric], help_text="Name of the experiment")
    bio_rep_no = models.IntegerField(null=False, default=1, help_text="Biological replicate number")
    tec_rep_no = models.IntegerField(null=False, default=1, help_text="Technical replicate number")
    type = models.ForeignKey(Choice, limit_choices_to={'type': "experiment_type"}, default=1, on_delete=models.DO_NOTHING, help_text="The category that best describes the experiment")
    protocol = models.ForeignKey(Protocol,related_name='exp_protocol', null=True, blank=True, on_delete=models.SET_NULL, help_text="Reference protocol document") 
    fields = JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.name



    
