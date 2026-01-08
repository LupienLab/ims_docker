# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from .forms import ApprovalRequestForm
from .models import ApprovalRequest, CompletionFile
from user_profiles.models import UserProfile
from user_profiles.utils import (
    get_user_lab,
    is_admin,
    is_admin_or_is_supervisor,
    is_sequence_core,
    is_supervisor,
)
from metadata.models import Experiment
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
def create_approval_request(request):
    if request.method == "POST":
        form = ApprovalRequestForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            approval_request = form.save(commit=False)
            approval_request.created_by = request.user
            # Set the project FK
            selected_project = form.cleaned_data.get("projects")
            approval_request.project = selected_project
            approval_request.save()

            # Set the many-to-many experiments
            selected_experiments = form.cleaned_data.get("experiments")
            approval_request.experiments.set(selected_experiments)

            return redirect("approval_list")
    else:
        form = ApprovalRequestForm(user=request.user)
    return render(request, "create_request.html", {"form": form})


@login_required
def approval_list(request):
    # Assuming the user is logged in
    user = request.user

    # Attempt to get the UserProfile
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # If the user does not have a profile, show a message
        return render(
            request,
            "approval_list.html",
            {
                "approvals": [],
                "is_supervisor": False,
                "is_admin": False,
                "profile_exists": False,
                "is_sequence_core": False,
            },
        )

    # Check if the user is a supervisor
    supervisor_status = is_supervisor(user)

    # Check if the user is admin
    admin_status = is_admin(user)

    # Check if the user is the sequence core user
    sequence_core_status = is_sequence_core(user)

    # Get the lab associated with the user's profile
    lab = user_profile.lab

    if admin_status or sequence_core_status:
        # If the user is an admin or sequence core, show all requests
        approvals = (
            ApprovalRequest.objects.all()
            .select_related("project", "completed_by")
            .prefetch_related("experiments", "completion_files")
            .order_by("status")
        )
    elif request.user == lab.supervisor:
        # If the user is a supervisor, show all requests for their lab
        approvals = (
            ApprovalRequest.objects.filter(created_by__userprofile__lab=lab)
            .select_related("project", "completed_by")
            .prefetch_related("experiments", "completion_files")
            .order_by("status")
        )
    else:
        # If the user is not a supervisor, show only their own requests
        approvals = (
            ApprovalRequest.objects.filter(created_by=user)
            .select_related("project", "completed_by")
            .prefetch_related("experiments", "completion_files")
            .order_by("status")
        )

    # Serialize ALL approvals for both grids
    all_serialized_approvals = []
    for approval in approvals:
        # Experiments HTML
        experiments_html = []
        for experiment in approval.experiments.all():
            experiments_html.append(
                f'<a href="{reverse("detailExperiment", args=[experiment.pk])}">{experiment.name}</a>'
            )
        experiments_html = ", ".join(experiments_html) if experiments_html else "None"

        labs = []
        for lab in approval.project.labs.all():
            labs.append(lab.name)
        labs = ", ".join(labs) if labs else "None"

        completion_files_count = approval.completion_files.count()
        completion_files_list = []
        if completion_files_count > 0:
            for comp_file in approval.completion_files.all():  # Show first 3
                completion_files_list.append({
                    'file': comp_file.file.url,
                    'filename': comp_file.file.name.split('/')[-1],
                    'uploaded_by': comp_file.uploaded_by.get_full_name() if comp_file.uploaded_by else 'N/A',
                    'uploaded_at': comp_file.uploaded_at.strftime("%Y-%m-%d %H:%M") if comp_file.uploaded_at else '',
                    'comment': comp_file.comment or ''
                })
        all_serialized_approvals.append(
            {
                "id": approval.pk,
                "title": str(approval.title),
                "created_by_full_name": getattr(
                    approval.created_by, "get_full_name", lambda: "N/A"
                )(),
                "lab": labs,
                "project_name": approval.project.name if approval.project else "N/A",
                "project_url": reverse("detailProject", args=[approval.project.pk])
                if approval.project
                else "",
                "experiments_html": experiments_html,
                "document_url": approval.document.url
                if hasattr(approval.document, "url") and approval.document
                else "",
                "created_at": approval.created_at.strftime("%Y-%m-%d %H:%M")
                if approval.created_at
                else "",
                "status": approval.status,
                "status_display": approval.get_status_display(),
                "approved_by_full_name": getattr(
                    approval.approved_by, "get_full_name", lambda: "N/A"
                )()
                if approval.approved_by
                else "N/A",
                "approved_at": approval.approved_at.strftime("%Y-%m-%d %H:%M")
                if approval.approved_by and approval.approved_at
                else "N/A",
                "comments": approval.comments or "",
                "is_action_allowed": (supervisor_status or admin_status)
                and approval.status == "pending",
                "is_complete_action_allowed": (sequence_core_status or admin_status)
                and approval.status == "approved",
                "approve_url": reverse("approve_request", args=[approval.pk])
                if approval.pk
                else "",
                "completion_files_count": completion_files_count,
                "completion_files": completion_files_list,
                "completed_by_full_name": getattr(
                    approval.completed_by, "get_full_name", lambda: "N/A"
                )() if hasattr(approval, 'completed_by') and approval.completed_by else "N/A",
                "completed_at": approval.completed_at.strftime("%Y-%m-%d %H:%M")
                if hasattr(approval, 'completed_at') and approval.completed_at else "N/A",
            }
        )

    context = {
        "all_approvals": all_serialized_approvals,  # Single source for both grids
        "is_supervisor": supervisor_status,
        "is_admin": admin_status,
        "profile_exists": True,
        "is_sequence_core": sequence_core_status,
    }

    return render(request, "approval_list.html", context)


@login_required
@user_passes_test(is_admin_or_is_supervisor)  # Only allow supervisor to approve
def approve_request(request, pk):
    approval_request = get_object_or_404(ApprovalRequest, pk=pk)
    approval_request.status = "approved"
    approval_request.approved_by = request.user  # Set the supervisor who approved
    approval_request.approved_at = timezone.now()  # Set the approval timestamp
    approval_request.save()
    return redirect("approval_list")


@login_required
@user_passes_test(is_admin_or_is_supervisor)  # Only allow supervisor to approve
def disapprove_request(request, pk):
    approval_request = get_object_or_404(ApprovalRequest, pk=pk)
    if request.method == "POST":
        # Handle the comment submission
        comment = request.POST.get("comment")
        approval_request.comments = comment
        approval_request.status = "disapproved"
        approval_request.approved_by = request.user  # Set the supervisor who approved
        approval_request.approved_at = timezone.now()  # Set the approval timestamp
        approval_request.save()

    return redirect("approval_list")


@login_required
@user_passes_test(lambda u: is_admin(u) or is_sequence_core(u))
def complete_request(request, pk):
    approval_request = get_object_or_404(ApprovalRequest, pk=pk)
    if approval_request.status != 'approved':
        return JsonResponse({'error': 'Can only complete approved requests'}, status=400)

    sequence_core = is_sequence_core(request.user)
    admin_status = is_admin(request.user)
    if not sequence_core and not admin_status:
        return render(request, "access_denied.html")

    files = request.FILES.getlist('files')
    comment = request.POST.get('completion_comment', '')

    # Create completion files
    for file in files:
        CompletionFile.objects.create(
            approval_request=approval_request,
            file=file,
            uploaded_by=request.user,
            comment=comment
        )
    approval_request.status = "completed"
    approval_request.completed_by = request.user
    approval_request.completed_at = timezone.now()
    approval_request.save()

    return redirect("approval_list")


def access_denied(request):
    return render(request, "access_denied.html")


def get_experiments(request, project_id):
    experiments = Experiment.objects.filter(project_id=project_id)
    # Serialize the experiments into a list of dictionaries
    experiments_data = [
        {"id": experiment.id, "name": experiment.name} for experiment in experiments
    ]
    return JsonResponse({"experiments": experiments_data})
