from django.http import HttpResponseForbidden
from functools import wraps
from django.shortcuts import get_object_or_404
from user_profiles.utils import get_user_lab  # Import the utility function to get user's lab

def lab_assignment_required(model, relationship_field):
  def decorator(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
      # Get the object ID from the URL or request
      object_id = kwargs.get('object_id')  # Adjust based on your URL pattern
      obj = get_object_or_404(model, id=object_id)

      # Get the user's lab using the utility function
      user_lab = get_user_lab(user)

      # Check if the user is assigned to the lab of the object
      if user_lab and user_lab in getattr(obj, relationship_field):
        return view_func(request, *args, **kwargs)
      else:
        return HttpResponseForbidden("You do not have permission to view this.")

    return _wrapped_view
  return decorator
