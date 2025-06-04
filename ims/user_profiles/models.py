# user_profiles/models.py

from django.db import models
from django.contrib.auth.models import User
from lab.models import Lab

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, null=True, related_name='members')

    def __str__(self):
        return self.user.username


