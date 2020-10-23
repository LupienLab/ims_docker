from django.contrib import admin
from metadata.models import *

# Register your models here.

admin.site.register(Project)
admin.site.register(Choice)
admin.site.register(ChoiceDisease)
admin.site.register(Protocol)
admin.site.register(Experiment) 
admin.site.register(JsonObj)
admin.site.register(Biosource)
admin.site.register(Biosample)
admin.site.register(Modification)
admin.site.register(Treatment)
admin.site.register(SequencingRun)
admin.site.register(SeqencingFile)
admin.site.register(ExperimentTag)

