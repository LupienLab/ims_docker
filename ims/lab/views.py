# lab/views.py

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import Lab
from user_profiles.utils import is_supervisor, is_admin, is_admin_or_is_supervisor, get_user_lab

@login_required
@user_passes_test(is_admin_or_is_supervisor)
def supervisor_view(request):
    labs = Lab.objects.filter(supervisor=request.user)
    return render(request, 'supervisor_view.html', {'labs': labs})

@login_required
def lab_list(request):
    labs = Lab.objects.all()
    supervisor = is_supervisor(request.user)
    admin = is_admin(request.user)
    user_lab = get_user_lab(request.user)  # Use the utility function to get the user's lab
    return render(request, 'lab_list.html', {'labs': labs, 'is_supervisor': supervisor, 'is_admin': admin,'user_lab': user_lab})

