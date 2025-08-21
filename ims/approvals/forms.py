# forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import ApprovalRequest
from metadata.models import Project, Experiment
from metadata.utils import get_projects_for_user

class ApprovalRequestForm(forms.ModelForm):
  projects = forms.ModelChoiceField(queryset=Project.objects.none(), required=True)
  experiments = forms.ModelChoiceField(queryset=Experiment.objects.none(), required=True)
  class Meta:
    model = ApprovalRequest
    fields = ['projects', 'experiments', 'title', 'document']
    widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

  def __init__(self, *args, user=None, **kwargs):
    super(ApprovalRequestForm, self).__init__(*args, **kwargs)
    self.helper = FormHelper()
    self.helper.form_method = 'post'
    self.helper.add_input(Submit('submit', 'Submit'))
    if user is not None:
      self.fields['projects'].queryset = get_projects_for_user(user)  # Adjust according to your lab
