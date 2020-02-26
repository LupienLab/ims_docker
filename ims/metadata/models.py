from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from metadata.validators import alphanumeric

# Create your models here.


class Project(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Archived', 'Archived'),
    )
    name = models.CharField(max_length=500, help_text="Name of the project", unique=True, validators=[alphanumeric])
    owner = models.ForeignKey(User, help_text="Name the owner of this project",
                              related_name='ownerProject', on_delete=models.CASCADE)
    contributor = models.ManyToManyField(
        User, help_text="Collaborating members for this project", related_name='contributorProject', blank=True)
    models.CharField(choices=STATUS_CHOICES, help_text="Is project currently in progress")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this project is added to the system")
    decription = models.TextField(null=True, blank=True, help_text="Notes for the project")

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
