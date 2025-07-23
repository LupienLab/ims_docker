from django.shortcuts import redirect
from django.urls import reverse

class ApprovalsAccessMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
      # Check if the user belongs to the 'sequence_core' group
      if request.user.groups.filter(name='sequence_core').exists():

        allowed_paths = [
          reverse('approval_list'), # approval_list view
          reverse('access_denied'), # access denied page to prevent redirect loop
        ]
        # If the requested path is not the allowed path, redirect to access denied
        if request.path not in allowed_paths:
          return redirect('access_denied')  # Redirect to an access denied page

    response = self.get_response(request)
    return response
