from django.db import models
from django.contrib.auth.models import User

class Lab(models.Model):
    name = models.CharField(max_length=100, verbose_name="Full Lab Name")
    website = models.URLField(max_length=200, blank=True, null=True, verbose_name="Lab URL")
    supervisor = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='supervised_lab')

    def __str__(self):
      return self.name
