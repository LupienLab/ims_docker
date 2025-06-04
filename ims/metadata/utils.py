# views.py in projects app
from django.shortcuts import render, get_object_or_404
from user_profiles.utils import get_user_lab  # Import the utility function to get user's lab
from .models import Project

def get_projects_for_user(user):
    """
    Retrieve projects associated with the lab of the given user.

    Args:
        user (User): The user instance for which to retrieve projects.

    Returns:
        QuerySet: A QuerySet of projects associated with the user's lab.
    """
    # Get the user's lab using the utility function
    user_lab = get_user_lab(user)

    if user_lab is None:
        return Project.objects.none()  # Return an empty QuerySet if no lab is assigned

    # Filter projects associated with the user's lab
    return Project.objects.filter(labs=user_lab)
