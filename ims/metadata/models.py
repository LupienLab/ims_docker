from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from metadata.validators import alphanumeric

# Create your models here.

class UserLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this object is added to the system")
    created_by = models.ForeignKey(User, related_name="project_created", on_delete=models.CASCADE, help_text="Who created this object",)
    edited_at = models.DateTimeField(auto_now_add=True, help_text="When this object was edited last")
    edited_by = models.ForeignKey(User, related_name="project_edited" , on_delete=models.CASCADE, help_text="Who edited this object last")


class Project(UserLog):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Archived', 'Archived'),
    )
    name = models.CharField(max_length=500, help_text="Name of the project", unique=True, validators=[alphanumeric])
    contributor = models.ManyToManyField(
        User, help_text="Collaborating members for this project", related_name='project_contibutor', blank=True)
    status=models.CharField(choices=STATUS_CHOICES, max_length=10, default= "Active", help_text="Is project currently in progress")
    description = models.TextField(null=True, blank=True, help_text="Notes for the project")
    

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']

# class Contributing_Lab(models.Model):
#     lab_name = models.CharField(max_length=100, null=False, default="", help_text="Name of the lab")
#     contact_person=models.CharField(max_length=100, null=False, default="", help_text="Name of contact person")
#     contact_info = JSONField ("ContactInfo", default=contact_default)
#
#     def contact_default():
#         return {"email": "to1@example.com"}
#
#     def __str__(self):
#         return self.lab_name
#     class Meta:
#         ordering = ['lab_name']
