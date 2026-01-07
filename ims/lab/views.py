# lab/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Lab
from user_profiles.utils import is_sequence_core, is_supervisor, is_admin, get_user_lab


@login_required
def lab_list(request):
    labs = Lab.objects.all()
    supervisor = is_supervisor(request.user)
    admin = is_admin(request.user)
    user_lab = get_user_lab(request.user)  # Use the utility function to get the user's lab
    sequence_core = is_sequence_core(request.user)
    return render(request, 'lab_list.html', {'labs': labs, 'is_supervisor': supervisor, 'is_admin': admin, 'is_sequence_core': sequence_core, 'user_lab': user_lab})

