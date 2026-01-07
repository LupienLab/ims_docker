from django.contrib import admin

from .models import ApprovalRequest, CompletionFile

# Register your models here.
admin.site.register(ApprovalRequest)
admin.site.register(CompletionFile)
