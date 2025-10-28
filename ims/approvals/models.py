# models.py
from django.db import models
from django.contrib.auth.models import User

from metadata.models import Experiment, Project

class ApprovalRequest(models.Model):
  STATUS_CHOICES = [
      ('pending', 'Pending'),
      ('approved', 'Approved'),
      ('disapproved', 'Disapproved'),
  ]
  title = models.CharField(max_length=255)
  document = models.FileField(upload_to='documents/')
  status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='pending')
  created_by = models.ForeignKey(User, on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)
  approved_by = models.ForeignKey(User, null=True, blank=True, related_name='approvals', on_delete=models.SET_NULL)
  approved_at = models.DateTimeField(null=True, blank=True)
  comments = models.CharField(max_length=500, null=True, blank=True)
  project = models.ForeignKey(Project, on_delete=models.RESTRICT, related_name='approval_requests')
  experiments = models.ManyToManyField(Experiment, related_name='approval_requests')

  def __str__(self):
    return f"Request by {self.created_by.username} - Status: {self.status}"

