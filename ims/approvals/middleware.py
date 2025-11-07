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
        approval_list_url = reverse('approval_list')
        access_denied_url = reverse('access_denied')
        login_url = reverse('login')
        logout_url = reverse('logout')

        # Redirect from login to approval_list if in sequence_core group
        if request.path == login_url:
          return redirect(approval_list_url)

        allowed_paths = [
          approval_list_url,
          access_denied_url,
          login_url,
          logout_url,
        ]
        # If the requested path is not the allowed path, redirect to access denied
        if request.path not in allowed_paths:
          return redirect(access_denied_url)  # Redirect to an access denied page

    response = self.get_response(request)
    return response
