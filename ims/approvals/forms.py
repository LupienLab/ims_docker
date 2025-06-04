# forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import ApprovalRequest

class ApprovalRequestForm(forms.ModelForm):
  class Meta:
    model = ApprovalRequest
    fields = ['title', 'document']
    widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

  def __init__(self, *args, **kwargs):
    super(ApprovalRequestForm, self).__init__(*args, **kwargs)
    self.helper = FormHelper()
    self.helper.form_method = 'post'
    self.helper.add_input(Submit('submit', 'Submit'))
