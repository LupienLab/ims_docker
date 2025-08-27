# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from .forms import ApprovalRequestForm
from .models import ApprovalRequest
from user_profiles.models import UserProfile
from user_profiles.utils import is_admin_or_is_supervisor
from metadata.models import Experiment
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
def create_approval_request(request):
  if request.method == 'POST':
    form = ApprovalRequestForm(request.POST, request.FILES, user=request.user)
    if form.is_valid():
      approval_request = form.save(commit=False)
      approval_request.created_by = request.user
      # Set the project FK
      selected_project = form.cleaned_data.get('projects')
      approval_request.project = selected_project
      approval_request.save()

      # Set the many-to-many experiments
      selected_experiments = form.cleaned_data.get('experiments')
      approval_request.experiments.set(selected_experiments)

      return redirect('approval_list')
  else:
    form = ApprovalRequestForm(user=request.user)
  return render(request, 'create_request.html', {'form': form})

@login_required
def approval_list(request):
  # Assuming the user is logged in
  user = request.user

  # Attempt to get the UserProfile
  try:
    user_profile = UserProfile.objects.get(user=user)
  except UserProfile.DoesNotExist:
    # If the user does not have a profile, show a message
    return render(request, 'approval_list.html', {'approvals': [], 'is_supervisor': False, 'profile_exists': False, 'is_sequence_core': False})

  # Check if the user is a supervisor
  supervisor_status = is_admin_or_is_supervisor(user)

  # Check if the user is the sequence core user
  is_sequence_core = user.groups.filter(name='sequence_core').exists()

  # Get the lab associated with the user's profile
  lab = user_profile.lab

  if request.user == lab.supervisor:
    # If the user is a supervisor, show all requests for their lab
    approvals = ApprovalRequest.objects.filter(created_by__userprofile__lab=lab).select_related('project').prefetch_related('experiments').order_by('status')
  else:
    # If the user is not a supervisor, show only their own requests
    approvals = ApprovalRequest.objects.filter(created_by=user).select_related('project').prefetch_related('experiments').order_by('status')

  return render(request, 'approval_list.html', {'approvals': approvals, 'is_supervisor': supervisor_status, 'profile_exists': True, 'is_sequence_core': is_sequence_core})

@login_required
@user_passes_test(is_admin_or_is_supervisor) # Only allow supervisor to approve
def approve_request(request, pk):
  approval_request = get_object_or_404(ApprovalRequest, pk=pk)
  approval_request.status = 'approved'
  approval_request.approved_by = request.user  # Set the supervisor who approved
  approval_request.approved_at = timezone.now()  # Set the approval timestamp
  approval_request.save()
  return redirect('approval_list')


@login_required
@user_passes_test(is_admin_or_is_supervisor) # Only allow supervisor to approve
def disapprove_request(request, pk):
  approval_request = get_object_or_404(ApprovalRequest, pk=pk)
  if request.method == 'POST':
    # Handle the comment submission
    comment = request.POST.get('comment')
    approval_request.comments = comment
    approval_request.status = 'disapproved'
    approval_request.approved_by = request.user  # Set the supervisor who approved
    approval_request.approved_at = timezone.now()  # Set the approval timestamp
    approval_request.save()

  return redirect('approval_list')

def access_denied(request):
  return render(request, 'access_denied.html')

def get_experiments(request, project_id):
  experiments = Experiment.objects.filter(project_id=project_id)
  # Serialize the experiments into a list of dictionaries
  experiments_data = [{'id': experiment.id, 'name': experiment.name} for experiment in experiments]
  return JsonResponse({'experiments': experiments_data})
